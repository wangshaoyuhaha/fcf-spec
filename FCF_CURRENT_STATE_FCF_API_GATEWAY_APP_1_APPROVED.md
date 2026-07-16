# FCF Current State - FCF-API-GATEWAY-APP-1 Approved

## Status

APPROVED_NOT_STARTED

## Approved baseline

- branch: main
- parent: e3cf199d41fa0ae66469e859e4235409bf3ea4b0
- planned branch: sidecar-fcf-api-gateway-app-1

## Purpose

Deliver a deterministic loopback-only API policy boundary with registered local
process identity, authorization, schemas, correlation, idempotency, budgets,
audit emission, and fail-closed dispatch. No secret material or external
network exposure is introduced.

## Required delivery order

- D1 immutable loopback API boundary, request, response, and route contracts
- D2 registered local-principal authentication, authorization, policy, and schema gates
- D3 deterministic correlation and idempotency ledger
- D4 deterministic rate and declared-cost budget enforcement
- D5 fail-closed dispatch service, audit emission, and Operator review packet
- D6 integration acceptance, closeout, merge validation, and authority sync

## Permanent boundary

- P1-P47 frozen and no P48
- paper-only, local-only, loopback-only, sidecar-only
- read-only routes and mandatory Operator review
- no password, API key, bearer token, credential file, environment secret,
  external binding, public API, account, order, or execution path
- no tag, release, or deployment

<!-- FCF-API-GATEWAY-APP-1 APPROVAL -->
