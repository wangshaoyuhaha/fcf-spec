from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping


REQUIRED_COMPLETION_ENTRY_KEYS: List[str] = [
    "app_id",
    "status",
    "branch",
    "main_merge_commit",
    "final_branch_commit",
    "final_current_state_commit",
    "final_current_state_file",
    "validation",
    "git_status",
    "origin_main",
    "tag",
    "release",
    "deploy",
]

ALLOWED_COMPLETION_STATUS: List[str] = [
    "completed",
    "merged",
    "archived",
]

FORBIDDEN_RELEASE_VALUES: List[str] = [
    "tag",
    "release",
    "deploy",
]


@dataclass(frozen=True)
class CompletionIndexValidationResult:
    record_id: str
    status: str
    missing_keys: List[str]
    invalid_values: List[str]


@dataclass(frozen=True)
class CompletionIndexDuplicateResult:
    status: str
    duplicate_app_ids: List[str]
    duplicate_final_state_files: List[str]


def normalize_text(value: object) -> str:
    return str(value).strip().strip("`")


def normalize_status(value: object) -> str:
    return normalize_text(value).lower().replace("-", "_").replace(" ", "_")


def find_missing_keys(record: Mapping[str, object], required_keys: Iterable[str]) -> List[str]:
    return [key for key in required_keys if key not in record]


def validate_completion_status(value: object) -> bool:
    return normalize_status(value) in ALLOWED_COMPLETION_STATUS


def validate_no_tag_release_deploy(record: Mapping[str, object]) -> List[str]:
    invalid: List[str] = []
    for key in FORBIDDEN_RELEASE_VALUES:
        if key in record and normalize_status(record[key]) not in {"none", "no", "false"}:
            invalid.append(f"{key}:MUST_BE_NONE")
    return invalid


def validate_commit_field(value: object) -> bool:
    text = normalize_text(value).lower()
    parts = text.split()
    if not parts:
        return False
    commit = parts[0]
    return 7 <= len(commit) <= 40 and all(char in "0123456789abcdef" for char in commit)


def validate_completion_index_entry(record: Mapping[str, object]) -> CompletionIndexValidationResult:
    missing = find_missing_keys(record, REQUIRED_COMPLETION_ENTRY_KEYS)
    invalid: List[str] = []

    if "status" in record and not validate_completion_status(record["status"]):
        invalid.append("status:INVALID")

    for key in ["main_merge_commit", "final_branch_commit", "final_current_state_commit"]:
        if key in record and not validate_commit_field(record[key]):
            invalid.append(f"{key}:INVALID_COMMIT")

    if "final_current_state_file" in record:
        file_name = normalize_text(record["final_current_state_file"])
        if not file_name.startswith("FCF_CURRENT_STATE_") or not file_name.endswith(".md"):
            invalid.append("final_current_state_file:INVALID_NAME")

    if "git_status" in record and normalize_status(record["git_status"]) != "clean":
        invalid.append("git_status:MUST_BE_CLEAN")

    if "origin_main" in record and normalize_status(record["origin_main"]) != "synced":
        invalid.append("origin_main:MUST_BE_SYNCED")

    invalid.extend(validate_no_tag_release_deploy(record))

    status = "PASS" if not missing and not invalid else "BLOCK"

    return CompletionIndexValidationResult(
        record_id=normalize_text(record.get("app_id", "UNKNOWN_APP")),
        status=status,
        missing_keys=missing,
        invalid_values=invalid,
    )


def assert_completion_index_entry_pass(result: CompletionIndexValidationResult) -> None:
    if result.status != "PASS":
        missing = ",".join(result.missing_keys)
        invalid = ",".join(result.invalid_values)
        raise ValueError(
            f"CONTROL_CENTER_COMPLETION_INDEX_ENTRY_FAILED:"
            f"{result.record_id}:missing={missing}:invalid={invalid}"
        )


def find_duplicate_values(records: Iterable[Mapping[str, object]], field_name: str) -> List[str]:
    seen = set()
    duplicates = set()

    for record in records:
        if field_name not in record:
            continue

        value = normalize_text(record[field_name])
        if not value:
            continue

        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return sorted(duplicates)


def validate_completion_index_uniqueness(records: Iterable[Mapping[str, object]]) -> CompletionIndexDuplicateResult:
    record_list = list(records)
    duplicate_app_ids = find_duplicate_values(record_list, "app_id")
    duplicate_final_state_files = find_duplicate_values(record_list, "final_current_state_file")

    status = "PASS" if not duplicate_app_ids and not duplicate_final_state_files else "BLOCK"

    return CompletionIndexDuplicateResult(
        status=status,
        duplicate_app_ids=duplicate_app_ids,
        duplicate_final_state_files=duplicate_final_state_files,
    )


def assert_completion_index_uniqueness_pass(result: CompletionIndexDuplicateResult) -> None:
    if result.status != "PASS":
        duplicate_apps = ",".join(result.duplicate_app_ids)
        duplicate_files = ",".join(result.duplicate_final_state_files)
        raise ValueError(
            f"CONTROL_CENTER_COMPLETION_INDEX_DUPLICATE_FAILED:"
            f"app_ids={duplicate_apps}:final_state_files={duplicate_files}"
        )