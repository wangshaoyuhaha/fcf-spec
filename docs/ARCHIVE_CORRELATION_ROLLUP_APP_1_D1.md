# ARCHIVE-CORRELATION-ROLLUP-APP-1 D1

## Stage

ARCHIVE-CORRELATION-D1 sidecar boundary and correlation rollup contract.

## Purpose

Upgrade correlation_id from field preservation into a read-only full-chain evidence index.

## Boundary

- sidecar-only
- read-only
- local-only
- paper-only
- index-only
- no core mutation
- no P48
- no tag
- no release
- no deploy

## Required Evidence Links

The rollup contract indexes these existing links only:

1. data_snapshot
2. candidate
3. ai_explanation
4. ui_packet
5. review_packet
6. archive_packet
7. handoff
8. final_state

## Missing Chain Policy

Missing or broken chain evidence must be marked only:

- INCOMPLETE
- STALE
- UNRESOLVED

The sidecar must not backfill evidence.

## Explicitly Forbidden

- auto-pass
- auto-fill correlation_id
- placeholder review generation
- UI dashboard panel creation
- core mutation
- trade execution
- broker or exchange API
- API key
- wallet private key
- real account
- real position
- buy/sell/order
- automatic position sizing
- automatic portfolio action

## D1 Deliverables

- sidecar package boundary
- immutable rollup contract builder
- D1 regression tests
