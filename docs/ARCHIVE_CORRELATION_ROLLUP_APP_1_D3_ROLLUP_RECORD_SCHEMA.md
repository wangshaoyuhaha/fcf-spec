# ARCHIVE-CORRELATION-ROLLUP-APP-1 D3 Rollup Record Schema

## Purpose

D3 defines the deterministic rollup record schema for Correlation_ID tracing across archive, report, final current state, and control center artifacts.

## Record Goal

A rollup record connects one source artifact to a stable Correlation_ID and preserves enough metadata for later audit review.

## Required Fields

- correlation_id
- artifact_path
- artifact_type
- source_app
- source_phase
- validation_state
- safety_state
- operator_review_state
- rollup_scope
- trace_state

## Rollup Scope Values

- archive
- report
- final_current_state
- control_center
- handoff
- validation

## Trace State Values

- trace_ready
- trace_partial
- trace_blocked

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

## D3 Output

D3 adds deterministic rollup record builders and schema validation tests.
