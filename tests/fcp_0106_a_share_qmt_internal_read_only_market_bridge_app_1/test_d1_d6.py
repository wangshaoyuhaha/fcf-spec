from __future__ import annotations

import ast
from dataclasses import replace
import json
from pathlib import Path

import pytest

from apps.fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1 import (
    DEFAULT_REGISTRATION,
    EMPTY_INGEST_STATE,
    QmtBridgeIngestState,
    build_live_operator_review_evidence,
    build_reference_event_bytes,
    build_reference_event_payload,
    build_reference_snapshot,
    ingest_registered_events,
    inspect_bridge_file,
    inspect_bridge_source,
    parse_registered_event,
    read_registered_spool,
    render_live_operator_review_evidence_json,
    render_reference_snapshot_json,
)
from apps.fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1 import (
    qmt_bridge,
)
from apps.fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1.contracts import (
    canonical_bytes,
    digest,
)
from scripts import run_fcp_0106_qmt_live_operator_review_probe as live_probe


NOW_MS = 1_775_000_001_000


def _raw(**updates: object) -> bytes:
    payload = build_reference_event_payload()
    payload.update(updates)
    payload.pop("event_hash", None)
    payload["event_hash"] = digest(payload)
    return canonical_bytes(payload)


def _write_config(tmp_path: Path, **updates: object) -> None:
    payload: dict[str, object] = {
        "bridge_root": str(tmp_path / "bridge"),
        "max_events_per_second": 5,
        "period": "tick",
        "symbols": ["600000.SH"],
    }
    payload.update(updates)
    (tmp_path / qmt_bridge.CONFIG_NAME).write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True),
        encoding="ascii",
    )


def _quote() -> dict[str, object]:
    return {
        "amount": 120000000,
        "high": 10.2,
        "lastClose": 9.95,
        "lastPrice": 10.1,
        "low": 9.9,
        "open": 10,
        "time": 1_775_000_000_000,
        "volume": 120000,
    }


def _reset_bridge() -> None:
    qmt_bridge._STATE["config"] = None
    qmt_bridge._STATE["last_emit_ns"] = {}
    qmt_bridge._STATE["sequences"] = {}
    qmt_bridge._STATE["subscriptions"] = []


class FakeContext:
    def __init__(self) -> None:
        self.universe: list[str] = []
        self.subscriptions: list[dict[str, object]] = []

    def set_universe(self, symbols: list[str]) -> None:
        self.universe = symbols

    def subscribe_quote(self, symbol: str, **kwargs: object) -> int:
        self.subscriptions.append({"symbol": symbol, **kwargs})
        return len(self.subscriptions)


def test_reference_event_and_snapshot_are_exact_and_non_authorizing():
    event = parse_registered_event(build_reference_event_bytes())
    snapshot = build_reference_snapshot()

    assert event.symbol == "600000.SH"
    assert event.sequence == 1
    assert snapshot.bridge_state == "CANDIDATE_REALTIME_OBSERVED"
    assert snapshot.operator_review_required and snapshot.read_only
    assert not any(
        (
            snapshot.market_data_authority,
            snapshot.data_promotion_authority,
            snapshot.account_authority,
            snapshot.execution_authority,
        )
    )
    assert snapshot.snapshot_hash == build_reference_snapshot().snapshot_hash
    assert (
        render_reference_snapshot_json()
        == render_reference_snapshot_json().encode("ascii").decode("ascii")
    )


def test_live_operator_review_evidence_is_value_free_and_non_authorizing():
    snapshot = build_reference_snapshot()
    evidence = build_live_operator_review_evidence(
        snapshot,
        observed_at_ms=NOW_MS,
    )

    assert evidence["candidate_status"] == "OPERATOR_REVIEW_REQUIRED"
    assert evidence["realtime_gate_passed"] is True
    assert evidence["receive_age_ms"] == 500
    assert evidence["receive_age_min_ms"] == 500
    assert evidence["receive_age_max_ms"] == 500
    assert evidence["event_age_ms"] == 1000
    assert evidence["event_age_min_ms"] == 1000
    assert evidence["event_age_max_ms"] == 1000
    assert evidence["event_to_receive_lag_min_ms"] == 500
    assert evidence["event_to_receive_lag_max_ms"] == 500
    assert evidence["sequence_first"] == 1
    assert evidence["sequence_last"] == 1
    assert evidence["sequence_gap_count"] == 0
    assert evidence["session_span_ms"] == 0
    assert evidence["operator_review_required"] is True
    assert evidence["read_only"] is True
    assert not any(
        evidence[key]
        for key in (
            "account_authority",
            "data_promotion_authority",
            "execution_authority",
            "market_data_authority",
        )
    )
    assert not {
        "amount_cny",
        "high",
        "last",
        "low",
        "open",
        "previous_close",
        "volume_native",
    }.intersection(evidence)
    assert (
        render_live_operator_review_evidence_json(
            snapshot,
            observed_at_ms=NOW_MS,
        )
        == render_live_operator_review_evidence_json(
            snapshot,
            observed_at_ms=NOW_MS,
        )
    )


def test_live_operator_review_evidence_rejects_unapproved_registration():
    registration = replace(DEFAULT_REGISTRATION, max_event_age_ms=11_000)
    snapshot = ingest_registered_events(
        (build_reference_event_bytes(),),
        now_ms=NOW_MS,
        registration=registration,
    )

    with pytest.raises(ValueError, match="not approved"):
        build_live_operator_review_evidence(
            snapshot,
            observed_at_ms=NOW_MS,
        )


def test_live_operator_review_probe_succeeds_without_market_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    spool = tmp_path / "incoming"
    spool.mkdir()
    for sequence in range(1, 6):
        received_at_ms = NOW_MS - 600 + (sequence * 100)
        event_time_ms = received_at_ms - 500
        raw = _raw(
            event_time_ms=event_time_ms,
            received_at_ms=received_at_ms,
            sequence=sequence,
        )
        name = (
            "quote-600000-SH-"
            f"{received_at_ms:013d}-{sequence:012d}.json"
        )
        (spool / name).write_bytes(raw)
    monkeypatch.setattr(live_probe.time, "time", lambda: NOW_MS / 1000)

    result = live_probe.main(
        [
            "--spool-root",
            str(spool),
            "--timeout-seconds",
            "1",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert result == 0
    assert output["accepted_event_count"] == 5
    assert output["candidate_status"] == "OPERATOR_REVIEW_REQUIRED"
    assert output["realtime_gate_passed"] is True
    assert output["sequence_first"] == 1
    assert output["sequence_last"] == 5
    assert output["sequence_gap_count"] == 0
    assert output["receive_age_min_ms"] == 100
    assert output["receive_age_max_ms"] == 500
    assert output["event_age_min_ms"] == 600
    assert output["event_age_max_ms"] == 1000
    assert output["event_to_receive_lag_min_ms"] == 500
    assert output["event_to_receive_lag_max_ms"] == 500
    assert not {
        "amount_cny",
        "high",
        "last",
        "low",
        "open",
        "previous_close",
        "volume_native",
    }.intersection(output)


def test_live_operator_review_evidence_rejects_sequence_gap():
    snapshot = ingest_registered_events(
        (
            _raw(
                sequence=1,
                event_time_ms=NOW_MS - 1000,
                received_at_ms=NOW_MS - 500,
            ),
            _raw(
                sequence=3,
                event_time_ms=NOW_MS - 900,
                received_at_ms=NOW_MS - 400,
            ),
        ),
        now_ms=NOW_MS,
    )

    with pytest.raises(ValueError, match="continuity"):
        build_live_operator_review_evidence(
            snapshot,
            observed_at_ms=NOW_MS,
            minimum_event_count=2,
        )


def test_live_operator_review_evidence_checks_all_event_clocks():
    first_time_ms = 1_775_000_000_000
    second_time_ms = first_time_ms + 9000
    snapshot = ingest_registered_events(
        (
            _raw(
                sequence=1,
                event_time_ms=first_time_ms,
                received_at_ms=first_time_ms,
            ),
            _raw(
                sequence=2,
                event_time_ms=second_time_ms,
                received_at_ms=second_time_ms,
            ),
        ),
        now_ms=second_time_ms,
    )

    with pytest.raises(ValueError, match="receive clock"):
        build_live_operator_review_evidence(
            snapshot,
            observed_at_ms=first_time_ms + 10001,
            minimum_event_count=2,
        )


def test_live_operator_review_probe_times_out_without_event(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    spool = tmp_path / "incoming"
    spool.mkdir()
    ticks = iter((100.0, 102.0))
    monkeypatch.setattr(live_probe.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(live_probe.time, "sleep", lambda _: None)

    result = live_probe.main(
        [
            "--spool-root",
            str(spool),
            "--timeout-seconds",
            "1",
            "--minimum-events",
            "1",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert result == 2
    assert output == {
        "ok": False,
        "operator_review_required": True,
        "status": "WAITING_FOR_FRESH_QMT_EVENT",
    }


def test_live_operator_review_probe_reports_acceptance_failure_as_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    snapshot = ingest_registered_events(
        (
            _raw(
                sequence=1,
                event_time_ms=NOW_MS - 1000,
                received_at_ms=NOW_MS - 500,
            ),
            _raw(
                sequence=3,
                event_time_ms=NOW_MS - 900,
                received_at_ms=NOW_MS - 400,
            ),
        ),
        now_ms=NOW_MS,
    )
    monkeypatch.setattr(
        live_probe,
        "read_registered_spool",
        lambda *args, **kwargs: snapshot,
    )
    monkeypatch.setattr(live_probe.time, "time", lambda: NOW_MS / 1000)

    result = live_probe.main(
        [
            "--spool-root",
            str(tmp_path),
            "--timeout-seconds",
            "1",
            "--minimum-events",
            "2",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert result == 1
    assert output == {
        "error": "event sequence continuity is incomplete",
        "ok": False,
        "operator_review_required": True,
        "status": "FAILED_CLOSED",
    }


def test_event_schema_identity_hash_and_symbol_fail_closed():
    with pytest.raises(ValueError, match="canonical ASCII JSON"):
        parse_registered_event(build_reference_event_bytes() + b"\n")

    payload = build_reference_event_payload()
    payload["unexpected"] = "unsafe"
    with pytest.raises(ValueError, match="closed schema"):
        parse_registered_event(canonical_bytes(payload))

    payload = build_reference_event_payload()
    payload["last"] = "10.11"
    with pytest.raises(ValueError, match="event_hash"):
        parse_registered_event(canonical_bytes(payload))

    with pytest.raises(ValueError, match="symbol is not registered"):
        parse_registered_event(_raw(symbol="000001.SZ"))


def test_runtime_requires_exact_registration_state_and_snapshot_types(
    tmp_path: Path,
):
    class FakeRegistration:
        bridge_id = DEFAULT_REGISTRATION.bridge_id
        schema_version = DEFAULT_REGISTRATION.schema_version
        source_kind = DEFAULT_REGISTRATION.source_kind
        allowed_symbols = ("000001.SZ",)
        max_event_bytes = 999_999

    fake_registration = FakeRegistration()
    with pytest.raises(TypeError, match="exact QMT bridge registration"):
        parse_registered_event(
            _raw(symbol="000001.SZ"),
            fake_registration,
        )
    with pytest.raises(TypeError, match="exact QMT bridge registration"):
        ingest_registered_events(
            (build_reference_event_bytes(),),
            now_ms=NOW_MS,
            registration=fake_registration,
        )
    with pytest.raises(TypeError, match="exact QMT bridge registration"):
        read_registered_spool(
            tmp_path,
            now_ms=NOW_MS,
            registration=fake_registration,
        )

    class DerivedState(QmtBridgeIngestState):
        pass

    derived_state = DerivedState(last_sequences={}, event_hashes=())
    with pytest.raises(TypeError, match="exact ingest state"):
        ingest_registered_events(
            (build_reference_event_bytes(),),
            now_ms=NOW_MS,
            prior_state=derived_state,
        )

    snapshot = build_reference_snapshot()

    class DerivedSnapshot(type(snapshot)):
        pass

    derived_snapshot = DerivedSnapshot(**snapshot.__dict__)
    with pytest.raises(TypeError, match="exact QMT bridge snapshot"):
        build_live_operator_review_evidence(
            derived_snapshot,
            observed_at_ms=NOW_MS,
        )


def test_decimal_ohlc_future_and_stale_values_fail_closed():
    with pytest.raises(ValueError, match="canonical"):
        parse_registered_event(_raw(last="NaN"))
    with pytest.raises(ValueError, match="low exceeds"):
        parse_registered_event(_raw(low="10.15"))
    with pytest.raises(ValueError, match="received time is in the future"):
        ingest_registered_events(
            (_raw(received_at_ms=NOW_MS + 3000),),
            now_ms=NOW_MS,
        )
    with pytest.raises(ValueError, match="stale"):
        ingest_registered_events(
            (
                _raw(
                    event_time_ms=NOW_MS - 10002,
                    received_at_ms=NOW_MS - 10001,
                ),
            ),
            now_ms=NOW_MS,
        )
    with pytest.raises(ValueError, match="market event time is stale"):
        ingest_registered_events(
            (
                _raw(
                    event_time_ms=NOW_MS - 10001,
                    received_at_ms=NOW_MS,
                ),
            ),
            now_ms=NOW_MS,
        )


def test_duplicate_out_of_order_and_noncanonical_batches_fail_closed():
    first = ingest_registered_events(
        (build_reference_event_bytes(),),
        now_ms=NOW_MS,
    )
    with pytest.raises(ValueError, match="duplicate event hash"):
        ingest_registered_events(
            (build_reference_event_bytes(),),
            now_ms=NOW_MS,
            prior_state=first.state,
        )
    with pytest.raises(ValueError, match="sequence"):
        ingest_registered_events(
            (_raw(sequence=1, received_at_ms=1_775_000_000_600),),
            now_ms=NOW_MS,
            prior_state=QmtBridgeIngestState(
                last_sequences={"600000.SH": 2},
                event_hashes=(),
            ),
        )
    with pytest.raises(ValueError, match="chronological"):
        ingest_registered_events(
            (
                _raw(sequence=2, received_at_ms=1_775_000_000_700),
                _raw(sequence=1, received_at_ms=1_775_000_000_600),
            ),
            now_ms=NOW_MS,
        )


def test_spool_reader_accepts_closed_files_and_rejects_unregistered_entries(
    tmp_path: Path,
):
    spool = tmp_path / "incoming"
    spool.mkdir()
    (spool / "quote-600000-SH-1775000000500-000000000001.json").write_bytes(
        build_reference_event_bytes()
    )
    snapshot = read_registered_spool(
        spool,
        now_ms=NOW_MS,
        prior_state=EMPTY_INGEST_STATE,
    )
    assert len(snapshot.accepted_events) == 1

    (spool / "notes.txt").write_text("unsafe", encoding="ascii")
    with pytest.raises(ValueError, match="unregistered entry"):
        read_registered_spool(spool, now_ms=NOW_MS)


def test_spool_reader_binds_filename_to_event_identity(tmp_path: Path):
    spool = tmp_path / "incoming"
    spool.mkdir()
    raw = build_reference_event_bytes()

    malformed = spool / "quote-unregistered.json"
    malformed.write_bytes(raw)
    with pytest.raises(ValueError, match="unregistered entry"):
        read_registered_spool(spool, now_ms=NOW_MS)

    malformed.unlink()
    mismatched = spool / "quote-600000-SH-1775000000501-000000000001.json"
    mismatched.write_bytes(raw)
    with pytest.raises(ValueError, match="filename does not match"):
        read_registered_spool(spool, now_ms=NOW_MS)


def test_spool_reader_rejects_link_root(tmp_path: Path):
    target = tmp_path / "target"
    target.mkdir()
    (
        target / "quote-600000-SH-1775000000500-000000000001.json"
    ).write_bytes(build_reference_event_bytes())
    link = tmp_path / "incoming-link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="regular local directory"):
        read_registered_spool(link, now_ms=NOW_MS)


def test_spool_reader_rejects_link_ancestor(tmp_path: Path):
    target_parent = tmp_path / "target-parent"
    target = target_parent / "incoming"
    target.mkdir(parents=True)
    (
        target / "quote-600000-SH-1775000000500-000000000001.json"
    ).write_bytes(build_reference_event_bytes())
    parent_link = tmp_path / "parent-link"
    try:
        parent_link.symlink_to(target_parent, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="regular local directory"):
        read_registered_spool(parent_link / "incoming", now_ms=NOW_MS)


def test_production_bridge_source_uses_only_read_only_qmt_calls():
    path = (
        Path(__file__).resolve().parents[2]
        / "apps"
        / "fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1"
        / "qmt_bridge.py"
    )
    report = inspect_bridge_file(path)

    assert report.ok
    assert report.context_calls == ("set_universe", "subscribe_quote")
    assert not report.forbidden_calls
    assert not report.forbidden_imports


def test_bridge_source_policy_rejects_link_paths(tmp_path: Path):
    source = (
        Path(__file__).resolve().parents[2]
        / "apps"
        / "fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1"
        / "qmt_bridge.py"
    )
    direct_link = tmp_path / "linked-source.py"
    try:
        direct_link.symlink_to(source)
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")
    with pytest.raises(ValueError, match="regular local file"):
        inspect_bridge_file(direct_link)

    target_parent = tmp_path / "target-parent"
    target_parent.mkdir()
    target = target_parent / "qmt_bridge.py"
    target.write_bytes(source.read_bytes())
    parent_link = tmp_path / "parent-link"
    parent_link.symlink_to(target_parent, target_is_directory=True)
    with pytest.raises(ValueError, match="regular local file"):
        inspect_bridge_file(parent_link / "qmt_bridge.py")


def test_policy_rejects_network_account_and_order_capability():
    unsafe = """
import socket
def _on_quote(data):
    return data
def init(ContextInfo):
    ContextInfo.set_account("unsafe")
    ContextInfo.passorder("unsafe")
"""
    report = inspect_bridge_source(unsafe)
    assert not report.ok
    assert report.forbidden_imports == ("socket",)
    assert report.forbidden_calls == ("passorder", "set_account")


def test_qmt_init_registers_one_read_only_tick_subscription(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _reset_bridge()
    _write_config(tmp_path)
    monkeypatch.setattr(qmt_bridge, "__file__", str(tmp_path / "qmt_bridge.py"))
    context = FakeContext()

    qmt_bridge.init(context)

    assert context.universe == ["600000.SH"]
    assert len(context.subscriptions) == 1
    subscription = context.subscriptions[0]
    assert subscription["symbol"] == "600000.SH"
    assert subscription["period"] == "tick"
    assert subscription["dividend_type"] == "none"
    assert subscription["result_type"] == "dict"
    assert subscription["callback"] is qmt_bridge._on_quote


def test_qmt_bridge_finds_config_without_dunder_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _reset_bridge()
    python_dir = tmp_path / "python"
    python_dir.mkdir()
    _write_config(python_dir)
    monkeypatch.delitem(qmt_bridge.__dict__, "__file__", raising=False)
    monkeypatch.chdir(tmp_path)
    context = FakeContext()

    qmt_bridge.init(context)

    assert context.universe == ["600000.SH"]
    assert len(context.subscriptions) == 1


def test_quote_callback_writes_one_atomic_ascii_event_and_rate_limits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _reset_bridge()
    _write_config(tmp_path)
    monkeypatch.setattr(qmt_bridge, "__file__", str(tmp_path / "qmt_bridge.py"))
    monotonic_ticks = iter((1000.5, 1000.6))
    monkeypatch.setattr(qmt_bridge.time, "monotonic", lambda: next(monotonic_ticks))
    monkeypatch.setattr(qmt_bridge.time, "time", lambda: 1_775_000_000.5)
    context = FakeContext()
    qmt_bridge.init(context)

    callback = context.subscriptions[0]["callback"]
    callback({"600000.SH": _quote()})
    callback({"600000.SH": _quote()})

    files = tuple((tmp_path / "bridge" / "incoming").glob("*.json"))
    assert len(files) == 1
    assert not tuple((tmp_path / "bridge" / "incoming").glob("*.tmp-*"))
    event = parse_registered_event(files[0].read_bytes())
    assert event.last == "10.1"
    assert event.volume_native == "120000"
    assert event.sequence == 1


def test_qmt_bridge_source_is_python_36_syntax_compatible():
    source = Path(qmt_bridge.__file__).read_text(encoding="ascii")

    ast.parse(source, feature_version=(3, 6))
    assert "time.time_ns" not in source


def test_config_and_subscription_failure_are_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _reset_bridge()
    _write_config(tmp_path, period="1m")
    monkeypatch.setattr(qmt_bridge, "__file__", str(tmp_path / "qmt_bridge.py"))
    with pytest.raises(ValueError, match="period must be tick"):
        qmt_bridge.init(FakeContext())

    _write_config(tmp_path)

    class RejectedContext(FakeContext):
        def subscribe_quote(self, symbol: str, **kwargs: object) -> int:
            return 0

    with pytest.raises(RuntimeError, match="subscription failed"):
        qmt_bridge.init(RejectedContext())


def test_registration_rejects_authority_expansion_and_unbounded_limits():
    with pytest.raises(ValueError, match="closed contract"):
        replace(DEFAULT_REGISTRATION, max_event_age_ms=120_000)
    with pytest.raises(ValueError, match="closed contract"):
        replace(DEFAULT_REGISTRATION, max_batch_files=5000)
    with pytest.raises(ValueError, match="closed contract"):
        replace(DEFAULT_REGISTRATION, allowed_symbols=("unsafe",))
    with pytest.raises(ValueError, match="exact tuple"):
        replace(DEFAULT_REGISTRATION, allowed_symbols=["600000.SH"])
    with pytest.raises(ValueError, match="closed contract"):
        replace(DEFAULT_REGISTRATION, allowed_symbols=("600000.SH", 1))
    for field in (
        "max_event_age_ms",
        "max_future_skew_ms",
        "max_event_bytes",
        "max_batch_files",
    ):
        with pytest.raises(ValueError, match="exact integers"):
            replace(DEFAULT_REGISTRATION, **{field: "1000"})


def test_snapshot_state_rejects_mutable_or_coerced_primitive_containers():
    with pytest.raises(ValueError, match="exact mapping"):
        QmtBridgeIngestState(
            last_sequences=[("600000.SH", 1)],
            event_hashes=(),
        )
    with pytest.raises(ValueError, match="exact tuple"):
        QmtBridgeIngestState(last_sequences={}, event_hashes=[])
    with pytest.raises(ValueError, match="SHA-256"):
        QmtBridgeIngestState(last_sequences={}, event_hashes=(1,))
    with pytest.raises(ValueError, match="SHA-256"):
        QmtBridgeIngestState(last_sequences={}, event_hashes=([],))
    with pytest.raises(ValueError, match="last_sequences is invalid"):
        QmtBridgeIngestState(
            last_sequences={"600000.SH": 1, 2: 1},
            event_hashes=(),
        )

    snapshot = build_reference_snapshot()
    with pytest.raises(ValueError, match="exact event tuple"):
        replace(snapshot, accepted_events=list(snapshot.accepted_events))
    with pytest.raises(ValueError, match="exact booleans"):
        replace(snapshot, read_only=1)
    with pytest.raises(ValueError, match="registration_hash"):
        replace(snapshot, registration_hash=1)
    with pytest.raises(ValueError, match="snapshot_hash"):
        replace(snapshot, snapshot_hash=1)
