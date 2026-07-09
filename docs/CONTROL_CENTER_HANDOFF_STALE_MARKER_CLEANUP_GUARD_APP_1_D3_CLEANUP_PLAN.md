# CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1 D3 Cleanup Plan

## Phase

CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1

## Deliverable

D3 - Stale Marker Cleanup Plan

## Purpose

D3 builds a deterministic cleanup plan from the D2 stale marker inventory.

D3 does not edit handoff files.
D3 does not delete historical records.
D3 only decides which actionable stale markers should be cleaned in a later controlled cleanup stage.

## Cleanup Eligibility

Only ACTIONABLE_STALE_STATE hits are cleanup eligible.

EXPECTED_FINAL_STATE_HISTORY hits are preserved.

## Planned Action Types

Allowed planned actions:

- REPLACE_WITH_CURRENT_STATE
- MARK_AS_HISTORICAL
- PRESERVE_HISTORY

## Current State Replacement

Current-entry stale next-action text must be replaced with current truth:

- CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 completed
- main merge commit ad16c03
- final handoff sync commit 8c18573
- validation 1884 passed
- main clean
- origin/main synced
- next work requires explicit operator approval

## Safety Boundary

This sidecar remains:

- paper-only
- local-only
- sidecar-only
- operator review required

Forbidden:

- no P48
- no P1-P47 core mutation
- no source code mutation
- no runtime mutation
- no real trading
- no broker API
- no exchange API
- no API key
- no wallet private key
- no buy / sell / order
- no tag
- no release
- no deploy

## D3 Acceptance Criteria

D3 is complete when:

- cleanup plan builder exists
- only ACTIONABLE_STALE_STATE hits become cleanup actions
- EXPECTED_FINAL_STATE_HISTORY hits are preserved
- current state replacement text is deterministic
- cleanup plan does not mutate files
- safety boundary is preserved
- no tag, release, or deploy is performed
