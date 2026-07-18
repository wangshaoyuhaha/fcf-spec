import hashlib
import json
import shutil
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    build_console_read_model,
    build_default_operator_launch_profile,
    load_starter_artifact_package,
)
from apps.browser_product_console_runtime_app_1.research_workspace_views import (
    build_governance_workspace_model,
)
from apps.v2_r39_browser_operator_factor_governance_projection_integration_app_1 import (
    parse_registered_browser_governance_projection,
)
from apps.v2_r41_browser_governance_starter_package_integration_app_1 import (
    V2_R41_BROWSER_GOVERNANCE_STARTER_PACKAGE_BOUNDARY,
    V2R41BrowserGovernanceStarterPackageBoundary,
    build_starter_governance_acceptance,
)


ROOT = Path(__file__).resolve().parents[2]


def _loaded():
    profile = build_default_operator_launch_profile(project_root=ROOT)
    return load_starter_artifact_package(profile)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R41_BROWSER_GOVERNANCE_STARTER_PACKAGE_BOUNDARY
    assert boundary.demonstration_only and boundary.read_only
    assert not boundary.network_fetch_allowed and not boundary.write_controls_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.demonstration_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_action_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R41BrowserGovernanceStarterPackageBoundary(
            factor_activation_allowed=True
        )


def test_d2_starter_package_contains_exact_new_governance_artifacts():
    package, _ = _loaded()
    assert package.artifact_count == 16
    assert "demo-model-governance" in package.artifact_ids
    assert "demo-factor-governance-projection" in package.artifact_ids


def test_d2_governance_artifact_types_are_registered():
    package, _ = _loaded()
    assert {"model_governance", "policy_snapshot"}.issubset(package.artifact_types)
    assert "factor_governance_projection" in package.artifact_types


def test_d3_projection_payload_is_valid_and_demonstration_only():
    _, loaded = _loaded()
    artifact = next(
        item
        for item in loaded.artifacts
        if item.registration.artifact_type == "factor_governance_projection"
    )
    parsed = parse_registered_browser_governance_projection(artifact.payload)
    assert parsed.projection.candidate_id == "demo-a-share-candidate"
    assert artifact.payload["data_classification"] == "DEMONSTRATION_ONLY"


def test_d3_model_governance_preserves_authority_labels():
    _, loaded = _loaded()
    payload = next(
        item.payload
        for item in loaded.artifacts
        if item.registration.artifact_type == "model_governance"
    )
    assert payload["deterministic_authority"] is True
    assert payload["registered_evidence_authority"] is True
    assert payload["ai_advisory_only"] is True


def test_d4_index_digests_match_new_artifact_bytes():
    _, loaded = _loaded()
    for artifact_type in ("model_governance", "factor_governance_projection"):
        artifact = next(
            item
            for item in loaded.artifacts
            if item.registration.artifact_type == artifact_type
        )
        digest = hashlib.sha256(Path(artifact.source_path).read_bytes()).hexdigest()
        assert digest == artifact.registration.content_sha256


def test_d4_workspace_is_available_with_one_projection():
    _, loaded = _loaded()
    workspace = build_governance_workspace_model(build_console_read_model(loaded))
    assert workspace.state == "AVAILABLE"
    assert len(workspace.projection_presentations) == 1


def test_d5_default_governance_page_shows_semantic_details():
    _, loaded = _loaded()
    app = BrowserProductConsoleApplication(build_console_read_model(loaded))
    response = app.dispatch("GET", "/governance")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "Factor Governance Field Detail" in body
    assert "demo-policy-novelty-alignment" in body
    assert "OBSERVED" in body and "INFERRED" in body


def test_d5_default_governance_page_remains_read_only():
    _, loaded = _loaded()
    app = BrowserProductConsoleApplication(build_console_read_model(loaded))
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_reports_complete_demonstration():
    package, loaded = _loaded()
    acceptance = build_starter_governance_acceptance(loaded)
    assert acceptance.artifact_count == package.artifact_count
    assert acceptance.governance_state == "AVAILABLE"
    assert acceptance.projection_count == 1
    assert acceptance.observed_field_count == 1
    assert acceptance.inferred_field_count == 1


def test_d6_acceptance_is_non_actionable():
    _, loaded = _loaded()
    acceptance = build_starter_governance_acceptance(loaded)
    assert acceptance.status == "READY_FOR_READ_ONLY_GOVERNANCE_DEMONSTRATION"
    assert acceptance.operator_review_required and acceptance.read_only
    assert not acceptance.factor_activated and not acceptance.action_created


def test_d6_starter_projection_tampering_fails_closed(tmp_path: Path):
    source = build_default_operator_launch_profile(project_root=ROOT).allowed_root
    copied = tmp_path / "starter"
    shutil.copytree(source, copied)
    path = copied / "registered" / "factor-governance-projection.json"
    payload = json.loads(path.read_text(encoding="ascii"))
    payload["confidence"] = "HIGH"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="ascii")
    profile = build_default_operator_launch_profile(project_root=tmp_path)
    profile = profile.__class__(allowed_root=copied, index_path=copied / "index.json")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_starter_artifact_package(profile)
