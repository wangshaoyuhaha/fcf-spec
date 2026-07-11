# AI-COMPREHENSIVE-REPORT-CONSUMER-BINDING-APP-1 D5

## State

APPROVED / ACTIVE / D5

## Purpose

Validate deterministic consistency across the Operator Review, UI, and
Report Archive consumer bindings.

## Checked consumers

- OPERATOR-REVIEW-APP-1
- UI-APP-1
- REPORT-ARCHIVE-APP-1

## Identity consistency

Every consumer must preserve the same:

- source app ID
- source module
- source artifact type
- source artifact reference
- source artifact version
- source SHA-256
- correlation ID

## Shared content consistency

Every consumer must preserve the same:

- risk flags
- counterevidence
- alternative explanations
- uncertainty states

The UI and Report Archive visible sections must also remain identical.

## State consistency

- Operator Review decision remains PENDING
- UI decision remains PENDING
- archive decision remains PENDING
- archive status remains PENDING_MANUAL_ARCHIVE
- all bindings remain BOUND_READ_ONLY

## Fail-closed rules

The consistency result becomes BLOCKED when any consumer:

- changes identity
- changes the source hash
- changes the correlation ID
- removes risk flags
- removes counterevidence
- removes alternative explanations
- removes uncertainty
- hides a required UI section
- approves an operator decision automatically
- approves or executes an archive automatically
- writes an archive record
- mutates source data

## Permanent boundary

- deterministic-only
- read-only
- paper-only
- local-only
- sidecar-only
- registered artifacts only
- operator review required
- manual archive authorization required
- no real execution

## Next stage

D6 performs final full-chain validation and phase closeout.
