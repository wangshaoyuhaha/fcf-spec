from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apps.fcp_0083_a_share_guojin_miniqmt_sanitized_evidence_local_validation_runner_app_1 import (
    MAX_ARTIFACT_BYTES,
    main,
    render_packet_json,
    validate_local_evidence,
)


def payload(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "capabilities": ["DAILY_BAR", "MINUTE_BAR"],
        "captured_at_utc": "2026-07-23T10:00:00Z",
        "clock_semantics": "ASIA_SHANGHAI_EXCHANGE_TIME",
        "entitlement_declared_state": "GRANTED",
        "evidence_revision": "operator-evidence-v1",
        "expires_at_utc": "2026-08-23T10:00:00Z",
        "markets": ["SSE", "SZSE"],
        "module_file_sha256": "2" * 64,
        "probe_status": "SUCCEEDED",
        "python_module_name": "xtquant",
        "python_module_version": "1.0.0",
        "retention_state": "DOCUMENTED",
        "rights_state": "DOCUMENTED",
        "supporting_document_sha256": "3" * 64,
        "terminal_product": "GUOJIN_MINIQMT",
        "terminal_version": "2.1.19.0",
    }
    value.update(overrides)
    return value


def write_artifact(tmp_path: Path, **overrides: object) -> tuple[Path, bytes]:
    raw = json.dumps(
        payload(**overrides),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    path = tmp_path / "miniqmt-entitlement-evidence.json"
    path.write_bytes(raw)
    return path, raw


def validate(path: Path, raw: bytes):
    return validate_local_evidence(
        path,
        artifact_id="guojin-miniqmt-evidence-v1",
        expected_sha256=hashlib.sha256(raw).hexdigest(),
        expected_byte_length=len(raw),
        as_of_utc="2026-07-23T11:00:00Z",
    )


def test_runner_validates_complete_evidence_without_mutating_source(tmp_path: Path):
    path, raw = write_artifact(tmp_path)
    before = path.read_bytes()
    before_time = path.stat().st_mtime_ns
    packet = validate(path, raw)
    assert packet.decision_state == "OPERATOR_REVIEW_ELIGIBLE"
    assert path.read_bytes() == before
    assert path.stat().st_mtime_ns == before_time


def test_runner_preserves_non_authorizing_boundary(tmp_path: Path):
    path, raw = write_artifact(tmp_path)
    packet = validate(path, raw)
    assert packet.entitlement_authorized is False
    assert packet.registered_evidence_authority is False
    assert packet.realtime_activation_authorized is False
    assert packet.provider_selected is False
    assert packet.data_promotion_authorized is False
    assert packet.closes_gap is False
    assert packet.operator_review_required is True


def test_rendered_json_is_canonical_ascii_and_deterministic(tmp_path: Path):
    path, raw = write_artifact(tmp_path)
    packet = validate(path, raw)
    first = render_packet_json(packet)
    second = render_packet_json(packet)
    assert first == second
    assert first == first.encode("ascii").decode("ascii")
    assert " " not in first
    assert json.loads(first)["packet_hash"] == packet.packet_hash


def test_incomplete_evidence_renders_fail_closed_packet(tmp_path: Path):
    path, raw = write_artifact(tmp_path, entitlement_declared_state="UNKNOWN")
    packet = validate(path, raw)
    assert packet.decision_state == "INSUFFICIENT_EVIDENCE"
    assert "ENTITLEMENT_NOT_DECLARED_GRANTED" in packet.blockers


@pytest.mark.parametrize(
    "change,match",
    (
        ({"expected_sha256": "0" * 64}, "SHA-256 mismatch"),
        ({"expected_byte_length": 2}, "length mismatch"),
        ({"artifact_id": "unsafe identity"}, "safe value"),
        ({"as_of_utc": "2026-07-23T19:00:00+08:00"}, "as_of_utc"),
    ),
)
def test_runner_rejects_invalid_registration(tmp_path: Path, change: dict[str, object], match: str):
    path, raw = write_artifact(tmp_path)
    args: dict[str, object] = {
        "artifact_id": "guojin-miniqmt-evidence-v1",
        "expected_sha256": hashlib.sha256(raw).hexdigest(),
        "expected_byte_length": len(raw),
        "as_of_utc": "2026-07-23T11:00:00Z",
    }
    args.update(change)
    with pytest.raises(ValueError, match=match):
        validate_local_evidence(path, **args)  # type: ignore[arg-type]


def test_runner_rejects_missing_file(tmp_path: Path):
    with pytest.raises(ValueError, match="existing regular file"):
        validate_local_evidence(
            tmp_path / "missing.json",
            artifact_id="guojin-miniqmt-evidence-v1",
            expected_sha256="0" * 64,
            expected_byte_length=2,
            as_of_utc="2026-07-23T11:00:00Z",
        )


def test_runner_rejects_directory(tmp_path: Path):
    with pytest.raises(ValueError, match="existing regular file"):
        validate_local_evidence(
            tmp_path,
            artifact_id="guojin-miniqmt-evidence-v1",
            expected_sha256="0" * 64,
            expected_byte_length=2,
            as_of_utc="2026-07-23T11:00:00Z",
        )


def test_runner_rejects_symlink_when_supported(tmp_path: Path):
    source, raw = write_artifact(tmp_path)
    link = tmp_path / "evidence-link.json"
    try:
        link.symlink_to(source)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(ValueError, match="symlink"):
        validate_local_evidence(
            link,
            artifact_id="guojin-miniqmt-evidence-v1",
            expected_sha256=hashlib.sha256(raw).hexdigest(),
            expected_byte_length=len(raw),
            as_of_utc="2026-07-23T11:00:00Z",
        )


def test_runner_rejects_oversized_registration(tmp_path: Path):
    path = tmp_path / "oversized.json"
    path.write_bytes(b"x" * (MAX_ARTIFACT_BYTES + 1))
    with pytest.raises(ValueError, match="bounded limit"):
        validate_local_evidence(
            path,
            artifact_id="guojin-miniqmt-evidence-v1",
            expected_sha256="0" * 64,
            expected_byte_length=MAX_ARTIFACT_BYTES + 1,
            as_of_utc="2026-07-23T11:00:00Z",
        )


def test_cli_prints_only_canonical_review_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    path, raw = write_artifact(tmp_path)
    result = main(
        (
            "--artifact",
            str(path),
            "--artifact-id",
            "guojin-miniqmt-evidence-v1",
            "--sha256",
            hashlib.sha256(raw).hexdigest(),
            "--byte-length",
            str(len(raw)),
            "--as-of-utc",
            "2026-07-23T11:00:00Z",
        )
    )
    captured = capsys.readouterr()
    assert result == 0
    assert captured.err == ""
    assert json.loads(captured.out)["decision_state"] == "OPERATOR_REVIEW_ELIGIBLE"


def test_cli_failure_is_generic_and_does_not_echo_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    missing = tmp_path / "secret-token-value.json"
    result = main(
        (
            "--artifact",
            str(missing),
            "--artifact-id",
            "guojin-miniqmt-evidence-v1",
            "--sha256",
            "0" * 64,
            "--byte-length",
            "2",
            "--as-of-utc",
            "2026-07-23T11:00:00Z",
        )
    )
    captured = capsys.readouterr()
    assert result == 2
    assert captured.out == ""
    assert captured.err.strip() == '{"error":"LOCAL_EVIDENCE_VALIDATION_FAILED"}'
    assert "secret-token-value" not in captured.err
