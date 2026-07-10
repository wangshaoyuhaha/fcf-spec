# DASHBOARD-CONTRADICTION-SCANNER-APP-1 D1

## Purpose

Define the executable sidecar boundary contract for dashboard contradiction scanning.

The scanner compares governed source artifacts and emits paper-only contradiction findings.

## Required boundaries

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no core mutation
- no P48 expansion
- no source mutation
- no risk flag deletion
- no risk flag downgrade
- no automatic review pass
- no UI execution action

## Required traceability

- correlation_id
- research_run_id
- source_artifact_ids
- validation_baseline_id

## Initial contradiction classes

- RISK_FLAG_MISSING
- RISK_FLAG_DOWNGRADED
- SUMMARY_RAW_CONFLICT
- REVIEW_STATE_MISMATCH
- LIFECYCLE_STATE_MISMATCH
- VALIDATION_STATE_MISMATCH
- ARCHIVE_STATE_MISMATCH
- SOURCE_LINEAGE_MISMATCH

## Output

PAPER_ONLY_CONTRADICTION_FINDINGS

Findings require operator review and archive preservation.

## Forbidden

- real trading
- real execution
- broker connection
- exchange connection
- API key access
- wallet private key access
- real account access
- real position access
- buy, sell, or order action
- automatic position sizing
- automatic portfolio action
- operator review bypass
