# UI-RISK-FLAG-VISIBILITY-APP-1 D4 Operator Review Visibility Packet

Status: D4
Scope: sidecar-only
Core boundary: P1-P47 frozen; no P48; no core mutation.
Safety boundary: paper-only, local-only, read-only, operator review required.

## Purpose

D4 defines the operator review visibility packet.

The packet is designed for UI, dashboard, review, handoff, export, and archive-facing surfaces.

D4 ensures protected risk metadata remains explicit before operator review.

## Packet requirements

The review visibility packet must include:

- candidate_id
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
- visibility_errors
- display_blocked

## Non-downgrade requirements

- REVIEW_REQUIRED must remain visible.
- CIRCUIT_BREAK must remain visible.
- conflict_signals must remain visible.
- missing_required_fields must remain visible.
- unsafe_permissions must remain visible.
- reason_codes must remain raw and explicit.
- risk_flags must remain raw and explicit.

## Display blocked rule

display_blocked must be true when visibility_errors is not empty.

display_blocked must also be true when operator_review_required is true.

## D4 acceptance criteria

D4 passes when tests prove the review packet preserves risk_flags, reason_codes, REVIEW_REQUIRED, CIRCUIT_BREAK, conflict_signals, missing_required_fields, unsafe_permissions, correlation_id, source_artifact, and abnormal evidence_chain_status.
