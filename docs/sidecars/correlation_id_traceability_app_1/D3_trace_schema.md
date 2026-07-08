# CORRELATION-ID-TRACEABILITY-APP-1 D3 Trace Schema

## Purpose

This document defines the required trace record schema for Correlation_ID governance.

## Trace Record Fields

Each trace record must include:

- trace_record_id
- correlation_id
- trace_schema_version
- source_stage
- source_artifact_id
- source_artifact_path
- source_artifact_checksum
- parent_correlation_id
- child_correlation_ids
- validation_state
- review_state
- risk_flags_present
- reason_codes_present
- ui_reference
- archive_reference
- dify_handoff_reference
- trace_created_at_utc
- operator_review_required

## Stage Values

Allowed source_stage values:
- DATA
- VALIDATION
- OPERATOR_REVIEW
- UI_REPORT
- ARCHIVE
- DIFY_HANDOFF

## State Rules

- validation_state must preserve failure states
- review_state must preserve operator review requirements
- risk_flags_present must not be hidden or downgraded
- reason_codes_present must not be deleted or rewritten
- archive_reference must point to local archive metadata only
- dify_handoff_reference must point to local handoff metadata only

## Forbidden Use

Trace schema records must not become:
- trade instructions
- order tickets
- execution triggers
- broker connectors
- exchange connectors
- credential records
- score mutation records
- reason code mutation records
- risk flag downgrade records
- operator review bypass records

## Output

D3 output is a schema contract only.
It is paper-only, local-only, read-only, sidecar-only, and operator-review-gated.
