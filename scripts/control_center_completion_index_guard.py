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

from pathlib import Path
from typing import Dict
import re


COMPLETION_SOURCE_PATTERNS: List[str] = [
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_CURRENT_STATE_*.md",
]


@dataclass(frozen=True)
class CompletionIndexSourceRecord:
    path: str
    source_kind: str
    exists: bool
    utf8_status: str
    extracted_fields: Dict[str, str]


def classify_completion_source(path: str | Path) -> str:
    name = Path(path).name
    normalized = Path(path).as_posix()

    if normalized == "docs/FCF_PROJECT_CONTROL_CENTER.md" or normalized.endswith("/docs/FCF_PROJECT_CONTROL_CENTER.md"):
        return "CONTROL_CENTER"
    if name.startswith("FCF_CURRENT_STATE_") and name.endswith(".md"):
        return "FINAL_CURRENT_STATE"
    return "GOVERNANCE_DOCUMENT"


def read_completion_source_utf8_status(path: str | Path) -> str:
    target = Path(path)
    try:
        target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "UTF8_DECODE_ERROR"
    except FileNotFoundError:
        return "MISSING"
    return "OK"


def normalize_completion_field_name(name: str) -> str:
    normalized = name.strip().lower()
    normalized = normalized.replace("`", "")
    normalized = normalized.replace("/", "_")
    normalized = normalized.replace("-", "_")
    normalized = normalized.replace(" ", "_")
    normalized = re.sub(r"[^a-z0-9_]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def extract_completion_key_values(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        line = line.lstrip("-").strip()
        match = re.match(r"^([A-Za-z][A-Za-z0-9_\- /]{1,100})\s*:\s*(.+)$", line)
        if not match:
            continue

        key = normalize_completion_field_name(match.group(1))
        value = match.group(2).strip().strip("`")
        fields[key] = value

    return fields


def discover_completion_sources(root: str | Path = ".") -> List[str]:
    base = Path(root)
    discovered: List[str] = []

    for pattern in COMPLETION_SOURCE_PATTERNS:
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


def load_completion_source(path: str | Path) -> CompletionIndexSourceRecord:
    target = Path(path)
    status = read_completion_source_utf8_status(target)
    fields: Dict[str, str] = {}

    if status == "OK":
        fields = extract_completion_key_values(target.read_text(encoding="utf-8"))

    return CompletionIndexSourceRecord(
        path=target.as_posix(),
        source_kind=classify_completion_source(target),
        exists=target.exists(),
        utf8_status=status,
        extracted_fields=fields,
    )


def load_completion_sources(root: str | Path = ".") -> List[CompletionIndexSourceRecord]:
    base = Path(root)
    return [load_completion_source(base / relative_path) for relative_path in discover_completion_sources(base)]


def summarize_completion_sources(records: Iterable[CompletionIndexSourceRecord]) -> Dict[str, int]:
    summary: Dict[str, int] = {}

    for record in records:
        key = f"{record.source_kind}:{record.utf8_status}"
        summary[key] = summary.get(key, 0) + 1

    return summary


def assert_completion_sources_readable(records: Iterable[CompletionIndexSourceRecord]) -> None:
    bad = [record for record in records if record.utf8_status != "OK"]
    if bad:
        details = "; ".join(f"{record.path}={record.utf8_status}" for record in sorted(bad, key=lambda item: item.path))
        raise ValueError(f"CONTROL_CENTER_COMPLETION_INDEX_SOURCE_READ_FAILED:{details}")


COMPLETION_FIELD_ALIASES: Dict[str, str] = {
    "app": "app_id",
    "app_name": "app_id",
    "application": "app_id",
    "branch_name": "branch",
    "latest_main_commit": "final_current_state_commit",
    "latest_main": "final_current_state_commit",
    "latest_head": "final_current_state_commit",
    "latest_head_commit": "final_current_state_commit",
    "head": "final_current_state_commit",
    "head_commit": "final_current_state_commit",
    "current_latest_main_commit": "final_current_state_commit",
    "final_current_state_documentation_commit": "final_current_state_commit",
    "final_current_state_commit": "final_current_state_commit",
    "main_merge": "main_merge_commit",
    "merge_commit": "main_merge_commit",
    "main_merge_commit": "main_merge_commit",
    "d6_commit": "final_branch_commit",
    "d6_final_branch_commit": "final_branch_commit",
    "final_branch": "final_branch_commit",
    "final_branch_commit": "final_branch_commit",
    "final_commit": "final_branch_commit",
    "final_current_state_file": "final_current_state_file",
    "final_current_state": "final_current_state_file",
    "current_state_file": "final_current_state_file",
    "pytest": "validation",
    "test_result": "validation",
    "validation_baseline": "validation",
    "origin": "origin_main",
    "origin_main": "origin_main",
    "origin_main_status": "origin_main",
    "origin_main_synced": "origin_main",
    "gitstatus": "git_status",
    "git_status": "git_status",
    "worktree": "git_status",
    "worktree_status": "git_status",
    "tag_status": "tag",
    "release_status": "release",
    "deploy_status": "deploy",
}


def canonical_completion_field_name(name: str) -> str:
    normalized = normalize_completion_field_name(name)
    return COMPLETION_FIELD_ALIASES.get(normalized, normalized)


def canonicalize_completion_fields(fields: Mapping[str, object]) -> Dict[str, str]:
    canonical: Dict[str, str] = {}
    for key, value in fields.items():
        canonical[canonical_completion_field_name(str(key))] = normalize_text(value)
    return canonical


def extract_commit_hash(value: object) -> str:
    text = normalize_text(value).lower()
    match = re.search(r"\b[0-9a-f]{7,40}\b", text)
    if match:
        return match.group(0)
    return text


def infer_app_id_from_final_state_file(path: str) -> str:
    name = Path(path).name
    if name.startswith("FCF_CURRENT_STATE_") and name.endswith(".md"):
        body = name[len("FCF_CURRENT_STATE_") : -len(".md")]
        if body.endswith("_FINAL"):
            body = body[: -len("_FINAL")]
        return body.replace("_", "-")
    return "UNKNOWN_APP"


def normalize_completion_status_text(value: object) -> str:
    text = normalize_status(value)
    if text in {"complete", "completed"}:
        return "completed"
    if text in {"merged", "merged_into_main"}:
        return "merged"
    if text in {"archived", "final", "finalized"}:
        return "archived"
    if "completed" in text:
        return "completed"
    if "merged" in text:
        return "merged"
    if "archived" in text:
        return "archived"
    return text


def normalize_completion_git_status(value: object) -> str:
    text = normalize_status(value)
    if text in {"blank", "empty", "clean"} or "clean" in text:
        return "clean"
    return text


def normalize_completion_origin_status(value: object) -> str:
    text = normalize_status(value)
    if text in {"synced", "sync", "up_to_date", "up_to-date"} or "synced" in text or "up_to_date" in text:
        return "synced"
    return text


def normalize_none_record(value: object) -> str:
    text = normalize_status(value)
    if text in {"none", "no", "false", "not_detected", "not_applicable", "n_a"}:
        return "none"
    return text


def build_completion_entry_from_source(record: CompletionIndexSourceRecord) -> Dict[str, str]:
    fields = canonicalize_completion_fields(record.extracted_fields)
    entry: Dict[str, str] = {}

    app_id = fields.get("app_id")
    if not app_id:
        app_id = infer_app_id_from_final_state_file(record.path)
    entry["app_id"] = app_id

    entry["status"] = normalize_completion_status_text(fields.get("status", "completed"))
    entry["branch"] = fields.get("branch", "main")

    if "main_merge_commit" in fields:
        entry["main_merge_commit"] = extract_commit_hash(fields["main_merge_commit"])

    if "final_branch_commit" in fields:
        entry["final_branch_commit"] = extract_commit_hash(fields["final_branch_commit"])

    if "final_current_state_commit" in fields:
        entry["final_current_state_commit"] = extract_commit_hash(fields["final_current_state_commit"])

    entry["final_current_state_file"] = fields.get("final_current_state_file", Path(record.path).name)
    entry["validation"] = fields.get("validation", "")
    entry["git_status"] = normalize_completion_git_status(fields.get("git_status", "clean"))
    entry["origin_main"] = normalize_completion_origin_status(fields.get("origin_main", "synced"))
    entry["tag"] = normalize_none_record(fields.get("tag", "none"))
    entry["release"] = normalize_none_record(fields.get("release", "none"))
    entry["deploy"] = normalize_none_record(fields.get("deploy", "none"))

    return entry


def build_completion_entries_from_sources(records: Iterable[CompletionIndexSourceRecord]) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for record in records:
        if record.source_kind != "FINAL_CURRENT_STATE":
            continue
        if record.utf8_status != "OK":
            continue
        entries.append(build_completion_entry_from_source(record))
    return sorted(entries, key=lambda item: item.get("app_id", ""))


def validate_completion_entries_from_sources(records: Iterable[CompletionIndexSourceRecord]) -> List[CompletionIndexValidationResult]:
    entries = build_completion_entries_from_sources(records)
    return [validate_completion_index_entry(entry) for entry in entries]


def assert_completion_entries_from_sources_pass(records: Iterable[CompletionIndexSourceRecord]) -> None:
    entries = build_completion_entries_from_sources(records)
    for result in [validate_completion_index_entry(entry) for entry in entries]:
        assert_completion_index_entry_pass(result)
    assert_completion_index_uniqueness_pass(validate_completion_index_uniqueness(entries))
