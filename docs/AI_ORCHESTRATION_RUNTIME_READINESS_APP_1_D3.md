# AI-ORCHESTRATION-RUNTIME-READINESS-APP-1 D3

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D3 provides deterministic routing eligibility contracts.

It evaluates whether a registered candidate is eligible for Operator review,
BLOCKED, or DEGRADED. It does not select or execute a route.

## Required Evidence

- registered role contract
- registered model version
- registered Prompt version
- policy identifier, version, and digest
- Config Snapshot identifier
- privacy permission
- licensing permission
- provider health
- cost-limit status

## Fail-Closed Rules

A candidate becomes BLOCKED when registered evidence is missing, privacy or
licensing policy blocks use, the provider is unavailable, or the cost limit
is exceeded.

A candidate becomes DEGRADED when provider health is degraded or cost status
is unknown.

## Permanent Restrictions

- no automatic routing
- no route selection
- no winner selection
- no model invocation
- no Prompt execution
- no runtime execution
- no Operator bypass
- no Core mutation
