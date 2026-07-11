from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_consumer_binding_app_1 import (
    APP_ID,
    CONTRACT_VERSION,
    REQUIRED_CONSUMERS,
    REQUIRED_CONTENT_FIELDS,
    REQUIRED_IDENTITY_FIELDS,
    SOURCE_APP_ID,
    SOURCE_PACKAGE,
    build_consumer_binding_contract,
    validate_consumer_binding_contract,
)


def test_d1_contract_identity() -> None:
    contract = build_consumer_binding_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage"] == "D1"
    assert contract["contract_version"] == CONTRACT_VERSION
    assert contract["source_app_id"] == SOURCE_APP_ID
    assert contract["source_package"] == SOURCE_PACKAGE


def test_d1_requires_all_consumers() -> None:
    contract = build_consumer_binding_contract()

    assert tuple(contract["required_consumers"]) == REQUIRED_CONSUMERS
    assert contract["required_consumers"] == [
        "OPERATOR-REVIEW-APP-1",
        "UI-APP-1",
        "REPORT-ARCHIVE-APP-1",
    ]


def test_d1_requires_identity_preservation() -> None:
    contract = build_consumer_binding_contract()

    assert tuple(
        contract["required_identity_fields"]
    ) == REQUIRED_IDENTITY_FIELDS

    assert "source_sha256" in contract["required_identity_fields"]
    assert "correlation_id" in contract["required_identity_fields"]


def test_d1_requires_content_preservation() -> None:
    contract = build_consumer_binding_contract()

    assert tuple(
        contract["required_content_fields"]
    ) == REQUIRED_CONTENT_FIELDS

    assert "risk_flags" in contract["required_content_fields"]
    assert "counterevidence" in contract["required_content_fields"]
    assert "uncertainty_states" in contract["required_content_fields"]


def test_d1_binding_is_read_only_and_deterministic() -> None:
    contract = build_consumer_binding_contract()

    assert contract["binding_mode"] == "READ_ONLY_DETERMINISTIC_ADAPTER"
    assert contract["operator_review_required"] is True
    assert contract["registered_artifact_required"] is True
    assert contract["manual_archive_authorization_required"] is True


def test_d1_blocks_mutation_and_suppression() -> None:
    contract = build_consumer_binding_contract()

    assert contract["core_mutation_allowed"] is False
    assert contract["source_mutation_allowed"] is False
    assert contract["semantic_rewrite_allowed"] is False
    assert contract["risk_suppression_allowed"] is False


def test_d1_blocks_runtime_and_real_execution() -> None:
    contract = build_consumer_binding_contract()

    assert contract["runtime_model_invocation_allowed"] is False
    assert contract["prompt_execution_allowed"] is False
    assert contract["automatic_routing_allowed"] is False
    assert contract["real_execution_allowed"] is False


def test_d1_blocks_release_actions() -> None:
    contract = build_consumer_binding_contract()

    assert contract["tag_allowed"] is False
    assert contract["release_allowed"] is False
    assert contract["deployment_allowed"] is False


def test_d1_valid_contract_passes() -> None:
    contract = build_consumer_binding_contract()
    result = validate_consumer_binding_contract(contract)

    assert result["ok"] is True
    assert result["errors"] == []


def test_d1_rejects_missing_consumer() -> None:
    contract = build_consumer_binding_contract()
    contract["required_consumers"].remove("UI-APP-1")

    result = validate_consumer_binding_contract(contract)

    assert result["ok"] is False
    assert "INVALID_REQUIRED_CONSUMERS" in result["errors"]


def test_d1_rejects_automatic_approval() -> None:
    contract = build_consumer_binding_contract()
    contract["automatic_approval_allowed"] = True

    result = validate_consumer_binding_contract(contract)

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_APPROVAL_ALLOWED" in result["errors"]


def test_d1_does_not_mutate_contract() -> None:
    contract = build_consumer_binding_contract()
    original = deepcopy(contract)

    validate_consumer_binding_contract(contract)

    assert contract == original
