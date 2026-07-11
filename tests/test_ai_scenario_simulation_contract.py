"""Tests for the AI scenario simulation D1 boundary contract."""

from copy import deepcopy

from fcf.sidecars.ai_scenario_simulation import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    OVERLAP_POLICY,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)


def test_boundary_contract_identity() -> None:
    contract = build_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["contract_version"] == "1.0.0"
    assert contract["truth_status"] == "UNDETERMINED"


def test_boundary_contract_uses_registered_inputs_only() -> None:
    contract = build_boundary_contract()

    assert contract["allowed_inputs"] == list(ALLOWED_INPUTS)
    assert "registered_market_scenario_definition" in (
        contract["allowed_inputs"]
    )
    assert "live_market_data" not in contract["allowed_inputs"]


def test_boundary_contract_declares_governance_outputs() -> None:
    contract = build_boundary_contract()

    assert contract["allowed_outputs"] == list(ALLOWED_OUTPUTS)
    assert "scenario_simulation_review_packet" in (
        contract["allowed_outputs"]
    )
    assert "trade_order" not in contract["allowed_outputs"]


def test_boundary_contract_preserves_safety_flags() -> None:
    flags = build_boundary_contract()["safety_flags"]

    for name in REQUIRED_TRUE_FLAGS:
        assert flags[name] is True

    for name in REQUIRED_FALSE_FLAGS:
        assert flags[name] is False


def test_boundary_contract_prevents_market_scenario_overlap() -> None:
    policy = build_boundary_contract()["overlap_policy"]

    assert policy == OVERLAP_POLICY
    assert policy["creates_scenario_registry"] is False
    assert policy["mutates_registered_scenarios"] is False
    assert policy["replaces_market_scenario_app"] is False
    assert policy["simulation_result_is_truth"] is False
    assert policy["simulation_result_is_forecast"] is False
    assert policy["simulation_result_is_trade_instruction"] is False


def test_boundary_contract_validation_passes() -> None:
    assert validate_boundary_contract(build_boundary_contract()) == []


def test_validation_detects_unregistered_input() -> None:
    contract = build_boundary_contract()
    contract["allowed_inputs"].append("unregistered_live_input")

    assert validate_boundary_contract(contract) == [
        "allowed_inputs_must_match_contract"
    ]


def test_validation_detects_execution_boundary_violation() -> None:
    contract = build_boundary_contract()
    contract["safety_flags"]["real_execution_allowed"] = True

    assert (
        "real_execution_allowed_must_be_false"
        in validate_boundary_contract(contract)
    )


def test_validation_detects_overlap_policy_violation() -> None:
    contract = build_boundary_contract()
    contract["overlap_policy"]["creates_scenario_registry"] = True

    assert validate_boundary_contract(contract) == [
        "overlap_policy_must_match_contract"
    ]


def test_validation_rejects_non_mapping() -> None:
    assert validate_boundary_contract([]) == [
        "contract_must_be_mapping"
    ]


def test_builder_returns_fresh_mutable_containers() -> None:
    first = build_boundary_contract()
    second = build_boundary_contract()

    mutated = deepcopy(first)
    mutated["allowed_inputs"].append("invalid")
    mutated["safety_flags"]["trade_action_allowed"] = True
    mutated["overlap_policy"]["replaces_market_scenario_app"] = True

    assert second == build_boundary_contract()
    assert mutated != second
