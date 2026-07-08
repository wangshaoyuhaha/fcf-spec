# ARCHIVE-CORRELATION-ROLLUP-APP-1 D1 Contract

## Purpose

ARCHIVE-CORRELATION-ROLLUP-APP-1 builds a read-only Correlation_ID rollup layer across archive, report, final current state, and control center artifacts.

This sidecar does not mutate core logic, trading logic, scoring logic, broker logic, exchange logic, UI action logic, or operator review decisions.

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48
- no core mutation
- no real trading
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## Rollup Scope

The rollup layer may reference these artifact classes:

1. Archive reports
2. Final current state files
3. Control center files
4. Backend handoff files
5. Validation summary files

## Correlation_ID Rule

Every rollup item must preserve:

- correlation_id
- artifact_path
- artifact_type
- source_app
- source_phase
- validation_state
- safety_state
- operator_review_state

## Read Only Rule

The rollup layer must only read artifact metadata and produce derived rollup summaries.

It must not rewrite source artifacts.

## D1 Deliverable

D1 establishes:

- sidecar boundary contract
- rollup item schema
- deterministic validation helper
- baseline tests
