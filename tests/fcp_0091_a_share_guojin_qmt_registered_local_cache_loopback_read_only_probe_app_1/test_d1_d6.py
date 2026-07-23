from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.contracts import (
    build_snapshot,
)
from apps.fcp_0091_a_share_guojin_qmt_registered_local_cache_loopback_read_only_probe_app_1 import runner, runtime
from apps.fcp_0091_a_share_guojin_qmt_registered_local_cache_loopback_read_only_probe_app_1.contracts import (
    DEFAULT_REGISTRATION,
    build_probe_evidence,
    render_probe_evidence_json,
)


OBSERVED_AT = datetime(2026, 7, 23, 1, 30, tzinfo=timezone.utc)


class ShapeOnlyFrame:
    shape = (1, 1)
    columns = ("time",)

    @property
    def values(self):
        raise AssertionError("market values must not be inspected")


def _terminal_observed():
    return build_snapshot(["XtMiniQmt.exe"], OBSERVED_AT)


def _terminal_not_observed():
    return build_snapshot([], OBSERVED_AT)


def test_d1_registration_is_exact_and_deterministic():
    assert DEFAULT_REGISTRATION.payload() == {
        "artifact_id": "guojin-qmt-local-cache-loopback-probe-v1",
        "count": 1,
        "dividend_type": "none",
        "end_date": "20260721",
        "fields": ["time"],
        "fill_data": False,
        "function_identity": "xtquant.xtdata.get_local_data",
        "market": "SSE",
        "native_module_sha256": "bfefebaa08f25666c86f73e714c100f4fbdcd308332453ed16bdd619d8a0d847",
        "period": "1d",
        "server_retrieval_allowed": False,
        "start_date": "20260721",
        "symbol": "600000.SH",
        "xtdata_source_sha256": "52bc303c97b5deb207888821a27c0af4d268f81dc252dfdffca964ba0568ae3e",
    }
    assert DEFAULT_REGISTRATION.contract_sha256 == (
        "da5b77a26f14446303ffd62b5b75a94230837a99afeff1c4e0c49ecab4bdb6d4"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("artifact_id", "other-probe"),
        ("symbol", "000001.SZ"),
        ("fields", ("time", "close")),
        ("count", 2),
        ("fill_data", True),
        ("server_retrieval_allowed", True),
        ("native_module_sha256", "0" * 64),
        ("xtdata_source_sha256", "0" * 64),
    ),
)
def test_d1_rejects_any_registration_expansion(field, value):
    with pytest.raises(ValueError, match="closed request"):
        replace(DEFAULT_REGISTRATION, **{field: value})


def test_d2_terminal_gate_emits_not_run_without_calling_probe():
    calls = 0

    def probe():
        nonlocal calls
        calls += 1
        raise AssertionError("probe must remain gated")

    evidence = build_probe_evidence(_terminal_not_observed(), probe)
    assert calls == 0
    assert evidence.call_state == "NOT_RUN"
    assert evidence.call_attempted is False
    assert evidence.call_count == 0
    assert "QMT_TERMINAL_NOT_OBSERVED" in evidence.blockers


def test_d3_observed_terminal_invokes_exactly_once_and_retains_shape_only():
    calls = 0

    def probe():
        nonlocal calls
        calls += 1
        return {"600000.SH": ShapeOnlyFrame()}

    evidence = build_probe_evidence(_terminal_observed(), probe, elapsed_ms=7)
    assert calls == 1
    assert evidence.call_state == "CALL_SUCCEEDED_WITH_ROWS"
    assert evidence.call_count == 1
    assert evidence.row_count == 1
    assert evidence.schema_state == "EXACT_TIME_ONLY"
    assert evidence.timing_class == "LT_1S"


def test_d4_empty_mapping_is_a_bounded_success():
    evidence = build_probe_evidence(
        _terminal_observed(),
        lambda: {},
        elapsed_ms=1001,
    )
    assert evidence.call_state == "CALL_SUCCEEDED_EMPTY"
    assert evidence.row_count == 0
    assert evidence.schema_state == "EMPTY_MAPPING"
    assert evidence.timing_class == "LT_5S"


@pytest.mark.parametrize(
    "result",
    (
        None,
        {"000001.SZ": ShapeOnlyFrame()},
        {"600000.SH": type("Wide", (), {"shape": (1, 2), "columns": ("time", "close")})()},
        {"600000.SH": type("Long", (), {"shape": (2, 1), "columns": ("time",)})()},
    ),
)
def test_d4_invalid_result_fails_closed_without_exception_text(result):
    evidence = build_probe_evidence(
        _terminal_observed(),
        lambda: result,
        elapsed_ms=8,
    )
    rendered = render_probe_evidence_json(evidence)
    assert evidence.call_state == "CALL_FAILED"
    assert evidence.row_count == 0
    assert evidence.schema_state == "REJECTED_OR_UNAVAILABLE"
    assert "LOCAL_CACHE_PROBE_FAILED" in evidence.blockers
    assert "probe result" not in rendered


def test_d4_arbitrary_exception_text_is_never_retained():
    def probe():
        raise RuntimeError("private path account token market value 123.45")

    rendered = render_probe_evidence_json(
        build_probe_evidence(_terminal_observed(), probe, elapsed_ms=9)
    )
    for forbidden in ("private path", "account token", "123.45"):
        assert forbidden not in rendered


def test_d5_evidence_invariants_reject_tampering_and_keep_all_authorities_false():
    evidence = build_probe_evidence(
        _terminal_observed(),
        lambda: {"600000.SH": ShapeOnlyFrame()},
        elapsed_ms=7,
    )
    assert evidence.gap_104_status == "RESEARCH_REQUIRED"
    assert evidence.entitlement_authority is False
    assert evidence.provider_selection_authority is False
    assert evidence.realtime_activation_authority is False
    assert evidence.data_promotion_authority is False
    assert evidence.product_authority is False
    assert evidence.execution_authority is False
    with pytest.raises(ValueError, match="state is inconsistent"):
        replace(evidence, row_count=0)
    with pytest.raises(ValueError, match="cannot grant authority"):
        replace(evidence, execution_authority=True)


def test_d6_reference_render_is_ascii_and_hash_locked():
    evidence = build_probe_evidence(
        _terminal_observed(),
        lambda: {"600000.SH": ShapeOnlyFrame()},
        elapsed_ms=7,
    )
    rendered = render_probe_evidence_json(evidence)
    assert rendered.encode("ascii").decode("ascii") == rendered
    assert json.loads(rendered)["evidence_hash"] == evidence.evidence_hash
    assert evidence.evidence_hash == (
        "00631fa523696fc27a01d5cdb88b04473442338d8f9ccfaed94607295caae515"
    )
    assert hashlib.sha256(rendered.encode("ascii")).hexdigest() == (
        "ea7f6d7e2b816f24c7f3b6aed36291671b26c17642415d2894e764280121147a"
    )


def test_runtime_gate_does_not_touch_sdk_root(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime, "iter_local_process_image_names", lambda: ())
    monkeypatch.setattr(
        runtime,
        "_load_registered_xtdata",
        lambda path: (_ for _ in ()).throw(AssertionError("SDK must not load")),
    )
    evidence = runtime.execute_registered_probe(tmp_path / "missing-sdk")
    assert evidence.call_state == "NOT_RUN"


def test_runtime_calls_only_registered_local_data_once(monkeypatch, tmp_path):
    calls = []

    class FakeXtdata:
        def get_local_data(self, **kwargs):
            calls.append(kwargs)
            return {"600000.SH": ShapeOnlyFrame()}

    monkeypatch.setattr(
        runtime,
        "iter_local_process_image_names",
        lambda: ("XtMiniQmt.exe",),
    )
    monkeypatch.setattr(runtime, "_load_registered_xtdata", lambda path: FakeXtdata())
    evidence = runtime.execute_registered_probe(tmp_path)
    assert evidence.call_state == "CALL_SUCCEEDED_WITH_ROWS"
    assert calls == [
        {
            "field_list": ["time"],
            "stock_list": ["600000.SH"],
            "period": "1d",
            "start_time": "20260721",
            "end_time": "20260721",
            "count": 1,
            "dividend_type": "none",
            "fill_data": False,
        }
    ]


def test_runner_output_never_discloses_sdk_path(monkeypatch, capsys):
    evidence = build_probe_evidence(_terminal_not_observed(), lambda: None)
    monkeypatch.setattr(runner, "execute_registered_probe", lambda path: evidence)
    private_path = "C:/private/account/sdk"
    assert runner.main(["--sdk-root", private_path]) == 0
    output = capsys.readouterr().out
    assert private_path not in output
    assert json.loads(output)["call_state"] == "NOT_RUN"
