"""D1 deterministic consumer binding contract."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

APP_ID = "AI-COMPREHENSIVE-REPORT-CONSUMER-BINDING-APP-1"
STAGE = "D1"
CONTRACT_VERSION = "1.0.0"

SOURCE_APP_ID = "AI-COMPREHENSIVE-REPORT-INTEGRATION-APP-1"
SOURCE_PACKAGE = "apps.ai_comprehensive_report_integration_app_1"
SOURCE_PACKET_TYPE = (
    "comprehensive_report_integration_full_chain_closeout_packet"
)

REQUIRED_CONSUMERS = (
    "OPERATOR-REVIEW-APP-1",
    "UI-APP-1",
    "REPORT-ARCHIVE-APP-1",
)

REQUIRED_IDENTITY_FIELDS = (
    "source_app_id",
    "source_module",
    "source_artifact_type",
    "source_artifact_ref",
    "source_artifact_version",
    "source_sha256",
    "correlation_id",
)

REQUIRED_CONTENT_FIELDS = (
    "source_statements",
    "original_conclusions",
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
)

FORBIDDEN_BEHAVIORS = (
    "SOURCE_MUTATION",
    "SEMANTIC_REWRITE",
    "RISK_SUPPRESSION",
    "COUNTEREVIDENCE_SUPPRESSION",
    "UNCERTAINTY_SUPPRESSION",
    "AUTOMATIC_OPERATOR_APPROVAL",
    "AUTOMATIC_ARCHIVE_APPROVAL",
    "AUTOMATIC_ARCHIVE_EXECUTION",
    "RUNTIME_MODEL_INVOCATION",
    "PROMPT_EXECUTION",
    "AUTOMATIC_MODEL_ROUTING",
    "REAL_EXECUTION",
)


def build_consumer_binding_contract() -> dict[str, Any]:
    """Return the immutable D1 consumer binding contract."""

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "contract_version": CONTRACT_VERSION,
        "source_app_id": SOURCE_APP_ID,
        "source_package": SOURCE_PACKAGE,
        "source_packet_type": SOURCE_PACKET_TYPE,
        "required_consumers": list(REQUIRED_CONSUMERS),
        "required_identity_fields": list(REQUIRED_IDENTITY_FIELDS),
        "required_content_fields": list(REQUIRED_CONTENT_FIELDS),
        "forbidden_behaviors": list(FORBIDDEN_BEHAVIORS),
        "binding_mode": "READ_ONLY_DETERMINISTIC_ADAPTER",
        "operator_review_required": True,
        "registered_artifact_required": True,
        "manual_archive_authorization_required": True,
        "paper_only": True,
        "local_only": True,
        "sidecar_only": True,
        "core_mutation_allowed": False,
        "source_mutation_allowed": False,
        "semantic_rewrite_allowed": False,
        "risk_suppression_allowed": False,
        "automatic_approval_allowed": False,
        "automatic_archive_allowed": False,
        "runtime_model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_routing_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deployment_allowed": False,
    }


def validate_consumer_binding_contract(
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the D1 contract and fail closed on drift."""

    expected = build_consumer_binding_contract()
    errors: list[str] = []

    for field in (
        "app_id",
        "stage",
        "contract_version",
        "source_app_id",
        "source_package",
        "source_packet_type",
        "binding_mode",
    ):
        if contract.get(field) != expected[field]:
            errors.append(f"INVALID_{field.upper()}")

    for field in (
        "required_consumers",
        "required_identity_fields",
        "required_content_fields",
        "forbidden_behaviors",
    ):
        if contract.get(field) != expected[field]:
            errors.append(f"INVALID_{field.upper()}")

    true_fields = (
        "operator_review_required",
        "registered_artifact_required",
        "manual_archive_authorization_required",
        "paper_only",
        "local_only",
        "sidecar_only",
    )

    for field in true_fields:
        if contract.get(field) is not True:
            errors.append(f"REQUIRED_{field.upper()}")

    false_fields = (
        "core_mutation_allowed",
        "source_mutation_allowed",
        "semantic_rewrite_allowed",
        "risk_suppression_allowed",
        "automatic_approval_allowed",
        "automatic_archive_allowed",
        "runtime_model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deployment_allowed",
    )

    for field in false_fields:
        if contract.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "contract": deepcopy(dict(contract)),
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
