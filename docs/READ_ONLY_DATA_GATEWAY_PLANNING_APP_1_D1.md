# READ-ONLY-DATA-GATEWAY-PLANNING-APP-1 D1

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D1 defines the planning-only boundary contract for a future Read-Only Data
Gateway.

## Allowed Planning Scope

- file upload
- public-data retrieval
- approved market-data retrieval
- approved research retrieval
- approved database SELECT operations
- approved archive lookup
- approved evidence lookup
- normalized evidence-linked output planning

## Required Governance Metadata

- source identity and class
- trust level
- publication and retrieval timestamps
- evidence identifier
- checksum
- freshness status
- licensing and allowed-use fields
- cloud-processing permission
- retention, redistribution, and training permissions

## Fail-Closed Defaults

Unknown licensing blocks cloud processing, training, and redistribution.

Unknown freshness remains UNKNOWN and becomes DEGRADED or BLOCKED according
to deterministic policy.

## Prohibited Scope

- no database INSERT, UPDATE, or DELETE
- no unrestricted file writing
- no order placement
- no balance or position retrieval
- no wallet or private-key access
- no credential exposure
- no model invocation
- no Prompt execution
- no automatic routing
- no archive writing
- no Core mutation
- no P48
- no real execution
- no tag, release, or deployment
