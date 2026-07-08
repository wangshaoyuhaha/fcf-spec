# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D3 Dependency Graph Repair

## Purpose

This repair fixes the default sidecar dependency graph after D2.

## Repairs

1. REPORT-ARCHIVE-APP-1 is archive_audit, not data_foundation.
2. UI-APP-1 -> OPERATOR-REVIEW-APP-1 is explicitly allowed.
3. OPERATOR-REVIEW-APP-1 -> REPORT-ARCHIVE-APP-1 is explicitly allowed.

## Reason

UI-APP-1 produces a read-only local report artifact.
OPERATOR-REVIEW-APP-1 consumes that artifact for paper-only human review.
REPORT-ARCHIVE-APP-1 archives completed review artifacts.

These edges are read-only artifact handoffs.
They are not core mutation, source mutation, score mutation, risk flag deletion, real trading, release, or deploy actions.

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no source mutation
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no real execution
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy
