"""Tests for AI orchestration runtime readiness D2 roles."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    ROLE_CONTRACT_STAGE_ID,
    ROLE_POLICY_IDENTIFIERS,
    TERMINAL_OPERATOR_ROLE_ID,
    RoleContractViolation,
    build_machine_readable_role_contract_manifest,
    build_runtime_readiness_boundary_contract,
    validate_machine_readable_role_contract_manifest,
)


def _build_manifest() -> dict[str, object]:
    return build_machine_readable_role_contract_manifest(
        manifest_id="fcf.runtime.roles.v1",
        boundary_contract=(
            build_runtime_readiness_boundary_contract()
        ),
    )


def test_valid_manifest_passes_validation() -> None:
    manifest = _build_manifest()

    assert (
        validate_machine_readable_role_contract_manifest(
            manifest
        )
        == []
    )


def test_manifest_identity_and_stage() -> None:
    manifest = _build_manifest()

    assert manifest["manifest_id"] == "fcf.runtime.roles.v1"
    assert manifest["stage_id"] == ROLE_CONTRACT_STAGE_ID


def test_roles_match_locked_v2_chain() -> None:
    manifest = _build_manifest()
    role_ids = [role["role_id"] for role in manifest["roles"]]

    assert role_ids == [
        "runtime_orchestration_coordinator",
        "market_narrative_context_analyst",
        "causal_reasoning_analyst",
        "contrarian_challenge_reviewer",
        "comprehensive_report_synthesizer",
        TERMINAL_OPERATOR_ROLE_ID,
    ]


def test_ai_roles_are_advisory_only() -> None:
    manifest = _build_manifest()

    for role in manifest["roles"]:
        if role["role_kind"] == "PLANNED_AI_ROLE":
            assert role["authority"] == "ADVISORY_ONLY"


def test_coordinator_has_no_truth_or_route_authority() -> None:
    coordinator = _build_manifest()["roles"][0]

    assert coordinator["authority"] == "COORDINATION_ONLY"
    assert coordinator["automatic_routing_status"] == "NOT_ALLOWED"
    assert coordinator["runtime_execution_status"] == "NOT_ALLOWED"


def test_human_operator_is_terminal_role() -> None:
    manifest = _build_manifest()

    assert manifest["roles"][-1]["role_id"] == (
        TERMINAL_OPERATOR_ROLE_ID
    )
    assert manifest["roles"][-1]["authority"] == (
        "FINAL_MANUAL_REVIEW"
    )


def test_all_roles_require_operator_gate() -> None:
    manifest = _build_manifest()

    assert all(
        role["operator_gate_required"] is True
        for role in manifest["roles"]
    )


def test_model_prompt_route_archive_and_runtime_forbidden() -> None:
    manifest = _build_manifest()

    for role in manifest["roles"]:
        assert role["model_invocation_status"] == "NOT_ALLOWED"
        assert role["prompt_execution_status"] == "NOT_ALLOWED"
        assert role["automatic_routing_status"] == "NOT_ALLOWED"
        assert role["archive_writing_status"] == "NOT_ALLOWED"
        assert role["runtime_execution_status"] == "NOT_ALLOWED"


def test_role_policy_identifiers_are_present() -> None:
    manifest = _build_manifest()

    for identifier in ROLE_POLICY_IDENTIFIERS:
        assert identifier in manifest["policy_identifiers"]


def test_output_ownership_is_unique() -> None:
    manifest = _build_manifest()
    output_types = [
        item["output_artifact_type"]
        for item in manifest["output_ownership"]
    ]

    assert len(output_types) == len(set(output_types))


def test_invalid_manifest_id_is_rejected() -> None:
    with pytest.raises(RoleContractViolation):
        build_machine_readable_role_contract_manifest(
            manifest_id="invalid manifest id",
            boundary_contract=(
                build_runtime_readiness_boundary_contract()
            ),
        )


def test_validation_rejects_automatic_routing() -> None:
    manifest = _build_manifest()
    manifest["roles"][0]["automatic_routing_status"] = "ALLOWED"

    assert "automatic_routing_status_invalid" in (
        validate_machine_readable_role_contract_manifest(
            manifest
        )
    )


def test_validation_rejects_ai_authority_escalation() -> None:
    manifest = _build_manifest()
    manifest["roles"][1]["authority"] = "FINAL_MANUAL_REVIEW"

    assert "planned_ai_role_authority_invalid" in (
        validate_machine_readable_role_contract_manifest(
            manifest
        )
    )


def test_validation_rejects_non_terminal_operator() -> None:
    manifest = _build_manifest()
    manifest["roles"][-1], manifest["roles"][-2] = (
        manifest["roles"][-2],
        manifest["roles"][-1],
    )

    assert "human_operator_must_be_terminal_role" in (
        validate_machine_readable_role_contract_manifest(
            manifest
        )
    )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _build_manifest()
    second = _build_manifest()
    mutated = deepcopy(first)

    mutated["roles"][0]["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert second == _build_manifest()
    assert mutated != second


def test_non_mapping_manifest_is_rejected() -> None:
    assert validate_machine_readable_role_contract_manifest(
        []
    ) == ["manifest_must_be_mapping"]