# FCF FCP 0084 A-Share Guojin QMT Local Export Batch Coverage Evidence App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Closed Export Evidence Contract

Define immutable sanitized artifact, batch, requested-window, and coverage
review contracts with closed vocabulary and non-authorizing outcomes. Reuse
FCP-0035 and FCP-0036 rather than creating a parallel parser or merger.

## D2 Bounded Read-Only Scanner

Require existing regular non-symlink registered QMT daily export files and
delegate byte verification, parsing, and normalization to FCP-0035. Retain no
raw prices, normalized rows, volumes, amounts, or paths in the packet.

## D3 Deterministic Batch Topology

Preserve FCP-0035 manifest hashes, row counts, actual date bounds, requested
range mismatches, and repeated observed row-count bounds.

## D4 Fail-Closed Completeness Semantics

Distinguish observed boundaries from requested parameters. Without a
registered expected-date artifact, do not invoke or imitate FCP-0036. Never
infer an exchange calendar, official row cap, pagination, or completeness.

## D5 Sanitized Operator Review Packet

Emit canonical ASCII aggregate evidence with source artifacts quarantined and
all promotion, factor, label, provider, and product authority disabled.

## D6 Validation And Closeout

Run isolated, affected A-share evidence, all FCP, full pytest, and all-checks
suites; restore generated outputs; audit exact files, ASCII, hashes, and
`git diff --check`; then commit, push, merge, revalidate, and synchronize.
