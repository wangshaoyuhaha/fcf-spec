# SIDECAR-TOPOLOGY-REVIEW-APP-1 D4 Dependency DAG Review

Status: D4 dependency DAG and circular dependency review completed.

## Purpose

This document defines the completed sidecar dependency DAG review.

The goal is to prevent circular dependency, backward mutation, review bypass, and UI-driven governance drift.

## DAG direction

The allowed topology direction is:

Data Ingestion and Quarantine
-> Context and Interpretation
-> Governance and Review Gate
-> Presentation and Immutable Archive

## Dependency edges

| From | To | Edge type |
| --- | --- | --- |
| DATA-QUALITY-OPS-APP-1 | STOCK-APP-1 | validated data quality input |
| STOCK-APP-1 | AI-CONTEXT-1 | ranked watchlist context input |
| DATA-QUALITY-OPS-APP-1 | AI-CONTEXT-1 | data quality context input |
| AI-CONTEXT-1 | MARKET-SCENARIO-APP-1 | explanation and scenario context |
| MARKET-SCENARIO-APP-1 | SIGNAL-VALIDATION-APP-1 | scenario signal review input |
| MODEL-GOVERNANCE-APP-1 | SIGNAL-VALIDATION-APP-1 | model governance constraint input |
| SIGNAL-VALIDATION-APP-1 | BACKTEST-REVIEW-APP-1 | signal validation review input |
| BACKTEST-REVIEW-APP-1 | OPERATOR-REVIEW-APP-1 | backtest limitation review input |
| OPERATOR-REVIEW-APP-1 | UI-APP-1 | reviewed operator output |
| OPERATOR-REVIEW-APP-1 | REPORT-ARCHIVE-APP-1 | reviewed archive output |
| UI-APP-1 | DIFY-UI-HANDOFF-APP-1 | manual UI handoff input |
| REPORT-ARCHIVE-APP-1 | DIFY-UI-HANDOFF-APP-1 | archive and report handoff input |
| SIDECAR-TOPOLOGY-REVIEW-APP-1 | OPERATOR-REVIEW-APP-1 | governance review input |

## Circular dependency rules

The following rules are mandatory:

- Presentation sidecars must not feed source mutations back into data sidecars.
- Archive sidecars must not modify reviewed artifacts after closeout.
- UI sidecars must not downgrade or hide risk flags.
- Dify handoff sidecars must not write into Dify through an API.
- Governance sidecars must not bypass operator review.
- Backtest review must not be interpreted as real trading approval.
- Topology review must not create feature execution authority.

## Forbidden reverse edges

The following reverse edges are forbidden:

| From | To | Reason |
| --- | --- | --- |
| UI-APP-1 | STOCK-APP-1 | UI must not mutate stock candidate generation |
| DIFY-UI-HANDOFF-APP-1 | AI-CONTEXT-1 | manual UI handoff must not mutate explanation logic |
| REPORT-ARCHIVE-APP-1 | SIGNAL-VALIDATION-APP-1 | immutable archive must not mutate validation logic |
| OPERATOR-REVIEW-APP-1 | DATA-QUALITY-OPS-APP-1 | review output must not mutate data quality source |
| BACKTEST-REVIEW-APP-1 | MODEL-GOVERNANCE-APP-1 | backtest output must not rewrite governance rules |
| SIDECAR-TOPOLOGY-REVIEW-APP-1 | core P1-P47 | topology review must not mutate frozen core |

## DAG review result

The reviewed dependency model is acyclic when the allowed direction is enforced.

No completed sidecar is allowed to create a reverse write dependency.

Future sidecars must declare:

- upstream artifacts
- downstream artifacts
- write boundary
- read boundary
- operator review gate
- rollback path
- final current-state file

## Safety boundary

This DAG review preserves:

- paper-only
- local-only
- read-only
- governance-only
- operator-review-only
- no P48
- no core mutation
- no broker API
- no exchange API
- no wallet API
- no real account
- no real order
- no real execution
- no real balance or position read
- no real money impact
- no automatic Dify app creation
- no Dify API write
- no deploy
- no release
- no tag

## D4 result

The dependency DAG review is established.

D5 must define the future sidecar queue and governance gates.
