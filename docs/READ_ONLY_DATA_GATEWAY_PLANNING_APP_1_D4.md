# READ-ONLY-DATA-GATEWAY-PLANNING-APP-1 D4

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D4 defines the planning-only credential-isolation boundary for the
future Read-Only Data Gateway.

## Credential authority

- credential owner: isolated read-only gateway
- credential storage remains outside FCF
- FCF receives normalized, redacted, evidence-linked data only
- Operator review remains required

## Prohibited exposure

- no credential material inside FCF
- no credential material in model input
- no credential material in model output
- no raw secret export
- no balance access
- no position access
- no wallet access
- no database write
- no real execution

## Restrictions

- planning-only
- no real credential access
- no live vendor connection
- no broker or exchange API
- no model invocation
- no Prompt execution
- no automatic routing
- no archive writing
- no Core mutation
- no P48
- no tag
- no release
- no deployment