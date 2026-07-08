# CORRELATION-ID-TRACEABILITY-APP-1 D4 Chain Integrity Rules

## Purpose

This document defines paper-only chain integrity rules for Correlation_ID traceability.

## Integrity Rules

Each Correlation_ID chain must satisfy:

- every trace record must have one correlation_id
- every source_artifact_id must map to one source_stage
- every source_artifact_checksum must be preserved when available
- parent_correlation_id must not create circular references
- child_correlation_ids must not create circular references
- validation failure states must remain visible
- operator review requirements must remain visible
- risk_flags_present must remain visible
- reason_codes_present must remain visible
- UI references must not hide risk flags
- archive references must not overwrite archived content
- Dify handoff references must stay local and read-only

## Break Conditions

A Correlation_ID chain is broken when:

- correlation_id is missing
- source_stage is missing
- source_artifact_id is missing
- validation_state is downgraded
- review_state bypasses operator review
- risk_flags_present is hidden
- reason_codes_present is deleted
- archive_reference points to overwritten content
- dify_handoff_reference points to deployment action
- parent or child references create a cycle

## Required Handling

Broken chains must be marked as trace_integrity_failed.
Broken chains must not be promoted to valid archive state.
Broken chains must not be passed to Dify handoff as complete.
Broken chains must not suppress operator review.
Broken chains must not become trade instructions.

## Output

D4 output is a chain integrity rule contract only.
It is paper-only, local-only, read-only, sidecar-only, and operator-review-gated.
