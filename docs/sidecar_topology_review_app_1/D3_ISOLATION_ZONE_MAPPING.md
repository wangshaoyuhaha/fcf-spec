# SIDECAR-TOPOLOGY-REVIEW-APP-1 D3 Isolation Zone Mapping

Status: D3 isolation zone mapping completed.

## Purpose

This document maps completed FCF sidecars into isolation zones.

The mapping is governance-only and does not start feature development.

## Isolation zones

The FCF sidecar topology uses four isolation zones:

1. Data Ingestion and Quarantine
2. Context and Interpretation
3. Governance and Review Gate
4. Presentation and Immutable Archive

## Zone 1: Data Ingestion and Quarantine

Purpose:

- receive external or derived data artifacts
- validate input quality
- quarantine unsafe or low-confidence records
- prevent raw data from directly driving operator-facing outputs

Mapped sidecars:

- DATA-QUALITY-OPS-APP-1
- STOCK-APP-1

Primary risks:

- stale input data
- incomplete input data
- unvalidated anomaly signals
- raw market data over-trust

Required gates:

- data quality gate
- source freshness gate
- anomaly explanation gate
- operator review gate

## Zone 2: Context and Interpretation

Purpose:

- transform validated data into explainable context
- attach reason codes
- attach risk flags
- preserve explanation traceability

Mapped sidecars:

- AI-CONTEXT-1
- MARKET-SCENARIO-APP-1
- MODEL-GOVERNANCE-APP-1
- SIGNAL-VALIDATION-APP-1

Primary risks:

- unsupported explanation
- hidden risk flags
- weak reason-code traceability
- scenario over-interpretation

Required gates:

- reason-code gate
- risk-flag visibility gate
- scenario review gate
- model governance gate

## Zone 3: Governance and Review Gate

Purpose:

- preserve operator review authority
- prevent automated action
- enforce safety boundaries
- review outputs before any downstream presentation or archive

Mapped sidecars:

- OPERATOR-REVIEW-APP-1
- BACKTEST-REVIEW-APP-1
- SIDECAR-TOPOLOGY-REVIEW-APP-1

Primary risks:

- review bypass
- false confidence from backtest outputs
- governance drift
- circular dependency in review flow

Required gates:

- operator review gate
- backtest limitation gate
- topology dependency gate
- no-auto-action gate

## Zone 4: Presentation and Immutable Archive

Purpose:

- present reviewed outputs
- preserve immutable review artifacts
- support manual Dify/Ollama UI handoff
- prevent UI from hiding or downgrading risk flags

Mapped sidecars:

- UI-APP-1
- REPORT-ARCHIVE-APP-1
- DIFY-UI-HANDOFF-APP-1

Primary risks:

- UI hides risk flags
- UI downgrades reason codes
- archive lacks correlation traceability
- manual UI handoff is misunderstood as deployment

Required gates:

- risk-flag display gate
- reason-code display gate
- archive traceability gate
- no-deploy confirmation gate

## Cross-zone rule

Sidecars may pass artifacts forward across zones, but later zones must not mutate earlier-zone source artifacts.

Allowed direction:

Data Ingestion and Quarantine
-> Context and Interpretation
-> Governance and Review Gate
-> Presentation and Immutable Archive

Disallowed direction:

Presentation and Immutable Archive
-> Governance and Review Gate
-> Context and Interpretation
-> Data Ingestion and Quarantine

## Safety boundary

This mapping preserves:

- paper-only
- local-only
- read-only
- governance-only
- operator-review-only
- no P48
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

## D3 result

The four-zone sidecar isolation model is established.

D4 must review dependency DAG and circular dependency risks.
