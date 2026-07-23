from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path

import pytest

from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtLocalDailyExportProfile,
)
from apps.fcp_0088_a_share_guojin_qmt_registered_local_dual_export_offline_sdk_compatibility_evidence_app_1 import (
    OfflineSdkAbiObservation,
    QmtRegisteredDualExportSpec,
    build_reference_evidence,
    render_compatibility_evidence_json,
    run_registered_local_compatibility,
)


HEADER = b"timetag,open,high,low,close,volumn,amount\n"


def _files(tmp_path: Path) -> tuple[Path, Path]:
    raw = tmp_path / "raw.txt"
    front = tmp_path / "front.txt"
    raw.write_bytes(
        HEADER
        + b"20260717,11.00,12.00,10.00,11.50,100,1000.00\n"
        + b"20260720,12.00,13.00,11.00,12.50,120,1200.00\n"
        + b"20260721,13.00,14.00,12.00,13.50,130,1300.00\n"
    )
    front.write_bytes(
        HEADER
        + b"20260717,10.00,11.00,9.00,10.50,100,1000.00\n"
        + b"20260720,11.00,12.00,10.00,11.50,120,1200.00\n"
        + b"20260721,12.00,13.00,11.00,12.50,130,1300.00\n"
    )
    return raw, front


def _profile() -> QmtLocalDailyExportProfile:
    return QmtLocalDailyExportProfile(
        profile_id="qmt-sh-600028-offline-compatibility-v1",
        source_id="guojin-qmt-local-export",
        instrument_id="600028.XSHG",
        requested_start_date="2026-07-17",
        requested_end_date="2026-07-21",
    )


def _sdk() -> OfflineSdkAbiObservation:
    return OfflineSdkAbiObservation(
        observation_id="qmt-offline-sdk-test-v1",
        observed_at_utc="2026-07-22T23:38:00Z",
        python_version="3.11.9",
        architecture_bits=64,
        native_module_name="xtpythonclient.cp311-win_amd64.pyd",
        native_module_sha256="5" * 64,
        native_module_byte_length=1147904,
        native_loaded=True,
        rpc_client_present=True,
    )


def _spec(raw: Path, front: Path) -> QmtRegisteredDualExportSpec:
    rb = raw.read_bytes()
    fb = front.read_bytes()
    return QmtRegisteredDualExportSpec(
        raw_path=raw,
        raw_artifact_id="qmt-raw-test-v1",
        raw_artifact_sha256=hashlib.sha256(rb).hexdigest(),
        raw_byte_length=len(rb),
        front_path=front,
        front_artifact_id="qmt-front-test-v1",
        front_artifact_sha256=hashlib.sha256(fb).hexdigest(),
        front_byte_length=len(fb),
    )


def _evidence(tmp_path: Path):
    raw, front = _files(tmp_path)
    return run_registered_local_compatibility(
        _spec(raw, front),
        _profile(),
        _sdk(),
        evidence_id="qmt-offline-compatibility-test-v1",
        observed_at_utc="2026-07-22T23:40:00Z",
    )


def test_d1_evidence_is_immutable_and_non_authorizing(tmp_path: Path):
    evidence = _evidence(tmp_path)
    assert evidence.entitlement_proven is False
    assert evidence.registered_evidence_promotion_allowed is False
    assert evidence.realtime_activation_allowed is False
    assert evidence.factor_calculation_allowed is False
    assert evidence.account_access_allowed is False
    assert evidence.order_allowed is False
    assert evidence.execution_allowed is False
    with pytest.raises(FrozenInstanceError):
        evidence.status = "UNSAFE"  # type: ignore[misc]


def test_d2_runner_delegates_and_keeps_rows_paths_and_values_out(tmp_path: Path):
    evidence = _evidence(tmp_path)
    rendered = render_compatibility_evidence_json(evidence)
    assert evidence.coverage_evidence.observations[0].row_count == 3
    assert str(tmp_path) not in rendered
    assert '"open"' not in rendered
    assert "11.50" not in rendered
    rendered.encode("ascii")


def test_d3_dual_export_lineage_is_exact(tmp_path: Path):
    evidence = _evidence(tmp_path)
    observation = evidence.coverage_evidence.observations[0]
    assert evidence.adjustment_reference.raw_artifact_sha256 == (
        observation.source_artifact_sha256
    )
    assert evidence.adjustment_reference.profile_hash == (
        evidence.coverage_evidence.profile_hash
    )
    assert evidence.adjustment_reference.row_count == observation.row_count


def test_d4_sdk_observation_is_offline_only():
    sdk = _sdk()
    assert sdk.native_loaded is True
    assert sdk.rpc_client_present is True
    assert sdk.connection_attempted is False
    assert sdk.network_used is False
    assert sdk.credentials_used is False
    with pytest.raises(ValueError, match="cannot connect"):
        replace(sdk, connection_attempted=True)


@pytest.mark.parametrize(
    "field,value",
    (
        ("python_version", "3.13.7"),
        ("architecture_bits", 32),
        ("native_module_name", "xtpythonclient.cp313-win_amd64.pyd"),
        ("native_loaded", False),
        ("rpc_client_present", False),
    ),
)
def test_d4_unsupported_sdk_observation_fails_closed(field: str, value: object):
    with pytest.raises(ValueError):
        replace(_sdk(), **{field: value})


def test_d5_registered_hash_mismatch_is_rejected(tmp_path: Path):
    raw, front = _files(tmp_path)
    spec = replace(_spec(raw, front), raw_artifact_sha256="0" * 64)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        run_registered_local_compatibility(
            spec,
            _profile(),
            _sdk(),
            evidence_id="qmt-offline-compatibility-test-v1",
            observed_at_utc="2026-07-22T23:40:00Z",
        )


def test_d5_front_volume_change_is_rejected(tmp_path: Path):
    raw, front = _files(tmp_path)
    front.write_bytes(front.read_bytes().replace(b",100,1000.00", b",101,1000.00"))
    with pytest.raises(ValueError, match="volume or amount"):
        run_registered_local_compatibility(
            _spec(raw, front),
            _profile(),
            _sdk(),
            evidence_id="qmt-offline-compatibility-test-v1",
            observed_at_utc="2026-07-22T23:40:00Z",
        )


def test_d6_reference_and_output_are_deterministic():
    first = build_reference_evidence()
    second = build_reference_evidence()
    rendered = render_compatibility_evidence_json(first)
    assert first.evidence_hash == second.evidence_hash
    assert rendered == render_compatibility_evidence_json(second)
    assert json.dumps(
        json.loads(rendered), ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ) + "\n" == rendered
