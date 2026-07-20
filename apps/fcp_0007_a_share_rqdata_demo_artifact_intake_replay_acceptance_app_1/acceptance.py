from __future__ import annotations

from apps.fcp_0006_a_share_mvp_target_data_acceptance_baseline_app_1 import (
    CANONICAL_DATA_FIELDS,
)

from .contracts import (
    OBSERVED_FCP_0006_FIELDS,
    RQDataDemoAcceptanceResult,
    RQDataDemoLoadResult,
    canonical_sha256,
)


def evaluate_rqdata_demo_acceptance(
    loaded: RQDataDemoLoadResult,
) -> RQDataDemoAcceptanceResult:
    if not isinstance(loaded, RQDataDemoLoadResult):
        raise TypeError("loaded must be RQDataDemoLoadResult")
    required = tuple(sorted(item[0] for item in CANONICAL_DATA_FIELDS))
    observed = tuple(sorted(OBSERVED_FCP_0006_FIELDS))
    missing = tuple(sorted(set(required) - set(observed)))
    instruments = tuple(sorted({item.instrument_id for item in loaded.rows}))
    dates = tuple(item.trade_date for item in loaded.rows)
    findings = {
        "COMMERCIAL_RIGHTS_UNRESOLVED",
        "INTRADAY_COVERAGE_MISSING",
        "POINT_IN_TIME_AVAILABILITY_MISSING",
        "PRODUCT_ACCEPTANCE_EVIDENCE_BLOCKED",
        "REGISTERED_LOCAL_DEMO_SCHEMA_READY",
        "RETENTION_RIGHTS_UNRESOLVED",
    }
    if len(instruments) < 2:
        findings.add("MULTI_INSTRUMENT_COVERAGE_MISSING")
    if loaded.repeated_bom_count:
        findings.add("REPEATED_LEADING_BOM_NORMALIZED_IN_MEMORY")
    payload = {
        "date_max": max(dates),
        "date_min": min(dates),
        "finding_codes": sorted(findings),
        "instrument_ids": instruments,
        "missing_required_field_ids": missing,
        "normalized_csv_sha256": loaded.normalized_csv_sha256,
        "observed_field_ids": observed,
        "product_evidence_state": "BLOCKED",
        "replay_sha256": loaded.replay_sha256,
        "row_count": len(loaded.rows),
        "rowset_sha256": loaded.rowset_sha256,
        "schema_state": "READY_FOR_LOCAL_SCHEMA_REPLAY",
        "source_artifact_sha256": loaded.artifact.artifact_sha256,
    }
    return RQDataDemoAcceptanceResult(
        result_sha256=canonical_sha256(payload),
        **payload,
    )
