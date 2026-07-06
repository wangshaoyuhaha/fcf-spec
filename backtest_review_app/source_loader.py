"""BACKTEST-REVIEW-D2 local source metadata loader.

The loader is paper-only and read-only.
It discovers local backtest review source metadata without reading source content
or mutating any source file.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import hashlib


STAGE_ID = "BACKTEST-REVIEW-D2"


@dataclass(frozen=True)
class BacktestSourceSpec:
    source_kind: str
    relative_globs: List[str]


@dataclass(frozen=True)
class BacktestSourceMetadata:
    source_id: str
    source_kind: str
    relative_path: str
    suffix: str
    exists: bool
    is_file: bool
    size_bytes: Optional[int]
    content_read_allowed: bool
    source_content_mutation_allowed: bool
    source_deletion_allowed: bool
    source_overwrite_allowed: bool
    real_account_access_allowed: bool
    real_position_access_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def default_backtest_source_specs() -> List[BacktestSourceSpec]:
    return [
        BacktestSourceSpec(
            source_kind="report_archive_outputs",
            relative_globs=[
                "runtime/report_archive_app/**/*.json",
                "runtime/report_archive/**/*.json",
                "docs/REPORT_ARCHIVE*.md",
                "FCF_CURRENT_STATE_REPORT_ARCHIVE_APP_1_FINAL.md",
            ],
        ),
        BacktestSourceSpec(
            source_kind="market_scenario_outputs",
            relative_globs=[
                "runtime/market_scenario_app/**/*.json",
                "runtime/market_scenario/**/*.json",
                "docs/MARKET_SCENARIO*.md",
                "FCF_CURRENT_STATE_MARKET_SCENARIO_APP_1_FINAL.md",
            ],
        ),
        BacktestSourceSpec(
            source_kind="operator_review_outputs",
            relative_globs=[
                "runtime/operator_review_app/**/*.json",
                "runtime/operator_review/**/*.json",
                "docs/OPERATOR_REVIEW*.md",
                "FCF_CURRENT_STATE_OPERATOR_REVIEW_APP_1_FINAL.md",
            ],
        ),
        BacktestSourceSpec(
            source_kind="data_quality_ops_outputs",
            relative_globs=[
                "runtime/data_quality_ops_app/**/*.json",
                "runtime/data_quality_ops/**/*.json",
                "docs/DATA_QUALITY_OPS*.md",
                "FCF_CURRENT_STATE_DATA_QUALITY_OPS_APP_1_FINAL.md",
            ],
        ),
        BacktestSourceSpec(
            source_kind="ui_ai_stock_handoff_metadata",
            relative_globs=[
                "runtime/ui_app/**/*.json",
                "runtime/ai_context_app/**/*.json",
                "runtime/stock_app/**/*.json",
                "docs/UI_APP*.md",
                "docs/AI_CONTEXT*.md",
                "docs/STOCK_APP*.md",
            ],
        ),
    ]


def _safe_relative_path(root_path: Path, candidate_path: Path) -> str:
    return candidate_path.resolve().relative_to(root_path.resolve()).as_posix()


def _source_id(source_kind: str, relative_path: str) -> str:
    raw = f"{source_kind}:{relative_path}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _metadata_for_path(root_path: Path, source_kind: str, candidate_path: Path) -> BacktestSourceMetadata:
    relative_path = _safe_relative_path(root_path, candidate_path)
    exists = candidate_path.exists()
    is_file = candidate_path.is_file()
    size_bytes = candidate_path.stat().st_size if exists and is_file else None
    return BacktestSourceMetadata(
        source_id=_source_id(source_kind, relative_path),
        source_kind=source_kind,
        relative_path=relative_path,
        suffix=candidate_path.suffix.lower(),
        exists=exists,
        is_file=is_file,
        size_bytes=size_bytes,
        content_read_allowed=False,
        source_content_mutation_allowed=False,
        source_deletion_allowed=False,
        source_overwrite_allowed=False,
        real_account_access_allowed=False,
        real_position_access_allowed=False,
    )


def load_local_backtest_source_metadata(
    root_path: Path | str,
    specs: Optional[Iterable[BacktestSourceSpec]] = None,
) -> List[BacktestSourceMetadata]:
    root = Path(root_path)
    selected_specs = list(specs) if specs is not None else default_backtest_source_specs()
    records: List[BacktestSourceMetadata] = []
    seen = set()

    for spec in selected_specs:
        for relative_glob in spec.relative_globs:
            for candidate in sorted(root.glob(relative_glob)):
                if not candidate.is_file():
                    continue
                relative_path = _safe_relative_path(root, candidate)
                key = (spec.source_kind, relative_path)
                if key in seen:
                    continue
                seen.add(key)
                records.append(_metadata_for_path(root, spec.source_kind, candidate))

    return records


def build_backtest_source_manifest(root_path: Path | str) -> Dict[str, object]:
    records = load_local_backtest_source_metadata(root_path)
    source_kinds_found = sorted({record.source_kind for record in records})
    return {
        "stage_id": STAGE_ID,
        "source_count": len(records),
        "source_kinds_found": source_kinds_found,
        "records": [record.to_dict() for record in records],
        "safety_flags": {
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "content_read_allowed": False,
            "source_content_mutation_allowed": False,
            "source_deletion_allowed": False,
            "source_overwrite_allowed": False,
            "real_trading_allowed": False,
            "real_execution_allowed": False,
            "real_account_access_allowed": False,
            "real_position_access_allowed": False,
        },
    }
