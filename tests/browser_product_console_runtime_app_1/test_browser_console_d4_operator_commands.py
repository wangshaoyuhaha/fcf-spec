import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BROWSER_CONSOLE_OPERATOR_COMMAND_BOUNDARY,
    GovernedOperatorCommandService,
    OperatorReviewCommand,
    handle_operator_api_request,
)


def _evidence(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "candidate.json"
    content = b'{"symbol":"600000"}'
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


def test_d4_boundary_preserves_operator_authority():
    boundary = BROWSER_CONSOLE_OPERATOR_COMMAND_BOUNDARY
    assert boundary.paper_only is True
    assert boundary.loopback_only is True
    assert boundary.operator_present_required is True
    assert boundary.automatic_approval_allowed is False
    assert boundary.real_execution_allowed is False


def test_d4_boundary_rejects_automatic_approval():
    with pytest.raises(ValueError, match="prohibited operator command capability"):
        replace(
            BROWSER_CONSOLE_OPERATOR_COMMAND_BOUNDARY,
            automatic_approval_allowed=True,
        )


def test_d4_command_rejects_unsupported_decision():
    with pytest.raises(ValueError, match="unsupported operator decision"):
        OperatorReviewCommand(**_payload("a" * 64, decision="APPROVE_AND_PROMOTE"))


def test_d4_rejection_requires_note():
    with pytest.raises(ValueError, match="note is required"):
        OperatorReviewCommand(**_payload("a" * 64, decision="REJECT_CANDIDATE", note=""))


def test_d4_service_validates_registered_evidence(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    validated = GovernedOperatorCommandService(tmp_path).validate(
        _payload(digest),
        evidence_path,
        "127.0.0.1",
    )
    assert validated.evidence_sha256 == digest
    assert len(validated.command_sha256) == 64
    assert validated.automatic_transition_allowed is False


def test_d4_api_rejects_non_loopback_peer(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    response = handle_operator_api_request(
        "POST",
        "/api/operator-review/validate",
        "192.168.1.10",
        _payload(digest),
        evidence_path,
        GovernedOperatorCommandService(tmp_path),
    )
    assert response.status == 403


def test_d4_api_validates_without_transition_authority(tmp_path: Path):
    evidence_path, digest = _evidence(tmp_path)
    response = handle_operator_api_request(
        "POST",
        "/api/operator-review/validate",
        "127.0.0.1",
        _payload(digest),
        evidence_path,
        GovernedOperatorCommandService(tmp_path),
    )
    assert response.status == 200
    assert response.payload["status"] == "VALIDATED_OPERATOR_COMMAND"
    assert response.payload["automatic_transition_allowed"] is False
