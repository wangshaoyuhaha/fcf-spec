from copy import deepcopy

import pytest

from apps.ai_comprehensive_report_synthesis_app_1 import (
    APP_ID,
    CONTRACT_VERSION,
    STAGE_ID,
    ContractViolation,
    build_d1_contract,
    require_valid_d1_contract,
    validate_d1_contract,
)


def test_d1_contract_has_registered_identity() -> None:
    contract = build_d1_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["contract_version"] == CONTRACT_VERSION
    assert contract["status"] == "D1_COMPLETE"


def test_d1_contract_requires_permanent_boundaries() -> None:
    boundaries = build_d1_contract()["boundaries"]

    assert boundaries["paper_only"] is True
    assert boundaries["local_only"] is True
    assert boundaries["read_only"] is True
    assert boundaries["sidecar_only"] is True
    assert boundaries["deterministic_only"] is True
    assert boundaries["registered_artifacts_only"] is True
    assert boundaries["operator_review_required"] is True
    assert boundaries["source_artifacts_preserved"] is True
    assert boundaries["original_conclusions_preserved"] is True


def test_d1_contract_disables_unsafe_permissions() -> None:
    permissions = build_d1_contract()["permissions"]

    assert permissions
    assert all(value is False for value in permissions.values())
    assert permissions["live_model_invocation"] is False
    assert permissions["prompt_execution"] is False
    assert permissions["runtime_orchestrator_execution"] is False
    assert permissions["automatic_routing"] is False
    assert permissions["automatic_archive_execution"] is False
    assert permissions["trade_action"] is False
    assert permissions["real_execution"] is False


def test_d1_contract_preserves_governance_states() -> None:
    states = build_d1_contract()["governance_states"]

    assert states == {
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "operator_review": "REQUIRED",
        "operator_decision": "PENDING",
        "archive_execution": "NOT_PERFORMED",
    }


def test_d1_contract_blocks_authority_overlap() -> None:
    rules = build_d1_contract()["anti_overlap_rules"]

    assert rules["report_archive_authority"] == "NOT_GRANTED"
    assert rules["operator_decision_authority"] == "NOT_GRANTED"
    assert rules["upstream_artifact_mutation"] == "FORBIDDEN"
    assert rules["runtime_orchestration_authority"] == "NOT_GRANTED"
    assert rules["source_conclusion_rewrite"] == "FORBIDDEN"


def test_d1_contract_build_is_deterministic_and_independent() -> None:
    first = build_d1_contract()
    second = build_d1_contract()

    assert first == second
    assert first is not second
    assert first["boundaries"] is not second["boundaries"]
    assert first["permissions"] is not second["permissions"]


def test_d1_validator_rejects_source_preservation_change() -> None:
    contract = deepcopy(build_d1_contract())
    contract["boundaries"]["source_artifacts_preserved"] = False

    errors = validate_d1_contract(contract)

    assert errors
    assert any(
        "boundaries.source_artifacts_preserved" in error
        for error in errors
    )

    with pytest.raises(ContractViolation):
        require_valid_d1_contract(contract)


def test_d1_validator_rejects_runtime_orchestration_permission() -> None:
    contract = deepcopy(build_d1_contract())
    contract["permissions"]["runtime_orchestrator_execution"] = True

    errors = validate_d1_contract(contract)

    assert errors
    assert any(
        "permissions.runtime_orchestrator_execution" in error
        for error in errors
    )


def test_d1_validator_accepts_registered_contract() -> None:
    contract = build_d1_contract()

    assert validate_d1_contract(contract) == ()
    assert require_valid_d1_contract(contract) is contract