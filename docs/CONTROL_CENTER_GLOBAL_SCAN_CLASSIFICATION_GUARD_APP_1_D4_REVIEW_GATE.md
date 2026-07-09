# CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 D4 Review Gate

## Phase

CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1

## Deliverable

D4 - Actionable Review Gate

## Purpose

D4 adds a deterministic review gate for classified global scan packets.

The gate does not approve unsafe findings.
The gate does not hide expected findings.
The gate does not delete any scan hit.
The gate does not mutate core files, source files, runtime files, or handoff files.

## Gate Status

The gate may return one of these statuses:

- EXPECTED_ONLY_VISIBLE
- ACTIONABLE_REVIEW_REQUIRED
- UNSAFE_PERMISSION_BLOCKED

## Gate Rules

### EXPECTED_ONLY_VISIBLE

Use when all hits are expected labels.

Expected hits remain visible in the packet and summary.

### ACTIONABLE_REVIEW_REQUIRED

Use when at least one actionable label exists.

This status requires operator review.

### UNSAFE_PERMISSION_BLOCKED

Use when at least one ACTIONABLE_UNSAFE_PERMISSION label exists.

This status requires operator review and must be treated as blocked until reviewed.

## Non-Downgrade Rule

The review gate must not downgrade:

- ACTIONABLE_UNSAFE_PERMISSION
- ACTIONABLE_STRUCTURE_GAP
- ACTIONABLE_STALE_STATE

Expected labels do not cancel actionable labels.

## Visibility Rule

All records remain visible.

The review gate produces summaries only.
It must not remove, hide, overwrite, or mutate records.

## Safety Boundary

This sidecar remains:

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

Forbidden:

- no P48
- no P1-P47 core mutation
- no source mutation
- no real trading
- no broker API
- no exchange API
- no API key
- no wallet private key
- no buy / sell / order
- no tag
- no release
- no deploy

## D4 Acceptance Criteria

D4 is complete when:

- a deterministic review gate exists
- expected-only packets remain visible
- actionable packets require review
- unsafe permission packets are blocked
- actionable labels are not downgraded
- packet record count is preserved
- no core mutation is introduced
- no source mutation is introduced
- no tag, release, or deploy is performed
