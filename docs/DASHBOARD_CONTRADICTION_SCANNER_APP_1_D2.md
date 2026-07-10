# DASHBOARD-CONTRADICTION-SCANNER-APP-1 D2

## Purpose

Provide a deterministic read-only loader for governed dashboard sources.

## Accepted source types

- DASHBOARD_STATUS_PACKET
- OPERATOR_REVIEW_PACKET
- MODEL_GOVERNANCE_PACKET
- VALIDATION_BASELINE_SNAPSHOT
- ARTIFACT_LIFECYCLE_RECORD
- AI_EVIDENCE_PACKAGE

## Required fields

- artifact_id
- artifact_type
- correlation_id
- research_run_id
- validation_baseline_id

## Preserved fields

- source_artifact_ids
- risk_flags
- reason_codes
- validation_state
- review_state
- lifecycle_state
- archive_state
- summary

## Integrity

Each loaded record receives a deterministic SHA-256 source_record_hash.

The complete source manifest receives a deterministic manifest_hash.

Duplicate artifact identifiers are rejected.

## Boundary

The loader:

- reads governed mappings only
- does not mutate source inputs
- does not delete or downgrade risk flags
- does not fabricate trace identifiers
- does not execute workflows
- requires operator review
- remains paper-only, local-only, read-only, and sidecar-only
