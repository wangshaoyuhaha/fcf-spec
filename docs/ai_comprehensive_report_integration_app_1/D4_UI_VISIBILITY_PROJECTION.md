# AI-COMPREHENSIVE-REPORT-INTEGRATION-APP-1 D4

## State

APPROVED / ACTIVE / D4

## Purpose

Create a read-only UI visibility packet from the validated operator
review packet.

## Consumer

UI-APP-1

## Mandatory visible sections

- source statements
- original conclusions
- risk flags
- counterevidence
- alternative explanations
- uncertainty states

## Visibility requirements

Every section must remain visible.

The UI projection cannot:

- suppress risk flags
- suppress counterevidence
- suppress alternative explanations
- suppress uncertainty states
- replace source content with a summary
- rewrite source meaning
- downgrade review status
- invent a probability
- select a winner
- approve a conclusion
- complete operator review

## Review banner

The UI must display:

- review status: REVIEW_REQUIRED
- operator decision: PENDING
- operator review required: true
- automatic approval allowed: false

## Decision state

- causal truth: UNDETERMINED
- probability: NOT_ASSIGNED
- winner: NOT_SELECTED
- operator decision: PENDING

## Derived metadata

D4 may derive only deterministic item counts.

Counts cannot replace visible source content.

## Permanent boundary

- P1-P47 core frozen
- no P48
- no core mutation
- paper-only
- local-only
- read-only
- sidecar-only
- registered artifacts only
- deterministic only
- operator review required
- no runtime model invocation
- no prompt execution
- no automatic routing
- no real execution
- no tag
- no release
- no deploy

## Next stage

D5 may add a manual-only report archive projection after D4 validation,
commit, push, and clean status.
