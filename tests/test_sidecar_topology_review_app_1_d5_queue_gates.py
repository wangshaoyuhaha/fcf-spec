from pathlib import Path


def test_sidecar_topology_review_d5_queue_gates_exists():
    path = Path("docs/sidecar_topology_review_app_1/D5_FUTURE_SIDECAR_QUEUE_AND_GATES.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "D5 Future Sidecar Queue and Governance Gates" in text
    assert "Candidate sidecar queue" in text
    assert "Governance gates" in text
    assert "DIFY-LOCAL-CONFIG-HARDENING-APP-1" in text


def test_sidecar_topology_review_d5_required_candidates():
    text = Path("docs/sidecar_topology_review_app_1/D5_FUTURE_SIDECAR_QUEUE_AND_GATES.md").read_text(
        encoding="utf-8"
    )
    required = [
        "CONTROL-CENTER-MAINTENANCE-APP-1",
        "DIFY-LOCAL-CONFIG-HARDENING-APP-1",
        "CORRELATION-ID-TRACEABILITY-APP-1",
        "RISK-FLAG-VISIBILITY-APP-1",
        "REASON-CODE-GOVERNANCE-APP-1",
        "ARCHIVE-INTEGRITY-REVIEW-APP-1",
        "OPERATOR-WORKFLOW-REVIEW-APP-1",
    ]
    for item in required:
        assert item in text


def test_sidecar_topology_review_d5_required_gates():
    text = Path("docs/sidecar_topology_review_app_1/D5_FUTURE_SIDECAR_QUEUE_AND_GATES.md").read_text(
        encoding="utf-8"
    )
    required = [
        "Scope gate",
        "Core freeze gate",
        "Data and artifact gate",
        "Operator review gate",
        "UI and presentation gate",
        "Dify and external tool gate",
        "Validation gate",
    ]
    for item in required:
        assert item in text


def test_sidecar_topology_review_d5_safety_boundary():
    text = Path("docs/sidecar_topology_review_app_1/D5_FUTURE_SIDECAR_QUEUE_AND_GATES.md").read_text(
        encoding="utf-8"
    )
    required = [
        "No future sidecar may start automatically",
        "explicit operator approval",
        "no P48",
        "no mutation of frozen core P1-P47",
        "no deploy",
        "no release",
        "no tag without explicit approval",
        "no automatic Dify app creation",
        "no Dify API write",
        "no broker, exchange, or wallet connection",
    ]
    for item in required:
        assert item in text