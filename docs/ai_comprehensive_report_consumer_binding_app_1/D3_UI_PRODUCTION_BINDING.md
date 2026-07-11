# AI-COMPREHENSIVE-REPORT-CONSUMER-BINDING-APP-1 D3

## State

APPROVED / ACTIVE / D3

## Purpose

Bind the validated comprehensive report integration chain to the
UI-APP-1 production consumer boundary.

## Required visible sections

- SOURCE_STATEMENTS
- ORIGINAL_CONCLUSIONS
- RISK_FLAGS
- COUNTEREVIDENCE
- ALTERNATIVE_EXPLANATIONS
- UNCERTAINTY_STATES

Every required section must remain visible.

## Required visible state

- display status: VISIBLE_READ_ONLY
- review status: REVIEW_REQUIRED
- operator decision: PENDING
- causal truth: UNDETERMINED
- probability: NOT_ASSIGNED
- winner: NOT_SELECTED

## Preserved identity

- source app ID
- source module
- source artifact type
- source artifact reference
- source artifact version
- source SHA-256
- correlation ID

## Forbidden behavior

- hiding risk flags
- hiding counterevidence
- hiding alternative explanations
- hiding uncertainty
- replacing the report with a summary
- semantic rewrite
- source mutation
- automatic approval
- runtime model invocation
- prompt execution
- automatic routing
- real execution
- tag
- release
- deployment

## Next stage

D4 binds the same registered chain to the REPORT-ARCHIVE-APP-1
production consumer while preserving manual archive authorization.
