from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping


REQUIRED_STAGE_KEYS: List[str] = [
    "app_id",
    "stage_id",
    "status",
    "branch",
    "commit",
    "validation",
    "git_status",
    "safety_boundary",
]

REQUIRED_FINAL_STATE_KEYS: List[str] = [
    "app_id",
    "latest_main_commit",
    "main_merge_commit",
    "final_branch_commit",
    "validation",
    "git_status",
    "origin_main",
    "tag",
    "release",
    "deploy",
]

ALLOWED_STATUS_VALUES: List[str] = [
    "planned",
    "in_progress",
    "completed",
    "merged",
    "archived",
    "blocked",
]

REQUIRED_SAFETY_FLAGS: Dict[str, bool] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "real_trading_allowed": False,
    "broker_api_allowed": False,
    "exchange_api_allowed": False,
    "api_key_allowed": False,
    "buy_button_allowed": False,
    "sell_button_allowed": False,
    "order_button_allowed": False,
    "tag_allowed": False,
    "release_allowed": False,
    "deploy_allowed": False,
}


@dataclass(frozen=True)
class SchemaConsistencyResult:
    record_id: str
    schema_name: str
    status: str
    missing_keys: List[str]
    invalid_values: List[str]


def find_missing_keys(record: Mapping[str, object], required_keys: Iterable[str]) -> List[str]:
    return [key for key in required_keys if key not in record]


def validate_status_value(value: object) -> bool:
    return isinstance(value, str) and value in ALLOWED_STATUS_VALUES


def validate_safety_boundary(boundary: Mapping[str, object]) -> List[str]:
    invalid: List[str] = []
    for key, expected in REQUIRED_SAFETY_FLAGS.items():
        if key not in boundary:
            invalid.append(f"{key}:MISSING")
        elif boundary[key] is not expected:
            invalid.append(f"{key}:EXPECTED_{str(expected).upper()}")
    return invalid


def validate_stage_record(record: Mapping[str, object]) -> SchemaConsistencyResult:
    missing = find_missing_keys(record, REQUIRED_STAGE_KEYS)
    invalid: List[str] = []

    if "status" in record and not validate_status_value(record["status"]):
        invalid.append("status:INVALID")

    boundary = record.get("safety_boundary")
    if "safety_boundary" in record:
        if not isinstance(boundary, Mapping):
            invalid.append("safety_boundary:INVALID_TYPE")
        else:
            invalid.extend(validate_safety_boundary(boundary))

    status = "PASS" if not missing and not invalid else "BLOCK"

    return SchemaConsistencyResult(
        record_id=str(record.get("stage_id", "UNKNOWN_STAGE")),
        schema_name="STAGE_RECORD",
        status=status,
        missing_keys=missing,
        invalid_values=invalid,
    )


def validate_final_state_record(record: Mapping[str, object]) -> SchemaConsistencyResult:
    missing = find_missing_keys(record, REQUIRED_FINAL_STATE_KEYS)
    invalid: List[str] = []

    for key in ["tag", "release", "deploy"]:
        if key in record and str(record[key]).lower() not in {"none", "false", "no"}:
            invalid.append(f"{key}:MUST_BE_NONE")

    status = "PASS" if not missing and not invalid else "BLOCK"

    return SchemaConsistencyResult(
        record_id=str(record.get("app_id", "UNKNOWN_APP")),
        schema_name="FINAL_STATE_RECORD",
        status=status,
        missing_keys=missing,
        invalid_values=invalid,
    )


def assert_schema_result_pass(result: SchemaConsistencyResult) -> None:
    if result.status != "PASS":
        missing = ",".join(result.missing_keys)
        invalid = ",".join(result.invalid_values)
        raise ValueError(
            f"CONTROL_CENTER_SCHEMA_CONSISTENCY_FAILED:"
            f"{result.schema_name}:{result.record_id}:missing={missing}:invalid={invalid}"
        )