# READ-ONLY-DATA-GATEWAY-PLANNING-APP-1 D2

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D2 defines a deterministic metadata-only normalized data envelope.

## Envelope scope

- source identity and evidence identity
- SHA-256 checksum
- source class and trust level
- publication and retrieval timestamps
- freshness classification
- licensing and allowed-use controls
- cloud-processing permission
- retention, redistribution, and training controls
- payload reference without unrestricted payload writing
- normalization and credential-scan status
- BLOCKED and DEGRADED reasons

## Fail-closed rules

- detected credentials: BLOCKED
- credential scan not run: BLOCKED
- prohibited source use: BLOCKED
- blocked normalization: BLOCKED
- unknown or stale metadata: DEGRADED
- restricted source use: DEGRADED

## Restrictions

- planning-only
- no live data source connection
- no database write
- no unrestricted file write
- no credential access
- no balance or position access
- no wallet access
- no model invocation
- no Prompt execution
- no automatic routing
- no archive writing
- no Core mutation
- no real execution
