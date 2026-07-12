# AI-ORCHESTRATION-RUNTIME-READINESS-APP-1 D4

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D4 provides deterministic readiness-only timeout, retry, fallback, and cost
contracts.

These contracts describe limits and fail-closed behavior. They do not execute
models, Prompts, routes, retries, fallbacks, or cost overrides.

## Timeout Contract

- positive connection, response, and total time budgets
- total time must cover connection plus response budgets
- timeout action is BLOCK and require Operator review
- automatic timeout recovery is not allowed

## Retry Contract

- retry attempts are bounded from zero to three
- backoff values are explicit and ordered
- retryable failure classes are machine-readable
- automatic retry execution is not allowed

## Fallback Contract

- fallback candidates must exist in the routing contract
- fallback options are presented to the Operator
- automatic fallback and automatic switching are not allowed

## Cost Contract

- integer microunit limits avoid floating-point ambiguity
- per-request, workflow, and daily limits are ordered
- unknown cost and exceeded cost both BLOCK
- automatic cost override is not allowed

## Permanent Restrictions

- no model invocation
- no Prompt execution
- no automatic routing
- no automatic retry
- no automatic fallback
- no runtime execution
- no Operator bypass
- no Core mutation
