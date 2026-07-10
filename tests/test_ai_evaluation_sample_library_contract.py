from copy import deepcopy
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_sample_library.contract import (
    APP_ID,
    CONTRACT_VERSION,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_FORBIDDEN_CAPABILITIES,
    REQUIRED_TRUE_FLAGS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)


def test_boundary_contract_identity() -> None:
    contract = build_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["contract_version"] == CONTRACT_VERSION


def test_boundary_contract_required_true_flags() -> None:
    contract = build_boundary_contract()

    for field in REQUIRED_TRUE_FLAGS:
        assert contract[field] is True


def test_boundary_contract_required_false_flags() -> None:
    contract = build_boundary_contract()

    for field in REQUIRED_FALSE_FLAGS:
        assert contract[field] is False


def test_boundary_contract_declares_local_inputs() -> None:
    contract = build_boundary_contract()

    assert (
        "local_prompt_model_version_registry_reference"
        in contract["allowed_inputs"]
    )
    assert (
        "local_context_evidence_reference"
        in contract["allowed_inputs"]
    )


def test_boundary_contract_declares_governance_outputs() -> None:
    contract = build_boundary_contract()

    assert (
        "local_sample_definition_metadata"
        in contract["allowed_outputs"]
    )
    assert (
        "paper_only_governance_handoff"
        in contract["allowed_outputs"]
    )


def test_boundary_contract_blocks_forbidden_capabilities() -> None:
    contract = build_boundary_contract()

    for capability in REQUIRED_FORBIDDEN_CAPABILITIES:
        assert capability in contract["forbidden_capabilities"]


def test_boundary_contract_validation_passes() -> None:
    contract = build_boundary_contract()

    assert validate_boundary_contract(contract) == []


def test_boundary_contract_validation_detects_bypass() -> None:
    contract = build_boundary_contract()
    contract["operator_review_bypass_allowed"] = True
    contract["model_invocation_allowed"] = True

    errors = validate_boundary_contract(contract)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_validation_detects_missing_prohibition() -> None:
    contract = build_boundary_contract()
    contract["forbidden_capabilities"].remove("real_execution")

    errors = validate_boundary_contract(contract)

    assert (
        "missing_forbidden_capability:real_execution"
        in errors
    )


def test_builder_returns_independent_values() -> None:
    first = build_boundary_contract()
    second = build_boundary_contract()
    changed = deepcopy(first)

    changed["allowed_inputs"].append("unexpected_input")
    changed["forbidden_capabilities"].clear()

    assert "unexpected_input" not in second["allowed_inputs"]
    assert second["forbidden_capabilities"]