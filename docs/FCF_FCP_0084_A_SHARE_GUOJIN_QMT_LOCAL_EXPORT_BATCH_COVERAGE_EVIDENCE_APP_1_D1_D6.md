# FCF FCP 0084 A-Share Guojin QMT Local Export Batch Coverage Evidence App 1 D1-D6

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

## D1 Closed Export Evidence Contract

Define immutable sanitized artifact, batch, requested-window, and coverage
review contracts with closed vocabulary and non-authorizing outcomes.

## D2 Bounded Read-Only Scanner

Read existing regular non-symlink ASCII QMT daily export files once, enforce
byte and row bounds, and retain no raw prices, volumes, amounts, or paths.

## D3 Deterministic Batch Topology

Measure exact header, row count, ordered date bounds, duplicates, overlap,
gaps between supplied batches, and repeated observed row-count bounds.

## D4 Fail-Closed Completeness Semantics

Distinguish observed boundaries from requested parameters. Never infer an
exchange calendar, official row cap, pagination, adjustment, or completeness.

## D5 Sanitized Operator Review Packet

Emit canonical ASCII aggregate evidence with source artifacts quarantined and
all promotion, factor, label, provider, and product authority disabled.

## D6 Validation And Closeout

Run isolated, affected A-share evidence, all FCP, full pytest, and all-checks
suites; restore generated outputs; audit exact files, ASCII, hashes, and
`git diff --check`; then commit, push, merge, revalidate, and synchronize.
