# ARCHIVE-CORRELATION-ROLLUP-APP-1 D2 Source Discovery

## Purpose

D2 adds read-only source discovery for Correlation_ID rollup inputs.

The discovery layer identifies eligible project artifacts without mutating them.

## Eligible Artifact Classes

- final_current_state
- control_center
- archive_report
- backend_handoff
- validation_summary
- project_prompt

## Discovery Rules

1. Source files are discovered from repository paths only.
2. Source files are not rewritten.
3. Runtime files are not rollup source of truth.
4. Control center is treated as governance source.
5. Final current state files are treated as phase completion source.
6. Archive and audit reports are treated as evidence source.
7. Backend handoff files are treated as continuity source.

## Safety Rules

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

## D2 Output

D2 provides deterministic artifact discovery helpers and tests.
