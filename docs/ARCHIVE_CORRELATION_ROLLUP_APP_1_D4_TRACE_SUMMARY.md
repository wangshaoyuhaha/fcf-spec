# ARCHIVE-CORRELATION-ROLLUP-APP-1 D4 Trace Summary

## Purpose

D4 builds a read-only trace summary for Correlation_ID rollup records.

The trace summary answers:

- which Correlation_ID exists
- which artifact classes are covered
- which source apps are represented
- whether any trace is partial or blocked
- whether operator review is still required

## Summary Fields

- correlation_id
- record_count
- artifact_types
- source_apps
- rollup_scopes
- trace_states
- has_blocked_trace
- has_partial_trace
- operator_review_required
- summary_state

## Summary State

- complete
- partial
- blocked

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48
- no core mutation
- no source mutation
- no source deletion
- no source overwrite
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

## D4 Output

D4 adds deterministic trace summary builders and tests.
