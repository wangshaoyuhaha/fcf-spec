# CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 D2 Rulebook

## Phase

CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1

## Deliverable

D2 - Global Scan Classification Rulebook

## Purpose

D2 adds a deterministic rulebook for classifying global scan hits.

The rulebook turns a scan hit into exactly one classification label.

## Labels

The only allowed labels are:

- EXPECTED_GOVERNANCE_TEXT
- EXPECTED_TEST_ASSERTION
- EXPECTED_FINAL_STATE_HISTORY
- EXPECTED_SAFETY_BOUNDARY
- ACTIONABLE_STALE_STATE
- ACTIONABLE_UNSAFE_PERMISSION
- ACTIONABLE_STRUCTURE_GAP

## Review Rule

The following labels always require review:

- ACTIONABLE_STALE_STATE
- ACTIONABLE_UNSAFE_PERMISSION
- ACTIONABLE_STRUCTURE_GAP

The following labels remain visible but do not require remediation by themselves:

- EXPECTED_GOVERNANCE_TEXT
- EXPECTED_TEST_ASSERTION
- EXPECTED_FINAL_STATE_HISTORY
- EXPECTED_SAFETY_BOUNDARY

## Conservative Priority

When more than one label could match, apply this order:

1. ACTIONABLE_UNSAFE_PERMISSION
2. ACTIONABLE_STRUCTURE_GAP
3. ACTIONABLE_STALE_STATE
4. EXPECTED_SAFETY_BOUNDARY
5. EXPECTED_TEST_ASSERTION
6. EXPECTED_FINAL_STATE_HISTORY
7. EXPECTED_GOVERNANCE_TEXT

## Rule Families

### Unsafe Permission Rule

Classify as ACTIONABLE_UNSAFE_PERMISSION when a hit appears to permit unsafe actions such as real trading, broker or exchange connectivity, API key usage, wallet private key access, real account or real position access, buy / sell / order actions, operator review bypass, or CIRCUIT_BREAK downgrade.

### Structure Gap Rule

Classify as ACTIONABLE_STRUCTURE_GAP when a hit indicates missing provenance, missing audit trail, missing classification rule, unclear ownership, reverse dependency, circular dependency, or sidecar isolation uncertainty.

### Stale State Rule

Classify as ACTIONABLE_STALE_STATE when a hit indicates stale status, obsolete validation count, obsolete branch pointer, outdated handoff, or conflict with the current control center.

### Safety Boundary Rule

Classify as EXPECTED_SAFETY_BOUNDARY when the hit is a prohibition statement that preserves the project safety boundary.

### Test Assertion Rule

Classify as EXPECTED_TEST_ASSERTION when the hit is inside a test assertion or test file and is not otherwise actionable.

### Final State History Rule

Classify as EXPECTED_FINAL_STATE_HISTORY when the hit belongs to final current-state files, closeout records, validation histories, or historical handoff archives and is not otherwise actionable.

### Governance Text Rule

Classify as EXPECTED_GOVERNANCE_TEXT when the hit belongs to governance docs, control-center docs, handoff docs, architecture docs, or safety policy docs and is not otherwise actionable.

## D2 Acceptance Criteria

D2 is complete when:

- a deterministic sidecar rulebook exists
- all seven labels are represented
- actionable labels require review
- expected labels remain visible
- conservative priority is enforced
- no frozen core file is changed
- no unsafe permission is introduced
- no tag, release, or deploy is performed
