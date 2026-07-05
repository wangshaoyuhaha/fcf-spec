"""Local source artifact discovery for REPORT-ARCHIVE-D2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .archive_contract import (
    ALLOWED_SOURCE_APP_IDS,
    ALLOWED_SOURCE_TYPES,
    build_report_archive_contract,
    validate_report_archive_contract,
)


DISCOVERY_ALLOWED_EXTENSIONS = (".json", ".md", ".txt")
DISCOVERY_EXCLUDED_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}


@dataclass(frozen=True)
class ArchiveSourceCandidate:
    """Read-only source artifact candidate for later archive stages."""

    source_app_id: str
    source_type: str
    source_path: str
    source_exists: bool
    file_extension: str
    file_size_bytes: int

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    archive_packet_is_trade_instruction: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def infer_source_app_id(path: str | Path) -> str:
    """Infer source app id from a local path or filename."""

    text = str(path).replace("\\", "/").lower()

    markers = (
        ("OPERATOR-REVIEW-APP-1", ("operator_review", "operator-review")),
        ("AI-CONTEXT-1", ("ai_context", "ai-context")),
        ("STOCK-APP-1", ("stock_app", "stock-app")),
        ("DATA-APP-1", ("data_app", "data-app")),
        ("UI-APP-1", ("ui_app", "ui-app")),
    )

    for app_id, app_markers in markers:
        if any(marker in text for marker in app_markers):
            return app_id

    return ""


def infer_source_type(path: str | Path) -> str:
    """Infer archive source type from a local path or filename."""

    name = Path(path).name.lower()

    if "final_handoff" in name or "final-handoff" in name:
        return "final_handoff"
    if "closeout" in name or "summary" in name:
        return "closeout_summary"
    if "handoff" in name:
        return "workflow_handoff"
    if "report" in name or "current_state" in name:
        return "local_report_artifact"

    return ""


def is_discoverable_archive_source(path: Path) -> bool:
    """Return whether a file path can be considered an archive source candidate."""

    if not path.is_file():
        return False
    if path.suffix.lower() not in DISCOVERY_ALLOWED_EXTENSIONS:
        return False
    if any(part in DISCOVERY_EXCLUDED_DIR_NAMES for part in path.parts):
        return False

    return bool(infer_source_app_id(path) and infer_source_type(path))


def build_archive_source_candidate(path: str | Path) -> ArchiveSourceCandidate:
    """Build a read-only candidate object from a path."""

    source_path = Path(path)
    source_app_id = infer_source_app_id(source_path)
    source_type = infer_source_type(source_path)

    file_size = 0
    if source_path.exists() and source_path.is_file():
        file_size = source_path.stat().st_size

    return ArchiveSourceCandidate(
        source_app_id=source_app_id,
        source_type=source_type,
        source_path=str(source_path),
        source_exists=source_path.exists() and source_path.is_file(),
        file_extension=source_path.suffix.lower(),
        file_size_bytes=file_size,
    )


def validate_archive_source_candidate(candidate: ArchiveSourceCandidate) -> list[str]:
    """Validate one archive source candidate."""

    errors: list[str] = []

    if candidate.source_app_id not in ALLOWED_SOURCE_APP_IDS:
        errors.append("source_app_id is not allowed")
    if candidate.source_type not in ALLOWED_SOURCE_TYPES:
        errors.append("source_type is not allowed")
    if not candidate.source_path:
        errors.append("source_path is required")
    if candidate.file_extension not in DISCOVERY_ALLOWED_EXTENSIONS:
        errors.append("file_extension is not allowed")
    if candidate.file_size_bytes < 0:
        errors.append("file_size_bytes must be non-negative")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
    )
    for flag_name in required_true_flags:
        if getattr(candidate, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "archive_packet_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(candidate, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def discover_archive_source_candidates(root_path: str | Path) -> tuple[ArchiveSourceCandidate, ...]:
    """Discover local source artifact candidates without reading or mutating contents."""

    contract = build_report_archive_contract()
    contract_errors = validate_report_archive_contract(contract)
    if contract_errors:
        raise ValueError("; ".join(contract_errors))

    root = Path(root_path)
    if not root.exists():
        return ()

    candidates: list[ArchiveSourceCandidate] = []
    for path in sorted(root.rglob("*")):
        if is_discoverable_archive_source(path):
            candidate = build_archive_source_candidate(path)
            if validate_archive_source_candidate(candidate) == []:
                candidates.append(candidate)

    return tuple(candidates)


def summarize_archive_source_candidates(
    candidates: tuple[ArchiveSourceCandidate, ...] | list[ArchiveSourceCandidate],
) -> dict[str, Any]:
    """Summarize discovered candidates for later archive manifest stages."""

    by_app: dict[str, int] = {}
    by_type: dict[str, int] = {}

    for candidate in candidates:
        by_app[candidate.source_app_id] = by_app.get(candidate.source_app_id, 0) + 1
        by_type[candidate.source_type] = by_type.get(candidate.source_type, 0) + 1

    return {
        "candidate_count": len(candidates),
        "by_source_app_id": by_app,
        "by_source_type": by_type,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
    }
