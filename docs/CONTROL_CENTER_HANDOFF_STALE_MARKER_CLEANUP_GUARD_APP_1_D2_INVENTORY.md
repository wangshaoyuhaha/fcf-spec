# CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1 D2 Inventory

## Phase

CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1

## Deliverable

D2 - Stale Marker Inventory Scanner

## Purpose

D2 defines a deterministic inventory scanner for stale handoff markers.

D2 does not clean handoff files.
D2 does not rewrite current-state files.
D2 only identifies stale marker candidates and classifies whether they are historical or actionable.

## Target Files

The inventory scanner is limited to:

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md
- docs/HANDOFF_PROMPT.md

## Stale Marker Families

The scanner detects these marker families:

- APPROVED_BUT_NOT_STARTED
- APPROVED_NEXT_PHASE
- BEGIN_WITH_D1
- CREATE_SIDECAR_BRANCH
- OLD_VALIDATION_COUNT
- OLD_NEXT_PHASE_CANDIDATE

## Classification

Historical stale markers are classified as:

- EXPECTED_FINAL_STATE_HISTORY

Current-entry stale markers are classified as:

- ACTIONABLE_STALE_STATE

## Current Truth Markers

Current truth must include:

- final handoff sync commit: 8c18573
- main merge commit: ad16c03
- D6 final closeout commit: 42ffeef
- validation: 1884 passed
- completed phase: CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1

## D2 Acceptance Criteria

D2 is complete when:

- inventory scanner exists
- target file scope is limited
- stale marker families are detected
- historical markers are classified as EXPECTED_FINAL_STATE_HISTORY
- current-entry markers are classified as ACTIONABLE_STALE_STATE
- current truth markers are verified
- no cleanup is performed
- no core mutation is introduced
- no tag, release, or deploy is performed
