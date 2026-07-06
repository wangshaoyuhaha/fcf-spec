# WATCHLIST-LIFECYCLE-D1 Boundary Contract

## Purpose

WATCHLIST-LIFECYCLE-APP-1 is a paper-only local watchlist lifecycle management sidecar.

It reads prior sidecar outputs and creates a local paper lifecycle contract for watchlist states.

## Read sources

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

## May generate

- watchlist_lifecycle_contract
- watchlist_lifecycle_source_manifest
- watchlist_lifecycle_state_schema
- watchlist_lifecycle_packet
- watchlist_lifecycle_final_handoff

## Lifecycle states

- ENTRY_REVIEW
- ACTIVE_WATCH
- REVIEW_REQUIRED
- STALE_REVIEW
- DROP_REVIEW

## Required boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

## Forbidden scope

- no P48 core expansion
- no P1-P47 core mutation
- no source content mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
- no real trading
- no real execution
- no broker connection
- no exchange connection
- no API key storage
- no wallet private key access
- no real account access
- no real position access
- no buy button
- no sell button
- no order button
- no automatic position sizing
- no automatic portfolio action
- no future return prediction
- no guaranteed performance claim
- no tag
- no release
- no deploy

## D1 status

This file defines the D1 sidecar boundary only.
It does not load source records, score candidates, mutate inputs, or generate lifecycle packets.
