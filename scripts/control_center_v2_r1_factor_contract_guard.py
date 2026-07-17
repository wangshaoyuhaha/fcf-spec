from __future__ import annotations

import json
import sys
from dataclasses import fields
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r1_factor_contract_foundation_app_1 import (
    FactorDefinition,
    ForecastTargetDefinition,
    StateSyncAnchor,
    V2_R1_FACTOR_CONTRACT_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r1_factor_contract_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "presentation.py",
    "registries.py",
    "state_sync.py",
)
DOC_PATHS = tuple(
    Path(f"docs/V2_R1_FACTOR_CONTRACT_FOUNDATION_APP_1_D{stage}.md")
    for stage in range(1, 7)
)
FACTOR_FIELDS = (
    "factor_id",
    "factor_name",
    "factor_family",
    "financial_hypothesis",
    "asset_class",
    "market",
    "instrument_scope",
    "research_horizon",
    "input_frequency",
    "output_frequency",
    "formula",
    "formula_version",
    "parameter_schema",
    "parameter_version",
    "input_fields",
    "source_requirements",
    "point_in_time_required",
    "lookback_window",
    "minimum_history",
    "normalization_method",
    "winsorization_method",
    "missing_value_policy",
    "outlier_policy",
    "neutralization_policy",
    "expected_direction",
    "valid_market_regimes",
    "invalid_market_regimes",
    "risk_flags",
    "known_failure_modes",
    "validation_status",
    "champion_challenger_status",
    "approved_by",
    "evidence_refs",
    "correlation_id",
    "effective_at_utc",
    "retired_at_utc",
    "owner",
    "dependency_factor_ids",
    "dependency_data_fields",
    "calculation_unit",
    "output_range",
    "deterministic_test_vectors",
    "reference_implementation_version",
    "compute_cost_class",
    "revision_policy",
    "backfill_policy",
    "replacement_factor_id",
    "lifecycle",
)
TARGET_FIELDS = (
    "target_id",
    "target_version",
    "asset_class",
    "market",
    "instrument_scope",
    "decision_time_basis",
    "forecast_horizon",
    "maturity_rule",
    "target_type",
    "formula",
    "basis",
    "objective",
    "cost_treatment",
    "slippage_treatment",
    "capacity_treatment",
    "label_availability_rule",
    "benchmark_policy",
    "neutralization_policy",
    "missing_behavior",
    "invalid_behavior",
    "censored_behavior",
    "abstention_behavior",
    "evaluation_metrics",
    "minimum_sample",
    "evidence_refs",
    "owner",
    "effective_at_utc",
)
STATE_SYNC_FIELDS = (
    "event_id",
    "instrument_id",
    "event_time_utc",
    "source_time_utc",
    "ingest_time_utc",
    "processing_time_utc",
    "snapshot_time_utc",
    "ttl_seconds",
    "baseline_id",
    "source_sequence",
    "factor_version",
    "data_quality_status",
    "data_latency_ms",
    "registered_artifact_id",
    "payload",
    "state_hash",
)
PROHIBITED_IMPORTS = (
    "import requests",
    "import socket",
    "import subprocess",
    "from urllib",
    "from requests",
)


def build_v2_r1_factor_contract_guard_report(
    root: Path = ROOT,
) -> dict[str, object]:
    app_paths = tuple(root / APP_ROOT / name for name in APP_FILES)
    try:
        app_text = "\n".join(path.read_text(encoding="ascii") for path in app_paths)
        docs = tuple(path.read_text(encoding="ascii") for path in (
            root / relative for relative in DOC_PATHS
        ))
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text = ""
        docs = ()
        ascii_only = False
    boundary = V2_R1_FACTOR_CONTRACT_BOUNDARY
    checks = {
        "canonical_app_files_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        ) == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "factor_contract_fields_exact": tuple(
            field.name for field in fields(FactorDefinition)
        ) == FACTOR_FIELDS,
        "forecast_target_fields_exact": tuple(
            field.name for field in fields(ForecastTargetDefinition)
        ) == TARGET_FIELDS,
        "state_sync_fields_exact": tuple(
            field.name for field in fields(StateSyncAnchor)
        ) == STATE_SYNC_FIELDS,
        "no_network_or_process_import": all(
            token not in app_text for token in PROHIBITED_IMPORTS
        ),
        "authority_boundary_closed": (
            boundary.paper_only
            and boundary.local_only
            and boundary.loopback_only
            and boundary.sidecar_only
            and boundary.registered_artifact_only
            and boundary.read_only_presentation
            and boundary.operator_review_required
            and boundary.deterministic_engine_authority_preserved
            and boundary.registered_evidence_authority_preserved
            and boundary.ai_advisory_only
            and not boundary.live_data_allowed
            and not boundary.network_access_allowed
            and not boundary.credential_access_allowed
            and not boundary.model_invocation_allowed
            and not boundary.prompt_execution_allowed
            and not boundary.factor_calculation_allowed
            and not boundary.official_scoring_allowed
            and not boundary.automatic_activation_allowed
            and not boundary.order_path_allowed
            and not boundary.real_execution_allowed
        ),
        "delivery_docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "no P48" in text for text in docs),
        "scope_not_overclaimed": len(docs) == 6
        and all(
            "production factor runtime remains not implemented" in text.lower()
            for text in docs
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r1_factor_contract_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R1 factor contract foundation guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
