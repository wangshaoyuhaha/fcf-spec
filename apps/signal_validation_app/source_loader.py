"""D2 read-only source loader for SIGNAL-VALIDATION-APP-1.

The loader inspects local source packet metadata from completed sidecar layers.
It is intentionally read-only and does not mutate, delete, overwrite, or repair
any source file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class SignalSourceSpec:
    """Read-only source packet specification."""

    source_id: str
    layer_id: str
    relative_path: str
    payload_type: str
    required: bool = False


DEFAULT_SIGNAL_SOURCE_SPECS: List[SignalSourceSpec] = [
    SignalSourceSpec(
        source_id="stock_app_current_state",
        layer_id="STOCK-APP-1",
        relative_path="FCF_CURRENT_STATE_STOCK_APP_1.md",
        payload_type="markdown",
    ),
    SignalSourceSpec(
        source_id="ai_context_current_state",
        layer_id="AI-CONTEXT-1",
        relative_path="FCF_CURRENT_STATE_AI_CONTEXT_1.md",
        payload_type="markdown",
    ),
    SignalSourceSpec(
        source_id="operator_review_final_state",
        layer_id="OPERATOR-REVIEW-APP-1",
        relative_path="FCF_CURRENT_STATE_OPERATOR_REVIEW_APP_1_FINAL.md",
        payload_type="markdown",
    ),
    SignalSourceSpec(
        source_id="report_archive_final_state",
        layer_id="REPORT-ARCHIVE-APP-1",
        relative_path="FCF_CURRENT_STATE_REPORT_ARCHIVE_APP_1_FINAL.md",
        payload_type="markdown",
    ),
    SignalSourceSpec(
        source_id="data_quality_ops_final_state",
        layer_id="DATA-QUALITY-OPS-APP-1",
        relative_path="FCF_CURRENT_STATE_DATA_QUALITY_OPS_APP_1_FINAL.md",
        payload_type="markdown",
    ),
    SignalSourceSpec(
        source_id="market_scenario_final_state",
        layer_id="MARKET-SCENARIO-APP-1",
        relative_path="FCF_CURRENT_STATE_MARKET_SCENARIO_APP_1_FINAL.md",
        payload_type="markdown",
    ),
    SignalSourceSpec(
        source_id="backtest_review_final_state",
        layer_id="BACKTEST-REVIEW-APP-1",
        relative_path="FCF_CURRENT_STATE_BACKTEST_REVIEW_APP_1_FINAL.md",
        payload_type="markdown",
        required=True,
    ),
]


def _safe_read_text(path: Path, max_chars: int) -> Optional[str]:
    """Read a text file with a bounded preview size."""

    if not path.exists() or not path.is_file():
        return None

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return handle.read(max_chars)


def inspect_signal_source(
    repo_root: Path,
    spec: SignalSourceSpec,
    max_preview_chars: int = 1200,
) -> Dict[str, Any]:
    """Inspect one source packet without changing it."""

    path = repo_root / spec.relative_path
    exists = path.exists() and path.is_file()
    stat = path.stat() if exists else None
    preview = _safe_read_text(path, max_preview_chars) if exists else None

    return {
        "source_id": spec.source_id,
        "layer_id": spec.layer_id,
        "relative_path": spec.relative_path,
        "payload_type": spec.payload_type,
        "required": spec.required,
        "exists": exists,
        "status": "AVAILABLE" if exists else ("MISSING_REQUIRED" if spec.required else "MISSING_OPTIONAL"),
        "size_bytes": stat.st_size if stat else 0,
        "preview": preview or "",
        "read_only": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
    }


def load_signal_source_manifest(
    repo_root: str | Path = ".",
    specs: Optional[Iterable[SignalSourceSpec]] = None,
    max_preview_chars: int = 1200,
) -> Dict[str, Any]:
    """Build a read-only source manifest for signal validation."""

    root = Path(repo_root)
    selected_specs = list(specs) if specs is not None else list(DEFAULT_SIGNAL_SOURCE_SPECS)
    sources = [
        inspect_signal_source(root, spec, max_preview_chars=max_preview_chars)
        for spec in selected_specs
    ]

    missing_required = [
        source["source_id"]
        for source in sources
        if source["required"] and not source["exists"]
    ]
    available = [source["source_id"] for source in sources if source["exists"]]
    missing_optional = [
        source["source_id"]
        for source in sources
        if not source["required"] and not source["exists"]
    ]

    return {
        "app_id": "SIGNAL-VALIDATION-APP-1",
        "stage_id": "SIGNAL-VALIDATION-D2",
        "loader_mode": "read_only_source_packet_metadata",
        "source_count": len(sources),
        "available_count": len(available),
        "missing_required_count": len(missing_required),
        "missing_optional_count": len(missing_optional),
        "available_sources": available,
        "missing_required_sources": missing_required,
        "missing_optional_sources": missing_optional,
        "sources": sources,
        "read_only": True,
        "paper_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
    }


def summarize_signal_source_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Return a compact loader summary for downstream packets."""

    if manifest["missing_required_count"] > 0:
        status = "BLOCKED_MISSING_REQUIRED_SOURCE"
    elif manifest["available_count"] == 0:
        status = "NO_SOURCE_AVAILABLE"
    elif manifest["missing_optional_count"] > 0:
        status = "PARTIAL_SOURCE_AVAILABLE"
    else:
        status = "ALL_CONFIGURED_SOURCES_AVAILABLE"

    return {
        "app_id": manifest["app_id"],
        "stage_id": manifest["stage_id"],
        "loader_status": status,
        "source_count": manifest["source_count"],
        "available_count": manifest["available_count"],
        "missing_required_count": manifest["missing_required_count"],
        "missing_optional_count": manifest["missing_optional_count"],
        "read_only": manifest["read_only"],
        "operator_review_required": manifest["operator_review_required"],
        "real_execution_allowed": manifest["real_execution_allowed"],
        "trade_action_enabled": manifest["trade_action_enabled"],
    }
