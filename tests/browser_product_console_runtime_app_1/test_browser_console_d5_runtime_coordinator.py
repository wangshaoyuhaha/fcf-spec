import hashlib
import json
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import ConsoleRuntimeCoordinator


def _evidence(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "candidate.json"
    content = b'{"symbol":"600000","score":88.5}'
    path.write_bytes(content)
    return path, hashlib.sha256(content).hexdigest()


def _payload(digest: str, **updates):
    value = {
        "command_id": "cmd-001",
        "correlation_id": "corr-001",
        "artifact_id": "candidate-001",
        "expected_artifact_sha256": digest,
        "decision": "ACKNOWLEDGE_EVIDENCE",
        "reviewer_id": "operator-001",
        "submitted_at_utc": "2026-07-14T00:00:00Z",
        "note": "reviewed",
    }
    value.update(updates)
    return value


def test_d5_coordinator_writes_atomic_review_bundle(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    result = ConsoleRuntimeCoordinator(tmp_path, tmp_path / "output").process_operator_review(
        _payload(digest),
        evidence_path,
    )
    bundle = Path(result.output_directory)
    assert {path.name for path in bundle.iterdir()} == {
        "audit.json",
        "manifest.json",
        "receipt.json",
    }
    assert result.reused_existing_bundle is False


def test_d5_exact_rerun_reuses_existing_bundle(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    coordinator = ConsoleRuntimeCoordinator(tmp_path, tmp_path / "output")
    first = coordinator.process_operator_review(_payload(digest), evidence_path)
    second = coordinator.process_operator_review(_payload(digest), evidence_path)
    assert first.manifest_sha256 == second.manifest_sha256
    assert second.reused_existing_bundle is True


def test_d5_tampered_bundle_is_rejected(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    coordinator = ConsoleRuntimeCoordinator(tmp_path, tmp_path / "output")
    result = coordinator.process_operator_review(_payload(digest), evidence_path)
    Path(result.output_directory, "receipt.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="tampered or command changed"):
        coordinator.process_operator_review(_payload(digest), evidence_path)


def test_d5_incomplete_bundle_is_rejected(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    coordinator = ConsoleRuntimeCoordinator(tmp_path, tmp_path / "output")
    result = coordinator.process_operator_review(_payload(digest), evidence_path)
    Path(result.output_directory, "audit.json").unlink()
    with pytest.raises(ValueError, match="incomplete or unexpected"):
        coordinator.process_operator_review(_payload(digest), evidence_path)


def test_d5_changed_command_with_same_id_is_rejected(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    coordinator = ConsoleRuntimeCoordinator(tmp_path, tmp_path / "output")
    coordinator.process_operator_review(_payload(digest), evidence_path)
    with pytest.raises(ValueError, match="tampered or command changed"):
        coordinator.process_operator_review(
            _payload(digest, note="different note"),
            evidence_path,
        )


def test_d5_output_root_must_remain_inside_allowed_root(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    with pytest.raises(ValueError, match="inside allowed_root"):
        ConsoleRuntimeCoordinator(allowed, outside)


def test_d5_receipt_preserves_no_automatic_authority(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    result = ConsoleRuntimeCoordinator(tmp_path, tmp_path / "output").process_operator_review(
        _payload(digest),
        evidence_path,
    )
    receipt = json.loads(Path(result.output_directory, "receipt.json").read_text(encoding="utf-8"))
    assert receipt["automatic_approval"] is False
    assert receipt["automatic_promotion"] is False
    assert receipt["automatic_archive"] is False
    assert receipt["paper_only"] is True
