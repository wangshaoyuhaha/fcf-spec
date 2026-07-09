# CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 D3 Classification Packet

## Phase

CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1

## Deliverable

D3 - Classification Packet

## Purpose

D3 defines a deterministic packet format for classified global scan results.

The packet preserves every scan hit and records:

- source path
- line number
- matched text
- context
- classification label
- reason code
- review required flag
- correlation id
- packet summary

## Non-Deletion Rule

D3 must not delete scan hits.

Expected hits remain visible.
Actionable hits remain visible.
No result is hidden because it is expected governance text, test assertion, final-state history, or safety boundary text.

## Review Required Rule

The following labels always require review:

- ACTIONABLE_STALE_STATE
- ACTIONABLE_UNSAFE_PERMISSION
- ACTIONABLE_STRUCTURE_GAP

## Packet Summary

The packet summary must include:

- total hit count
- count by label
- actionable hit count
- expected hit count
- review required count
- safety boundary preserved flag
- operator review required flag
- sidecar only flag

## Safety Boundary

This sidecar remains:

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

It must not:

- mutate P1-P47 core
- create P48
- mutate source scan files
- delete source scan files
- hide risk flags
- downgrade actionable findings
- allow real trading
- allow broker or exchange API
- allow API keys
- allow wallet private keys
- allow buy / sell / order actions
- tag
- release
- deploy

## D3 Acceptance Criteria

D3 is complete when:

- scan hits can be converted into classification records
- classification records preserve source metadata
- packet summary counts all labels
- actionable hits require review
- expected hits remain visible
- no source mutation is introduced
- no core mutation is introduced
- no tag, release, or deploy is performed
