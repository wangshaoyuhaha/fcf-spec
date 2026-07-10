# VALIDATION-BASELINE-REGISTRY-APP-1 D1

## Stage

VALIDATION-BASELINE-D1 sidecar boundary and validation baseline registry contract.

## Purpose

Create the validation baseline registry sidecar boundary and contract.

## Scope

D1 defines:

- app identity
- baseline status vocabulary
- required validation baseline fields
- read-only baseline index contract
- validation without fabrication
- operator review required gate

## Allowed baseline statuses

- REGISTERED
- VERIFIED
- INCOMPLETE
- STALE
- UNRESOLVED

## Boundary

Required:

- paper-only
- local-only
- read-only
- sidecar-only
- index-only
- operator review required

Forbidden:

- validation result fabrication
- pass count fabrication
- source artifact mutation
- evidence backfill
- correlation_id auto-fill
- placeholder review generation
- operator review auto-pass
- UI dashboard panel creation
- P1-P47 core mutation
- P48 core expansion
- tag
- release
- deploy
- real trading
- real execution
- broker or exchange connection
- API key
- wallet private key
- real account
- real position
- buy/sell/order
- automatic position sizing
- automatic portfolio action
