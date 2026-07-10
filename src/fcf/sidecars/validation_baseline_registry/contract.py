"""Contract for VALIDATION-BASELINE-REGISTRY-APP-1 D1."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

VALIDATION_BASELINE_REGISTRY_APP_ID = "VALIDATION-BASELINE-REGISTRY-APP-1"

ALLOWED_BASELINE_STATUSES = (
    "REGISTERED",
    "VERIFIED",
    "INCOMPLETE",
    "STALE",
    "UNRESOLVED",
)

REQUIRED_BASELINE_FIELDS = (
    "validation_id",
    "command",
    "result",
    "pass_count",
    "git_branch",
    "git_head",
    "git_status",
    "origin_status",
)


def build_validation_baseline_contract() -> Dict[str, Any]:
    """Build the read-only validation baseline registry contract."""

    return {
        "app_id": VALIDATION_BASELINE_REGISTRY_APP_ID,
        "stage": "D1",
        "contract_type": "validation_baseline_registry_contract",
        "allowed_baseline_statuses": list(ALLOWED_BASELINE_STATUSES),
        "required_baseline_fields": list(REQUIRED_BASELINE_FIELDS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "operator_review_required": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
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


def validate_baseline_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one baseline record without mutating or repairing it."""

    issues: List[str] = []

    for field in REQUIRED_BASELINE_FIELDS:
        if field not in record or record.get(field) in ("", None):
            issues.append(f"MISSING_{field.upper()}")

    status = record.get("baseline_status", "REGISTERED")
    if status not in ALLOWED_BASELINE_STATUSES:
        issues.append("UNSUPPORTED_BASELINE_STATUS")

    pass_count = record.get("pass_count")
    if pass_count is not None and not isinstance(pass_count, int):
        issues.append("PASS_COUNT_NOT_INTEGER")

    if record.get("validation_result_fabrication_allowed") is True:
        issues.append("VALIDATION_RESULT_FABRICATION_NOT_ALLOWED")
    if record.get("pass_count_fabrication_allowed") is True:
        issues.append("PASS_COUNT_FABRICATION_NOT_ALLOWED")
    if record.get("auto_pass_allowed") is True:
        issues.append("AUTO_PASS_NOT_ALLOWED")
    if record.get("source_artifact_mutation_allowed") is True:
        issues.append("SOURCE_ARTIFACT_MUTATION_NOT_ALLOWED")

    if issues:
        result_status = "UNRESOLVED"
    elif status in ("INCOMPLETE", "STALE", "UNRESOLVED"):
        result_status = status
    elif record.get("result") == "PASS":
        result_status = "VERIFIED"
    else:
        result_status = "REGISTERED"

    return {
        "valid": not issues,
        "result_status": result_status,
        "issues": issues,
        "read_only": True,
        "index_only": True,
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
    }


def build_validation_baseline_index(
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only validation baseline index."""

    indexed_records: List[Dict[str, Any]] = []
    counts = {
        "VERIFIED": 0,
        "REGISTERED": 0,
        "INCOMPLETE": 0,
        "STALE": 0,
        "UNRESOLVED": 0,
    }

    for record in records:
        validation = validate_baseline_record(record)
        result_status = validation["result_status"]
        if result_status not in counts:
            result_status = "UNRESOLVED"
        counts[result_status] += 1

        indexed_records.append(
            {
                "validation_id": record.get("validation_id"),
                "command": record.get("command"),
                "result": record.get("result"),
                "pass_count": record.get("pass_count"),
                "git_branch": record.get("git_branch"),
                "git_head": record.get("git_head"),
                "git_status": record.get("git_status"),
                "origin_status": record.get("origin_status"),
                "baseline_status": record.get("baseline_status", "REGISTERED"),
                "validation": validation,
                "read_only": True,
                "validation_result_fabrication_allowed": False,
                "pass_count_fabrication_allowed": False,
                "source_artifact_mutation_allowed": False,
                "evidence_backfill_allowed": False,
            }
        )

    if counts["UNRESOLVED"]:
        index_status = "UNRESOLVED"
    elif counts["STALE"]:
        index_status = "STALE"
    elif counts["INCOMPLETE"]:
        index_status = "INCOMPLETE"
    elif counts["VERIFIED"]:
        index_status = "VERIFIED"
    else:
        index_status = "REGISTERED"

    return {
        "app_id": VALIDATION_BASELINE_REGISTRY_APP_ID,
        "stage": "D1",
        "index_status": index_status,
        "record_count": len(indexed_records),
        "status_counts": counts,
        "records": indexed_records,
        "read_only": True,
        "index_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "auto_pass_allowed": False,
    }
