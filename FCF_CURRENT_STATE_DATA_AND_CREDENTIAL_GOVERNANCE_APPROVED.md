# FCF Current State - DATA-AND-CREDENTIAL-GOVERNANCE Approved

## Status

APPROVED_NOT_STARTED

## Approved baseline

- branch: main
- parent: 5e49ba1e8a2ee6c93676b434e80db15109b8cefd
- planned branch: sidecar-data-and-credential-governance

## Purpose

Deliver deterministic source-license, data-freshness, and isolated
credential-reference governance over the registered read-only data gateway.
The phase adds policy decisions and Operator-reviewable audit evidence without
network retrieval, secret material, authenticated requests, or execution.

## Required delivery order

- D1 immutable shared governance boundary, policy, decision, and audit contracts
- D2 deterministic source-license registry and fail-closed usage evaluator
- D3 deterministic as-of freshness registry and confidence/block evaluator
- D4 isolated metadata-only credential-reference registry and availability gate
- D5 unified read-only governance service and mandatory Operator review packet
- D6 integration acceptance, closeout, merge validation, and authority sync

## Credential isolation rule

- no credential or secret material may be accepted, stored, revealed, or used
- only opaque credential-reference metadata and availability state are allowed
- no environment-variable, file-secret, wallet, account, vendor, broker, or
  exchange access is authorized
- every decision is read-only, fail-closed, and Operator-reviewable

## Deferred scope

- RESEARCH-GATEWAY-APP-1
- ONLINE-EVIDENCE-TRACEABILITY-APP-1
- any network retrieval, vendor connection, or authenticated request
- FCF-API-GATEWAY-APP-1 and interactive product controls

## Permanent boundary

- P1-P47 frozen and no P48
- paper-only, local-only, loopback-only, sidecar-only
- registered-artifact-only and read-only product presentation
- Operator review mandatory
- Deterministic Engine and Registered Evidence authority preserved
- AI advisory only
- no credential material, account, balance, position, wallet, broker, exchange,
  order, execution, withdrawal, transfer, or real-money path
- no automatic approval, promotion, activation, archive, or learning activation
- no tag, release, or deployment

<!-- DATA-AND-CREDENTIAL-GOVERNANCE APPROVAL -->
