from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


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

DEFAULT_GOVERNANCE_SOURCE_PATTERNS: List[str] = [
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
    "FCF_CURRENT_STATE_*.md",
]


@dataclass(frozen=True)
class SchemaConsistencyResult:
    record_id: str
    schema_name: str
    status: str
    missing_keys: List[str]
    invalid_values: List[str]


@dataclass(frozen=True)
class GovernanceSourceRecord:
    path: str
    source_kind: str
    exists: bool
    utf8_status: str
    extracted_fields: Dict[str, str]


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


def classify_governance_source(path: str | Path) -> str:
    name = Path(path).name
    normalized = Path(path).as_posix()

    if normalized == "docs/FCF_PROJECT_CONTROL_CENTER.md":
        return "CONTROL_CENTER"
    if name == "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md":
        return "BACKEND_HANDOFF"
    if name == "FCF_NEW_WINDOW_CHAT_PROMPT.md":
        return "NEW_WINDOW_PROMPT"
    if name.startswith("FCF_CURRENT_STATE_") and name.endswith(".md"):
        return "FINAL_CURRENT_STATE"
    return "GOVERNANCE_DOCUMENT"


def read_utf8_status(path: str | Path) -> str:
    target = Path(path)
    try:
        target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "UTF8_DECODE_ERROR"
    except FileNotFoundError:
        return "MISSING"
    return "OK"


def extract_markdown_key_values(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        line = line.lstrip("-").strip()

        match = re.match(r"^([A-Za-z][A-Za-z0-9_\- ]{1,80})\s*:\s*(.+)$", line)
        if not match:
            continue

        key = match.group(1).strip().lower().replace(" ", "_").replace("-", "_")
        value = match.group(2).strip().strip("`")
        fields[key] = value

    return fields


def load_governance_source(path: str | Path) -> GovernanceSourceRecord:
    target = Path(path)
    status = read_utf8_status(target)
    fields: Dict[str, str] = {}

    if status == "OK":
        fields = extract_markdown_key_values(target.read_text(encoding="utf-8"))

    return GovernanceSourceRecord(
        path=target.as_posix(),
        source_kind=classify_governance_source(target),
        exists=target.exists(),
        utf8_status=status,
        extracted_fields=fields,
    )


def discover_governance_sources(root: str | Path = ".") -> List[str]:
    base = Path(root)
    discovered: List[str] = []

    for pattern in DEFAULT_GOVERNANCE_SOURCE_PATTERNS:
        if "*" in pattern:
            for item in base.glob(pattern):
                if item.is_file():
                    discovered.append(item.relative_to(base).as_posix())
        else:
            discovered.append(Path(pattern).as_posix())

    unique: List[str] = []
    seen = set()
    for item in discovered:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return sorted(unique)


def load_governance_sources(root: str | Path = ".") -> List[GovernanceSourceRecord]:
    base = Path(root)
    return [load_governance_source(base / relative_path) for relative_path in discover_governance_sources(base)]


def summarize_governance_sources(records: Iterable[GovernanceSourceRecord]) -> Dict[str, int]:
    summary: Dict[str, int] = {}

    for record in records:
        key = f"{record.source_kind}:{record.utf8_status}"
        summary[key] = summary.get(key, 0) + 1

    return summary


def assert_governance_sources_readable(records: Iterable[GovernanceSourceRecord]) -> None:
    bad = [record for record in records if record.utf8_status != "OK"]
    if bad:
        details = "; ".join(f"{record.path}={record.utf8_status}" for record in sorted(bad, key=lambda item: item.path))
        raise ValueError(f"CONTROL_CENTER_SCHEMA_SOURCE_READ_FAILED: {details}")