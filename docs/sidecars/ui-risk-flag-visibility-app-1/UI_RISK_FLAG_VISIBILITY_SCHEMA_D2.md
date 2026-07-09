# UI-RISK-FLAG-VISIBILITY-APP-1 D2 Protected Risk Metadata Schema

Status: D2
Scope: sidecar-only
Core boundary: P1-P47 frozen; no P48; no core mutation.
Safety boundary: paper-only, local-only, read-only, operator review required.

## Purpose

D2 defines the protected risk metadata fields that must remain visible in UI, handoff, review, dashboard, export, archive, and operator-facing surfaces.

D2 does not add trading logic.
D2 does not connect broker or exchange APIs.
D2 does not use API keys.
D2 does not create real orders, real positions, real accounts, or real execution.
D2 does not mutate core.

## Protected fields

The following fields must be preserved when present:

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

## Preservation rules

- risk_flags must remain explicitly visible.
- reason_codes must remain machine-readable and human-visible.
- REVIEW_REQUIRED must not auto-pass.
- CIRCUIT_BREAK must not downgrade.
- conflict_signals must not be hidden.
- missing_required_fields must not be hidden.
- unsafe_permissions must not be hidden.
- correlation_id must be preserved when present.
- source_artifact must be preserved when present.
- stale, incomplete, missing, or unresolved evidence_chain_status must remain visible.

## Operator review routing

An item must route to operator review when it contains:

- REVIEW_REQUIRED
- CIRCUIT_BREAK
- conflict_signals
- missing_required_fields
- unsafe_permissions
- stale evidence_chain_status
- incomplete evidence_chain_status
- missing evidence_chain_status
- unresolved evidence_chain_status

## Forbidden downgrade patterns

- replacing risk_flags with a safe summary
- replacing reason_codes with prose only
- replacing blocked_reasons with minor issue
- replacing REVIEW_REQUIRED with approved
- replacing CIRCUIT_BREAK with review_optional
- hiding conflict, missing field, or unsafe permission markers

## D2 acceptance criteria

D2 passes when this schema exists, tests verify all protected fields, and tests verify review routing for REVIEW_REQUIRED, CIRCUIT_BREAK, conflict_signals, missing_required_fields, unsafe_permissions, and abnormal evidence_chain_status.
