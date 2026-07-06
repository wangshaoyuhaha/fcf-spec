# SIGNAL-VALIDATION-APP-1 D2 Source Loader

## Stage

SIGNAL-VALIDATION-D2

## Purpose

D2 adds a read-only local source packet loader for SIGNAL-VALIDATION-APP-1.

The loader inspects metadata and bounded previews from completed sidecar state files.
It does not mutate source content, delete source content, overwrite source content,
repair source files, execute trades, or connect to external systems.

## Read-only source targets

- STOCK-APP-1 current state
- AI-CONTEXT-1 current state
- OPERATOR-REVIEW-APP-1 final state
- REPORT-ARCHIVE-APP-1 final state
- DATA-QUALITY-OPS-APP-1 final state
- MARKET-SCENARIO-APP-1 final state
- BACKTEST-REVIEW-APP-1 final state

## Loader status values

- ALL_CONFIGURED_SOURCES_AVAILABLE
- PARTIAL_SOURCE_AVAILABLE
- NO_SOURCE_AVAILABLE
- BLOCKED_MISSING_REQUIRED_SOURCE

## Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no source mutation
- no source deletion
- no source overwrite
- no real execution
- no trade action
