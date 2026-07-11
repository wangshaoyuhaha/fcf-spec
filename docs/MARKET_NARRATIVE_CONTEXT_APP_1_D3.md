# MARKET-NARRATIVE-CONTEXT-APP-1 D3

## Purpose

Implement deterministic narrative-to-research artifact linkage rules.

## Linkage inputs

- narrative artifact identifier
- target research artifact identifier
- correlation identifiers
- research run identifiers
- asset types
- symbols
- evidence reference identifiers

## Deterministic matching

The linkage evaluator checks:

- correlation ID equality
- research run ID equality
- asset type equality
- symbol equality
- shared evidence references

Asset type and symbol comparisons are case-insensitive.
Artifact and provenance identifiers remain exact.

## Dispositions

LINKED:

- identity metadata matches
- at least one evidence reference is shared
- operator review is still required

REVIEW_REQUIRED:

- identity metadata matches
- no evidence reference is shared

BLOCKED:

- correlation ID mismatch
- research run ID mismatch
- asset type mismatch
- symbol mismatch

## Important meaning

LINKED means metadata linkage only.

LINKED does not mean:

- the narrative is true
- the target conclusion is correct
- evidence is sufficient
- risk is resolved
- an operator review may be bypassed
- a trading action is authorized

Truth status remains UNDETERMINED.

## Permanent boundary

- P1-P47 core frozen
- no P48
- no core mutation
- paper-only
- local-only
- read-only
- sidecar-only
- deterministic-only
- registered artifacts only
- operator review required
- original conclusions preserved
- no live model invocation
- no prompt execution
- no automatic truth decision
- no automatic conclusion replacement
- no operator review bypass
- no trade action
- no real execution
- no broker or exchange connection
- no API keys
- no wallet keys
- no tag
- no release
- no deploy

## D3 status

The deterministic linkage request, validation rules, dispositions,
reason codes, risk flags, and tests are implemented.
