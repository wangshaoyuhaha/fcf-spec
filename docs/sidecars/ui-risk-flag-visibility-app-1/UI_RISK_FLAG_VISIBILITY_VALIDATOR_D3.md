# UI-RISK-FLAG-VISIBILITY-APP-1 D3 Visibility Preservation Validator

Status: D3
Scope: sidecar-only
Core boundary: P1-P47 frozen; no P48; no core mutation.
Safety boundary: paper-only, local-only, read-only, operator review required.

## Purpose

D3 adds a sidecar-only validator for visibility preservation.

The validator checks whether downstream UI, handoff, review, dashboard, export, archive, and operator-facing packets preserve protected risk metadata.

## Required protected metadata

- risk_flags
- reason_codes
- review_status
- blocked_reasons
- conflict_signals
- missing_required_fields
- unsafe_permissions
- operator_review_required
- circuit_break
- correlation_id
- source_artifact
- evidence_chain_status

## Validator rules

- If source packet contains risk_flags, rendered packet must contain risk_flags.
- If source packet contains reason_codes, rendered packet must contain reason_codes.
- REVIEW_REQUIRED must remain REVIEW_REQUIRED.
- CIRCUIT_BREAK must remain visible and truthy when present.
- conflict_signals must remain visible.
- missing_required_fields must remain visible.
- unsafe_permissions must remain visible.
- abnormal evidence_chain_status must remain visible.
- correlation_id must be preserved when present.
- source_artifact must be preserved when present.

## Operator review rules

Rendered packet must require operator review when source packet contains:

- REVIEW_REQUIRED
- CIRCUIT_BREAK
- conflict_signals
- missing_required_fields
- unsafe_permissions
- stale evidence_chain_status
- incomplete evidence_chain_status
- missing evidence_chain_status
- unresolved evidence_chain_status

## D3 acceptance criteria

D3 passes when validator tests confirm protected metadata cannot be removed, hidden, downgraded, or converted into summary-only output.
