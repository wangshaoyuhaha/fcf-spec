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


@dataclass(frozen=True)
class CompletionIndexMatrixRow:
    app_id: str
    final_current_state_file: str
    entry_present: bool
    validation_status: str
    order_index: int


@dataclass(frozen=True)
class CompletionIndexMatrixReport:
    status: str
    expected_count: int
    actual_count: int
    row_count: int
    missing_app_ids: List[str]
    unexpected_app_ids: List[str]
    duplicate_app_ids: List[str]
    duplicate_final_state_files: List[str]
    rows: List[CompletionIndexMatrixRow]


def normalize_app_id(value: object) -> str:
    return normalize_text(value).upper().replace("_", "-")


def derive_expected_app_ids_from_final_state_files(file_paths: Iterable[str]) -> List[str]:
    app_ids: List[str] = []

    for file_path in file_paths:
        app_id = infer_app_id_from_final_state_file(file_path)
        if app_id != "UNKNOWN_APP":
            app_ids.append(normalize_app_id(app_id))

    return sorted(set(app_ids))


def build_completion_index_matrix(
    entries: Iterable[Mapping[str, object]],
    expected_app_ids: Iterable[str] | None = None,
) -> CompletionIndexMatrixReport:
    entry_list = [dict(entry) for entry in entries]
    normalized_entries: List[Dict[str, str]] = []

    for entry in entry_list:
        normalized_entry = {str(key): normalize_text(value) for key, value in entry.items()}
        if "app_id" in normalized_entry:
            normalized_entry["app_id"] = normalize_app_id(normalized_entry["app_id"])
        normalized_entries.append(normalized_entry)

    actual_app_ids = sorted(set(entry.get("app_id", "") for entry in normalized_entries if entry.get("app_id", "")))

    if expected_app_ids is None:
        expected = actual_app_ids
    else:
        expected = sorted(set(normalize_app_id(app_id) for app_id in expected_app_ids))

    duplicate_result = validate_completion_index_uniqueness(normalized_entries)
    missing_app_ids = sorted(set(expected) - set(actual_app_ids))
    unexpected_app_ids = sorted(set(actual_app_ids) - set(expected))

    rows: List[CompletionIndexMatrixRow] = []
    by_app: Dict[str, Dict[str, str]] = {}

    for entry in normalized_entries:
        app_id = entry.get("app_id", "")
        if app_id and app_id not in by_app:
            by_app[app_id] = entry

    for index, app_id in enumerate(sorted(set(expected) | set(actual_app_ids))):
        entry = by_app.get(app_id)
        if entry is None:
            rows.append(
                CompletionIndexMatrixRow(
                    app_id=app_id,
                    final_current_state_file="",
                    entry_present=False,
                    validation_status="MISSING",
                    order_index=index,
                )
            )
            continue

        validation = validate_completion_index_entry(entry)
        rows.append(
            CompletionIndexMatrixRow(
                app_id=app_id,
                final_current_state_file=entry.get("final_current_state_file", ""),
                entry_present=True,
                validation_status=validation.status,
                order_index=index,
            )
        )

    status = "PASS"
    if (
        missing_app_ids
        or unexpected_app_ids
        or duplicate_result.status != "PASS"
        or any(row.validation_status == "BLOCK" for row in rows)
    ):
        status = "BLOCK"

    return CompletionIndexMatrixReport(
        status=status,
        expected_count=len(expected),
        actual_count=len(actual_app_ids),
        row_count=len(rows),
        missing_app_ids=missing_app_ids,
        unexpected_app_ids=unexpected_app_ids,
        duplicate_app_ids=duplicate_result.duplicate_app_ids,
        duplicate_final_state_files=duplicate_result.duplicate_final_state_files,
        rows=rows,
    )


def assert_completion_index_matrix_pass(report: CompletionIndexMatrixReport) -> None:
    if report.status != "PASS":
        raise ValueError(
            "CONTROL_CENTER_COMPLETION_INDEX_MATRIX_FAILED:"
            f"missing={','.join(report.missing_app_ids)}:"
            f"unexpected={','.join(report.unexpected_app_ids)}:"
            f"duplicate_apps={','.join(report.duplicate_app_ids)}:"
            f"duplicate_files={','.join(report.duplicate_final_state_files)}"
        )


def render_completion_index_matrix_md(report: CompletionIndexMatrixReport) -> str:
    lines: List[str] = [
        "# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D4 Completion Matrix",
        "",
        "## Summary",
        "",
        f"- status: {report.status}",
        f"- expected_count: {report.expected_count}",
        f"- actual_count: {report.actual_count}",
        f"- row_count: {report.row_count}",
        "",
        "## Missing App IDs",
        "",
    ]

    if report.missing_app_ids:
        for app_id in report.missing_app_ids:
            lines.append(f"- {app_id}")
    else:
        lines.append("- none")

    lines.extend(["", "## Unexpected App IDs", ""])

    if report.unexpected_app_ids:
        for app_id in report.unexpected_app_ids:
            lines.append(f"- {app_id}")
    else:
        lines.append("- none")

    lines.extend(["", "## Duplicate App IDs", ""])

    if report.duplicate_app_ids:
        for app_id in report.duplicate_app_ids:
            lines.append(f"- {app_id}")
    else:
        lines.append("- none")

    lines.extend(["", "## Matrix Rows", ""])

    for row in report.rows:
        lines.append(
            f"- {row.order_index}: {row.app_id}: "
            f"entry_present={str(row.entry_present).lower()}: "
            f"validation_status={row.validation_status}: "
            f"file={row.final_current_state_file}"
        )

    lines.append("")
    return "\n".join(lines)


def build_completion_index_matrix_from_sources(records: Iterable[CompletionIndexSourceRecord]) -> CompletionIndexMatrixReport:
    source_list = list(records)
    entries = build_completion_entries_from_sources(source_list)
    expected = derive_expected_app_ids_from_final_state_files(
        record.path for record in source_list if record.source_kind == "FINAL_CURRENT_STATE"
    )
    return build_completion_index_matrix(entries, expected)


@dataclass(frozen=True)
class CompletionIndexGuardPacket:
    stage_id: str
    status: str
    expected_count: int
    actual_count: int
    row_count: int
    missing_count: int
    unexpected_count: int
    duplicate_app_count: int
    duplicate_file_count: int
    invalid_row_count: int
    safety_scope: str
    operator_review_required: bool
    real_execution_allowed: bool
    trade_action_enabled: bool
    tag_allowed: bool
    release_allowed: bool
    deploy_allowed: bool


def build_completion_index_guard_packet(report: CompletionIndexMatrixReport) -> CompletionIndexGuardPacket:
    invalid_row_count = sum(1 for row in report.rows if row.validation_status == "BLOCK")

    return CompletionIndexGuardPacket(
        stage_id="CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1-D5",
        status=report.status,
        expected_count=report.expected_count,
        actual_count=report.actual_count,
        row_count=report.row_count,
        missing_count=len(report.missing_app_ids),
        unexpected_count=len(report.unexpected_app_ids),
        duplicate_app_count=len(report.duplicate_app_ids),
        duplicate_file_count=len(report.duplicate_final_state_files),
        invalid_row_count=invalid_row_count,
        safety_scope="PAPER_ONLY_LOCAL_ONLY_READ_ONLY_SIDECAR_ONLY",
        operator_review_required=True,
        real_execution_allowed=False,
        trade_action_enabled=False,
        tag_allowed=False,
        release_allowed=False,
        deploy_allowed=False,
    )


def assert_completion_index_guard_packet_safe(packet: CompletionIndexGuardPacket) -> None:
    if packet.status == "BLOCK":
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_BLOCKED")
    if packet.missing_count:
        raise ValueError(f"CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_MISSING:{packet.missing_count}")
    if packet.unexpected_count:
        raise ValueError(f"CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_UNEXPECTED:{packet.unexpected_count}")
    if packet.duplicate_app_count:
        raise ValueError(f"CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_DUPLICATE_APP:{packet.duplicate_app_count}")
    if packet.duplicate_file_count:
        raise ValueError(f"CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_DUPLICATE_FILE:{packet.duplicate_file_count}")
    if packet.invalid_row_count:
        raise ValueError(f"CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_INVALID_ROW:{packet.invalid_row_count}")
    if not packet.operator_review_required:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_OPERATOR_REVIEW_REQUIRED")
    if packet.real_execution_allowed:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_REAL_EXECUTION_FORBIDDEN")
    if packet.trade_action_enabled:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_TRADE_ACTION_FORBIDDEN")
    if packet.tag_allowed:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_TAG_FORBIDDEN")
    if packet.release_allowed:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_RELEASE_FORBIDDEN")
    if packet.deploy_allowed:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_DEPLOY_FORBIDDEN")


def render_completion_index_guard_packet_md(packet: CompletionIndexGuardPacket) -> str:
    lines: List[str] = [
        "# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D5 Guard Packet",
        "",
        "## Summary",
        "",
        f"- stage_id: {packet.stage_id}",
        f"- status: {packet.status}",
        f"- expected_count: {packet.expected_count}",
        f"- actual_count: {packet.actual_count}",
        f"- row_count: {packet.row_count}",
        f"- missing_count: {packet.missing_count}",
        f"- unexpected_count: {packet.unexpected_count}",
        f"- duplicate_app_count: {packet.duplicate_app_count}",
        f"- duplicate_file_count: {packet.duplicate_file_count}",
        f"- invalid_row_count: {packet.invalid_row_count}",
        f"- safety_scope: {packet.safety_scope}",
        f"- operator_review_required: {str(packet.operator_review_required).lower()}",
        f"- real_execution_allowed: {str(packet.real_execution_allowed).lower()}",
        f"- trade_action_enabled: {str(packet.trade_action_enabled).lower()}",
        f"- tag_allowed: {str(packet.tag_allowed).lower()}",
        f"- release_allowed: {str(packet.release_allowed).lower()}",
        f"- deploy_allowed: {str(packet.deploy_allowed).lower()}",
        "",
        "## Safety Boundary",
        "",
        "- paper-only",
        "- local-only",
        "- read-only governance validation",
        "- sidecar-only",
        "- operator review required",
        "- no real trading",
        "- no broker API",
        "- no exchange API",
        "- no API key",
        "- no buy button",
        "- no sell button",
        "- no order button",
        "- no tag",
        "- no release",
        "- no deploy",
        "",
    ]

    return "\n".join(lines)


def write_text_utf8_lf(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def write_completion_index_guard_packet_md(packet: CompletionIndexGuardPacket, output_path: str | Path) -> None:
    write_text_utf8_lf(output_path, render_completion_index_guard_packet_md(packet))


def build_completion_index_guard_packet_from_sources(records: Iterable[CompletionIndexSourceRecord]) -> CompletionIndexGuardPacket:
    matrix = build_completion_index_matrix_from_sources(records)
    return build_completion_index_guard_packet(matrix)


@dataclass(frozen=True)
class CompletionIndexCloseout:
    app_id: str
    completed_stages: List[str]
    final_status: str
    validation_required: bool
    merge_ready: bool
    paper_only: bool
    local_only: bool
    read_only: bool
    sidecar_only: bool
    operator_review_required: bool
    no_real_trading: bool
    no_tag_release_deploy: bool


def build_completion_index_closeout() -> CompletionIndexCloseout:
    return CompletionIndexCloseout(
        app_id="CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1",
        completed_stages=[
            "D1 completion index contract",
            "D2 completion source loader",
            "D3 completion entry builder",
            "D4 completion index matrix",
            "D5 completion index guard packet",
            "D6 final workflow handoff and closeout",
        ],
        final_status="READY_FOR_MAIN_MERGE",
        validation_required=True,
        merge_ready=True,
        paper_only=True,
        local_only=True,
        read_only=True,
        sidecar_only=True,
        operator_review_required=True,
        no_real_trading=True,
        no_tag_release_deploy=True,
    )


def assert_completion_index_closeout_safe(closeout: CompletionIndexCloseout) -> None:
    if not closeout.merge_ready:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_NOT_MERGE_READY")
    if not closeout.paper_only:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_PAPER_ONLY_REQUIRED")
    if not closeout.local_only:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_LOCAL_ONLY_REQUIRED")
    if not closeout.read_only:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_READ_ONLY_REQUIRED")
    if not closeout.sidecar_only:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_SIDECAR_ONLY_REQUIRED")
    if not closeout.operator_review_required:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_OPERATOR_REVIEW_REQUIRED")
    if not closeout.no_real_trading:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_REAL_TRADING_FORBIDDEN")
    if not closeout.no_tag_release_deploy:
        raise ValueError("CONTROL_CENTER_COMPLETION_INDEX_CLOSEOUT_TAG_RELEASE_DEPLOY_FORBIDDEN")


def render_completion_index_closeout_md(closeout: CompletionIndexCloseout) -> str:
    lines: List[str] = [
        "# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D6 Final Closeout",
        "",
        "## App",
        "",
        f"- app_id: {closeout.app_id}",
        f"- final_status: {closeout.final_status}",
        f"- validation_required: {str(closeout.validation_required).lower()}",
        f"- merge_ready: {str(closeout.merge_ready).lower()}",
        "",
        "## Completed Stages",
        "",
    ]

    for stage in closeout.completed_stages:
        lines.append(f"- {stage}")

    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            f"- paper_only: {str(closeout.paper_only).lower()}",
            f"- local_only: {str(closeout.local_only).lower()}",
            f"- read_only: {str(closeout.read_only).lower()}",
            f"- sidecar_only: {str(closeout.sidecar_only).lower()}",
            f"- operator_review_required: {str(closeout.operator_review_required).lower()}",
            f"- no_real_trading: {str(closeout.no_real_trading).lower()}",
            f"- no_tag_release_deploy: {str(closeout.no_tag_release_deploy).lower()}",
            "",
            "## Final Handoff",
            "",
            "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 protects the control center completion index from missing entries, duplicate app IDs, duplicate final current-state files, invalid commit references, dirty status records, unsynced origin/main records, and unsafe tag / release / deploy records.",
            "",
            "This sidecar does not mutate core logic and does not enable trading execution.",
            "",
        ]
    )

    return "\n".join(lines)


def write_completion_index_closeout_md(output_path: str | Path) -> None:
    closeout = build_completion_index_closeout()
    write_text_utf8_lf(output_path, render_completion_index_closeout_md(closeout))
