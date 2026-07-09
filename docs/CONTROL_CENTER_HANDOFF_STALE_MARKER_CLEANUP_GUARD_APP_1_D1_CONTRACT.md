# CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1 D1 Contract

## Phase

CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1

## Deliverable

D1 - Handoff Stale Marker Cleanup Contract

## Purpose

This sidecar defines the cleanup contract for stale handoff markers.

The goal is to prevent new ChatGPT windows from mistaking historical phase instructions for current project state.

## Problem

The global scan classification phase identified stale handoff markers such as:

- Approved but not started
- APPROVED NEXT PHASE
- Begin with D1
- Create sidecar branch
- old validation counts
- old next phase candidate text

Some of these markers are valid historical records.
Some may mislead a new window if they appear in current handoff entry sections.

## Classification Rule

Historical archived stale markers are classified as:

- EXPECTED_FINAL_STATE_HISTORY

Current-entry stale markers that can mislead the next window are classified as:

- ACTIONABLE_STALE_STATE

## Scope

This sidecar may inspect and update only current handoff / control-center documentation:

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md
- docs/HANDOFF_PROMPT.md

## Allowed Cleanup

Allowed cleanup actions:

- mark historical stale text as historical
- move stale current-entry text into historical context
- replace outdated next-action text with current state text
- preserve final completion records
- preserve completed phase history
- preserve validation history
- preserve safety boundary text

## Forbidden Cleanup

This sidecar must not:

- delete completed phase history
- delete final current-state history
- hide validation history
- hide safety boundary text
- change source code behavior
- mutate P1-P47 core
- create P48
- downgrade actionable findings
- bypass operator review

## Required Current-State Truth

After cleanup, current handoff entries must state that:

- CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed
- main merge commit is ad16c03
- final handoff sync commit is 8c18573
- validation is 1884 passed
- git status is clean
- origin/main is synced
- next work is architecture gap review or explicitly approved next phase only

## Safety Boundary

This sidecar remains:

- paper-only
- local-only
- read-only until explicit cleanup stage
- sidecar-only
- operator review required

Forbidden:

- no P48
- no P1-P47 core mutation
- no source code mutation
- no runtime mutation
- no real trading
- no real execution
- no broker API
- no exchange API
- no API key
- no wallet private key
- no real account
- no real position
- no buy / sell / order
- no tag
- no release
- no deploy

## D1 Acceptance Criteria

D1 is complete when:

- stale marker cleanup scope is defined
- historical stale markers are separated from actionable stale markers
- allowed cleanup actions are defined
- forbidden cleanup actions are defined
- current-state truth requirements are defined
- safety boundary is preserved
- no handoff cleanup is performed yet
- no core mutation is introduced
- no tag, release, or deploy is performed
