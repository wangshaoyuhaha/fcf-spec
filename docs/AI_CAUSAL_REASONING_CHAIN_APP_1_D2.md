# AI-CAUSAL-REASONING-CHAIN-APP-1 D2

## Stage

AI-CAUSAL-REASONING-CHAIN-D2

## Purpose

Define registered schemas for causal claims, premises, supporting
evidence, counterevidence, and alternative explanations.

D2 records supplied artifacts only.

It does not create missing claims or evidence.

## Registered premise record

Each premise records:

- premise identifier
- parent claim identifier
- registered premise text
- registration status
- source artifact identifiers
- correlation identifier
- research run identifier
- operator review requirement
- source preservation state

## Registered evidence reference

Each evidence reference records:

- evidence reference identifier
- parent claim identifier
- source artifact identifier
- registered artifact type
- evidence role
- relation type
- registration status
- correlation identifier
- research run identifier
- operator review requirement
- source preservation state

Evidence roles are:

- SUPPORTING
- COUNTEREVIDENCE
- ALTERNATIVE_EXPLANATION

## Registered causal claim record

Each claim records:

- registered claim text
- cause reference
- effect reference
- claim type
- claim registration status
- registered premises
- registered evidence references
- explicit counterevidence review status
- explicit alternative explanation review status
- deterministic reason codes
- deterministic record status
- correlation identifier
- research run identifier

## Interpretation boundary

Every claim retains:

- causal truth status: UNDETERMINED
- probability status: NOT_ASSIGNED
- winner status: NOT_SELECTED
- operator review status: REQUIRED
- source artifacts: PRESERVED
- original conclusions: PRESERVED

A recorded claim is not a confirmed causal relationship.

A missing counterevidence record is not proof that no counterevidence
exists.

A missing alternative explanation is not proof that no alternative
exists.

## Review states

Claim records may be:

- RECORDED
- REVIEW_REQUIRED
- BLOCKED

Review reasons include:

- missing premises
- missing supporting evidence
- counterevidence not reviewed
- alternative explanation not reviewed
- blocked registered evidence
- blocked registered premises
- claim registration review requirement

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
- no missing claim creation
- no missing evidence creation
- no causality inference from correlation
- no automatic causal truth decision
- no probability assignment
- no winner selection
- no conclusion replacement
- no source artifact mutation
- no live model invocation
- no prompt execution
- no runtime orchestrator execution
- no automatic routing
- no automatic role switching
- no trade action
- no real execution
- no tag
- no release
- no deploy
