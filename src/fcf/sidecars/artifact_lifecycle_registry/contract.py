"""Contract for ARTIFACT-LIFECYCLE-REGISTRY-APP-1 D1."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

ARTIFACT_LIFECYCLE_REGISTRY_APP_ID = "ARTIFACT-LIFECYCLE-REGISTRY-APP-1"

ALLOWED_LIFECYCLE_STATUSES = (
    "REGISTERED",
    "OBSERVED",
    "INCOMPLETE",
    "STALE",
    "UNRESOLVED",
)

REQUIRED_ARTIFACT_FIELDS = (
    "artifact_id",
    "artifact_type",
    "artifact_path",
    "lifecycle_status",
)


def build_lifecycle_registry_contract() -> Dict[str, Any]:
    """Build the read-only lifecycle registry contract."""

    return {
        "app_id": ARTIFACT_LIFECYCLE_REGISTRY_APP_ID,
        "stage": "D1",
        "contract_type": "artifact_lifecycle_registry_contract",
        "allowed_lifecycle_statuses": list(ALLOWED_LIFECYCLE_STATUSES),
        "required_artifact_fields": list(REQUIRED_ARTIFACT_FIELDS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "operator_review_required": True,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "ui_dashboard_panel_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "real_trade_allowed": False,
        "real_execution_allowed": False,
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_allowed": False,
        "wallet_private_key_allowed": False,
        "real_account_allowed": False,
        "real_position_allowed": False,
        "buy_sell_order_allowed": False,
        "auto_position_allowed": False,
        "auto_portfolio_action_allowed": False,
    }


def validate_lifecycle_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one lifecycle record without mutating or repairing it."""

    issues: List[str] = []

    for field in REQUIRED_ARTIFACT_FIELDS:
        if field not in record or record.get(field) in ("", None):
            issues.append(f"MISSING_{field.upper()}")

    status = record.get("lifecycle_status")
    if status not in ALLOWED_LIFECYCLE_STATUSES:
        issues.append("UNSUPPORTED_LIFECYCLE_STATUS")

    forbidden_true_fields = (
        "source_artifact_mutation_allowed",
        "artifact_status_auto_repair_allowed",
        "evidence_backfill_allowed",
        "correlation_id_auto_fill_allowed",
        "placeholder_review_allowed",
        "auto_pass_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
    )

    for field in forbidden_true_fields:
        if record.get(field) is True:
            issues.append(f"{field.upper()}_NOT_ALLOWED")

    if issues:
        result_status = "UNRESOLVED"
    elif status in ("INCOMPLETE", "STALE", "UNRESOLVED"):
        result_status = status
    else:
        result_status = "OBSERVED"

    return {
        "valid": not issues,
        "result_status": result_status,
        "issues": issues,
        "read_only": True,
        "index_only": True,
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
    }


def build_lifecycle_registry_index(
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only lifecycle registry index."""

    indexed_records: List[Dict[str, Any]] = []
    unresolved_count = 0
    stale_count = 0
    incomplete_count = 0

    for record in records:
        validation = validate_lifecycle_record(record)
        status = validation["result_status"]

        if status == "UNRESOLVED":
            unresolved_count += 1
        if status == "STALE":
            stale_count += 1
        if status == "INCOMPLETE":
            incomplete_count += 1

        indexed_records.append(
            {
                "artifact_id": record.get("artifact_id"),
                "artifact_type": record.get("artifact_type"),
                "artifact_path": record.get("artifact_path"),
                "lifecycle_status": record.get("lifecycle_status"),
                "validation": validation,
                "read_only": True,
                "source_artifact_mutation_allowed": False,
                "artifact_status_auto_repair_allowed": False,
                "evidence_backfill_allowed": False,
            }
        )

    if unresolved_count:
        registry_status = "UNRESOLVED"
    elif stale_count:
        registry_status = "STALE"
    elif incomplete_count:
        registry_status = "INCOMPLETE"
    else:
        registry_status = "OBSERVED"

    return {
        "app_id": ARTIFACT_LIFECYCLE_REGISTRY_APP_ID,
        "registry_status": registry_status,
        "records": indexed_records,
        "record_count": len(indexed_records),
        "unresolved_count": unresolved_count,
        "stale_count": stale_count,
        "incomplete_count": incomplete_count,
        "read_only": True,
        "index_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "auto_pass_allowed": False,
    }
