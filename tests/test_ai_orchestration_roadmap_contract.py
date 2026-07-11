"""Tests for AI orchestration roadmap D1 contract."""

from copy import deepcopy

from fcf.sidecars.ai_orchestration_roadmap import (
    APP_ID,
    ROADMAP_MODE,
    STAGE_ID,
    build_roadmap_boundary_contract,
    validate_roadmap_boundary_contract,
)


def test_contract_identity() -> None:
    contract = build_roadmap_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["roadmap_mode"] == ROADMAP_MODE


def test_valid_contract_passes_validation() -> None:
    contract = build_roadmap_boundary_contract()

    assert validate_roadmap_boundary_contract(contract) == []


def test_contract_is_planning_only() -> None:
    contract = build_roadmap_boundary_contract()

    assert contract["safety_flags"]["planning_only"] is True
    assert (
        contract["safety_flags"][
            "roadmap_outputs_non_executable"
        ]
        is True
    )


def test_runtime_orchestrator_is_forbidden() -> None:
    contract = build_roadmap_boundary_contract()

    assert (
        contract["overlap_policy"][
            "runtime_orchestrator_created"
        ]
        is False
    )
    assert (
        contract["safety_flags"][
            "ai_orchestrator_execution_allowed"
        ]
        is False
    )


def test_research_workflow_authority_is_preserved() -> None:
    contract = build_roadmap_boundary_contract()

    assert (
        contract["overlap_policy"][
            "research_workflow_app_remains_authoritative"
        ]
        is True
    )


def test_live_model_and_prompt_execution_are_forbidden() -> None:
    contract = build_roadmap_boundary_contract()

    flags = contract["safety_flags"]

    assert flags["live_model_invocation_allowed"] is False
    assert flags["prompt_execution_allowed"] is False


def test_automatic_routing_and_switching_are_forbidden() -> None:
    contract = build_roadmap_boundary_contract()

    flags = contract["safety_flags"]

    assert flags["automatic_route_selection_allowed"] is False
    assert flags["automatic_role_switching_allowed"] is False
    assert flags["automatic_model_switching_allowed"] is False
    assert flags["automatic_prompt_switching_allowed"] is False


def test_truth_winner_probability_and_rank_remain_forbidden() -> None:
    contract = build_roadmap_boundary_contract()

    flags = contract["safety_flags"]

    assert flags["automatic_truth_decision_allowed"] is False
    assert flags["automatic_winner_selection_allowed"] is False
    assert (
        flags["automatic_probability_assignment_allowed"]
        is False
    )
    assert flags["automatic_ranking_allowed"] is False


def test_validation_rejects_runtime_execution() -> None:
    contract = build_roadmap_boundary_contract()
    contract["safety_flags"][
        "ai_orchestrator_execution_allowed"
    ] = True

    assert (
        "ai_orchestrator_execution_allowed_must_be_false"
        in validate_roadmap_boundary_contract(contract)
    )


def test_validation_rejects_core_mutation() -> None:
    contract = build_roadmap_boundary_contract()
    contract["overlap_policy"]["core_mutation_allowed"] = True

    assert "overlap_policy_invalid" in (
        validate_roadmap_boundary_contract(contract)
    )


def test_builder_returns_fresh_containers() -> None:
    first = build_roadmap_boundary_contract()
    second = build_roadmap_boundary_contract()
    mutated = deepcopy(first)

    mutated["allowed_inputs"].append("UNREGISTERED_INPUT")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == build_roadmap_boundary_contract()
    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert validate_roadmap_boundary_contract([]) == [
        "contract_must_be_mapping"
    ]
