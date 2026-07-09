# UI-RISK-FLAG-VISIBILITY-APP-1 D1 Contract

Status: D1 UI Risk Flag Visibility Contract
Scope: sidecar-only
Core: P1-P47 frozen; no P48; no core mutation.
Mode: paper-only / local-only / read-only / operator-review-required.

## Purpose

This sidecar defines a visibility contract for UI, handoff, review, dashboard, export, and archive-facing surfaces.

It ensures `risk_flags` and `reason_codes` remain explicitly visible and cannot be hidden, weakened, renamed into vague language, summarized away, or downgraded before operator review.

## Protected Fields

- `risk_flags`
- `reason_codes`
- `review_status`
- `blocked_reasons`
- `conflict_signals`
- `missing_required_fields`
- `unsafe_permissions`
- `operator_review_required`
- `circuit_break`

## Mandatory Display Contract

Any UI, handoff, review, dashboard, export, or archive-facing surface that receives a candidate, packet, report, or archive item containing protected risk metadata MUST display or carry forward:

1. raw `risk_flags`
2. raw `reason_codes`
3. explicit blocked / review status
4. conflict markers
5. missing-field markers
6. unsafe-permission markers
7. source trace / correlation reference when available

No surface may replace explicit risk metadata with only summaries such as "looks fine", "low risk", "safe", "approved", or "ready".

## Non-Downgrade Rules

- `REVIEW_REQUIRED` MUST NOT auto-pass.
- `CIRCUIT_BREAK` MUST NOT downgrade.
- conflict flags MUST NOT be hidden.
- missing required fields MUST remain visible.
- unsafe permissions MUST remain visible.
- reason codes MUST remain machine-readable and human-visible.
- downstream views may add explanation text but MUST NOT remove the original code.

## Operator Review Gate

Any item containing one or more of the following MUST be routed to operator review:

- `REVIEW_REQUIRED`
- `CIRCUIT_BREAK`
- conflict signal
- missing required field
- unsafe permission
- unresolved reason code
- stale evidence chain
- incomplete evidence chain

## Allowed Sidecar Actions

- read existing sidecar outputs
- validate visibility metadata
- generate sidecar-only visibility summaries
- append review-facing guard documentation
- add tests around contract preservation

## Forbidden Actions

- mutate P1-P47 core
- create P48
- call broker or exchange APIs
- use API keys
- create orders or execution logic
- infer real positions or balances
- hide or downgrade risk flags
- hide or rewrite reason codes into non-auditable text
- tag
- release
- deploy

## D1 Acceptance Criteria

D1 passes only if:

- this contract exists in repo
- protected fields are explicitly listed
- non-downgrade rules include REVIEW_REQUIRED and CIRCUIT_BREAK
- conflict, missing-field, and unsafe-permission visibility is required
- operator review routing is required
- tests verify the contract text
