# CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 D1 Contract

## Phase

CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1

## Deliverable

D1 - Global Scan Classification Contract

## Purpose

This sidecar defines the classification contract for global grep / safety scan results.

The goal is to separate expected governance hits from actionable structural risks.

This sidecar does not weaken any existing safety boundary.
This sidecar does not mutate frozen core logic.
This sidecar does not approve, downgrade, hide, or auto-resolve safety findings.

## Scope

This contract applies to scan hits from:

- governance text
- safety boundary text
- test assertions
- final-state history
- handoff documents
- archive reports
- project control center documents

## Classification Labels

Every global scan hit must be classified into exactly one of the following labels:

### EXPECTED_GOVERNANCE_TEXT

Use when the hit appears in governance documentation, architecture policy, control-center policy, safety policy, or approved project rules.

These hits are expected and are not actionable by themselves.

### EXPECTED_TEST_ASSERTION

Use when the hit appears in tests that intentionally assert safety boundaries, blocked behavior, read-only behavior, paper-only behavior, or governance rules.

These hits are expected and are not actionable by themselves.

### EXPECTED_FINAL_STATE_HISTORY

Use when the hit appears in historical final-state summaries, completion records, branch closeouts, merge records, validation baselines, or handoff archives.

These hits are expected and are not actionable by themselves.

### EXPECTED_SAFETY_BOUNDARY

Use when the hit appears in safety boundary statements that explicitly prohibit unsafe behavior.

These hits are expected and are not actionable by themselves.

### ACTIONABLE_STALE_STATE

Use when the hit indicates stale project state, outdated completion status, obsolete validation count, obsolete branch pointer, outdated current-state file, or a handoff that conflicts with the current control center.

These hits require review.

### ACTIONABLE_UNSAFE_PERMISSION

Use when the hit appears to permit, enable, normalize, or leave room for unsafe behavior, including but not limited to:

- real trading
- broker API
- exchange API
- API key usage
- wallet key usage
- real order execution
- buy / sell / order actions
- automatic approval of review-required states
- downgrading CIRCUIT_BREAK
- bypassing operator review

These hits require review and must never be auto-approved.

### ACTIONABLE_STRUCTURE_GAP

Use when the hit indicates a structural architecture gap, missing dependency boundary, missing classification rule, missing provenance, missing audit trail, missing sidecar isolation, or unclear ownership between governance layers.

These hits require review.

## Label Exclusivity Rule

A scan hit must receive exactly one classification label.

If multiple labels appear possible, choose the most conservative actionable label in this order:

1. ACTIONABLE_UNSAFE_PERMISSION
2. ACTIONABLE_STRUCTURE_GAP
3. ACTIONABLE_STALE_STATE
4. EXPECTED_SAFETY_BOUNDARY
5. EXPECTED_TEST_ASSERTION
6. EXPECTED_FINAL_STATE_HISTORY
7. EXPECTED_GOVERNANCE_TEXT

## Non-Downgrade Rule

Actionable labels must not be downgraded to expected labels automatically.

Expected labels only mean the hit is explainable by approved governance or history.
Expected labels do not delete the hit.
Expected labels do not remove audit visibility.

## Safety Boundary

This sidecar is:

- paper-only
- local-only
- read-only
- sidecar-only
- operator-review-required

This sidecar must not:

- create P48
- mutate frozen core P1-P47
- create real trading functionality
- connect to broker APIs
- connect to exchange APIs
- use API keys
- use wallet keys
- place buy, sell, or order instructions
- deploy anything
- create release tags
- bypass operator review

## Input Contract

A scan hit may include:

- source path
- line number
- matched text
- surrounding context
- matched keyword
- scan family
- timestamp
- correlation id

## Output Contract

A classified scan hit must include:

- source path
- line number
- matched text
- classification label
- reason code
- review required flag
- correlation id if available

## Review Required Rule

The following labels always require review:

- ACTIONABLE_STALE_STATE
- ACTIONABLE_UNSAFE_PERMISSION
- ACTIONABLE_STRUCTURE_GAP

The following labels remain visible but do not require immediate remediation by themselves:

- EXPECTED_GOVERNANCE_TEXT
- EXPECTED_TEST_ASSERTION
- EXPECTED_FINAL_STATE_HISTORY
- EXPECTED_SAFETY_BOUNDARY

## D1 Acceptance Criteria

D1 is complete when:

- the seven classification labels are defined
- label exclusivity is defined
- actionable labels require review
- expected labels remain visible
- non-downgrade rule is defined
- paper-only / local-only / read-only / sidecar-only boundary is preserved
- no core mutation is introduced
- no tag, release, or deploy is performed
