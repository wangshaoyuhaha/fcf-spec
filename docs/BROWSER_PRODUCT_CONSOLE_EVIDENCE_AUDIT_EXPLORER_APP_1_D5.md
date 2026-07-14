# BROWSER-PRODUCT-CONSOLE-EVIDENCE-AUDIT-EXPLORER-APP-1 D5

## Status

COMPLETED_ON_SIDECAR

## Scope

D5 connects all seven Evidence Audit Explorer routes to the governed local
Browser Product Console and adds deterministic filtering, integrity visibility,
failure-closed query handling, and integration acceptance.

## Delivered routes

- /evidence
- /evidence/artifacts
- /evidence/lineage
- /evidence/risk
- /evidence/validation
- /evidence/review
- /evidence/archive

## Query contract

Allowed query parameters:

- correlation_id
- artifact_ids
- artifact_types
- integrity_states
- risk_flags
- contradiction_codes
- offset
- limit
- sort_order

Array parameters may be repeated. Scalar parameters must not be repeated.
Queries are bounded to 2048 characters and 100 parameter pairs. Pagination is
bounded by the D1 contract.

Unsupported, blank, malformed, unsafe, duplicate scalar, invalid percent
encoding, traversal-like, and unbounded query values fail closed with HTTP 400
and the explicit REJECTED_QUERY state.

## Integrity and evidence visibility

The explorer displays only registered artifact identities already loaded by the
Browser Product Console artifact index:

- artifact_id
- artifact_type
- correlation_id
- registered relative_path
- content_sha256
- verified integrity state
- explicit risk flags
- explicit contradiction codes
- typed registered relationships
- Paper Validation evidence
- Shadow Observation evidence
- Operator review evidence
- Report Archive evidence
- AI evidence identity and metadata

No unregistered file is loaded and no free-text warning is converted into risk
or contradiction evidence.

## Integration acceptance

The immutable acceptance verifies:

- exact seven-route registry
- unique routes
- GET 200 for all routes
- HEAD 200 with empty bodies
- POST, PUT, PATCH, and DELETE rejected with 405
- malformed queries rejected with 400
- valid deterministic query behavior
- unknown and traversal routes rejected with 404
- registered artifact identities match the read model
- registered SHA-256 values remain visible
- no-store cache policy
- nosniff content type policy
- content security policy
- complete navigation
- no form, button, method, or script mutation controls
- paper-only health state
- loopback-only health state
- mandatory Operator review
- Deterministic Engine authority
- AI advisory-only boundary

## Permanent boundary

- P1-P47 frozen
- no P48
- paper-only
- local-only
- loopback-only
- sidecar-only
- registered-artifact-only
- read-only product presentation
- Operator review mandatory
- Deterministic Engine authority preserved
- Registered Evidence remains evidence authority
- AI advisory only
- no evidence mutation
- no source artifact mutation
- no record deletion
- no command or workflow dispatch
- no public network exposure
- no external data fetching
- no broker, exchange, credentials, account, balance, position, wallet,
  order, or real execution path
- no automatic approval, promotion, baseline replacement, model activation,
  Prompt activation, learning activation, or archive
- no tag, release, or deployment

D6 performs final acceptance, closeout, main merge, and authority
synchronization. Runtime Hardening remains a separate successor phase requiring
explicit approval.
