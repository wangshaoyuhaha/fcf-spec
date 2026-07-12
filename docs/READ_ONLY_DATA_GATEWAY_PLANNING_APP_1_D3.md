# READ-ONLY-DATA-GATEWAY-PLANNING-APP-1 D3

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D3 defines deterministic source-policy decisions for validated D2
normalized data envelopes.

## Decision statuses

- CLOUD_ELIGIBLE
- LOCAL_ONLY
- DEGRADED
- BLOCKED

## Policy rules

- invalid D2 envelopes are rejected
- credential scans not CLEAR are BLOCKED
- prohibited use is BLOCKED
- blocked envelopes remain BLOCKED
- restricted use is DEGRADED and local-only
- stale or unknown data remains DEGRADED and local-only
- cloud-disabled valid sources are LOCAL_ONLY
- cloud-approved valid public sources are CLOUD_ELIGIBLE
- runtime activation remains forbidden
- Operator review remains required

## Restrictions

- planning-only
- no live source connection
- no credential access
- no database write
- no model invocation
- no Prompt execution
- no automatic routing
- no archive writing
- no Core mutation
- no P48
- no real execution
- no tag
- no release
- no deployment