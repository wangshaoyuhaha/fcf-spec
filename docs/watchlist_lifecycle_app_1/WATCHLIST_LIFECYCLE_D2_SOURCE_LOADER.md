# WATCHLIST-LIFECYCLE-D2 Source Loader

## Purpose

D2 adds a read-only local source metadata loader for WATCHLIST-LIFECYCLE-APP-1.

The loader builds metadata records for prior sidecar outputs so later stages can decide whether a watchlist lifecycle packet has enough local source context.

## Sources represented

- DATA-APP-1
- STOCK-APP-1
- AI-CONTEXT-1
- UI-APP-1
- OPERATOR-REVIEW-APP-1
- REPORT-ARCHIVE-APP-1
- DATA-QUALITY-OPS-APP-1
- MARKET-SCENARIO-APP-1
- BACKTEST-REVIEW-APP-1
- SIGNAL-VALIDATION-APP-1
- MODEL-GOVERNANCE-APP-1

## Metadata only

D2 records:

- app_id
- source_kind
- relative_path
- exists
- status
- path_type
- size_bytes
- file_count
- sha256 for files only
- modified_at_utc

D2 does not return source content.

## Required boundary

- read_only = true
- content_loaded = false
- source_content_mutation_allowed = false
- source_deletion_allowed = false
- source_overwrite_allowed = false
- score_mutation_allowed = false
- reason_code_mutation_allowed = false
- risk_flag_deletion_allowed = false
- trade_action_allowed = false
- real_execution_allowed = false
- operator_review_required = true

## D2 status

This stage only creates source metadata loading and validation.
It does not create lifecycle decisions, review states, trading actions, position sizing, portfolio actions, or performance claims.
