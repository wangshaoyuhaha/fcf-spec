"""Tests for AI prompt and model version registry boundary."""

from fcf.sidecars.ai_prompt_model_version_registry import (
    APP_ID,
    CONTRACT_VERSION,
    build_contract,
    validate_contract,
)


def test_contract_is_valid() -> None:
    contract = build_contract()

    assert validate_contract(contract) == []
    assert contract["app_id"] == APP_ID
    assert contract["contract_version"] == CONTRACT_VERSION
    assert contract["output_kind"] == (
        "PAPER_ONLY_VERSION_REGISTRY_RECORDS"
    )


def test_safety_boundaries_are_locked() -> None:
    boundaries = build_contract()["boundaries"]

    assert boundaries["paper_only"] is True
    assert boundaries["local_only"] is True
    assert boundaries["read_only"] is True
    assert boundaries["sidecar_only"] is True
    assert boundaries["operator_review_required"] is True

    assert boundaries["core_mutation_allowed"] is False
    assert boundaries["p48_core_expansion_allowed"] is False
    assert boundaries["model_execution_allowed"] is False
    assert boundaries["automatic_activation_allowed"] is False
    assert boundaries["automatic_promotion_allowed"] is False
    assert boundaries["automatic_rollback_allowed"] is False
    assert boundaries["credential_storage_allowed"] is False
    assert boundaries["api_key_access_allowed"] is False
    assert boundaries["real_trading_allowed"] is False
    assert boundaries["real_execution_allowed"] is False


def test_required_version_fields_are_locked() -> None:
    fields = set(build_contract()["required_version_fields"])

    assert fields == {
        "registry_entry_id",
        "prompt_version",
        "model_version",
        "contract_version",
        "registry_version",
    }


def test_required_trace_fields_are_locked() -> None:
    fields = set(build_contract()["required_trace_fields"])

    assert fields == {
        "correlation_id",
        "research_run_id",
        "source_artifact_ids",
        "validation_baseline_id",
    }


def test_version_statuses_do_not_allow_auto_activation() -> None:
    statuses = set(build_contract()["version_statuses"])

    assert "REVIEW_REQUIRED" in statuses
    assert "APPROVED_FOR_PAPER_RESEARCH" in statuses
    assert "BLOCKED" in statuses
    assert "AUTO_ACTIVE" not in statuses
    assert "PRODUCTION_DEPLOYED" not in statuses


def test_execution_capabilities_are_forbidden() -> None:
    forbidden = set(build_contract()["forbidden_capabilities"])

    assert {
        "MODEL_EXECUTION",
        "PROMPT_AUTO_DEPLOY",
        "MODEL_AUTO_DEPLOY",
        "AUTOMATIC_ACTIVATION",
        "AUTOMATIC_PROMOTION",
        "AUTOMATIC_ROLLBACK",
        "BROKER_CONNECTION",
        "EXCHANGE_CONNECTION",
        "API_KEY_ACCESS",
        "BUY",
        "SELL",
        "ORDER",
        "EXECUTE",
        "OPERATOR_REVIEW_BYPASS",
    }.issubset(forbidden)


def test_invalid_model_execution_boundary_is_rejected() -> None:
    contract = build_contract()
    contract["boundaries"]["model_execution_allowed"] = True

    assert "invalid_boundary:model_execution_allowed" in (
        validate_contract(contract)
    )


def test_missing_prompt_version_field_is_rejected() -> None:
    contract = build_contract()
    contract["required_version_fields"].remove("prompt_version")

    assert "missing_version_field:prompt_version" in (
        validate_contract(contract)
    )


def test_review_and_archive_are_mandatory() -> None:
    contract = build_contract()

    assert contract["human_review_required"] is True
    assert contract["archive_required"] is True
