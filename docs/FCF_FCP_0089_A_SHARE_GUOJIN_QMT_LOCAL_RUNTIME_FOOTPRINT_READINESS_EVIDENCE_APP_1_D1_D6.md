# FCF FCP 0089 A-Share Guojin QMT Local Runtime Footprint Readiness Evidence App 1 D1-D6

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

## D1 Exact Local Directory Registration

Require one existing Operator-designated regular local directory, a safe
artifact identity, exact directory kind, and bounded scan policy.

## D2 Bounded Metadata-Only Scan

Inspect top-level directory entries only. Reject symlinks and reparse points,
enforce a closed entry limit, and never read file contents or recurse.

## D3 Closed Footprint Classification

Classify only registered required directories and cache families. Preserve
counts, aggregate regular-file bytes, latest metadata time, and one canonical
manifest hash without arbitrary names or paths.

## D4 Fail-Closed Readiness Evidence

Emit READY_FOR_OPERATOR_PROBE only when every required footprint class exists.
Keep terminal liveness, entitlement, rights, market-data availability, and
all data-quality claims unproven.

## D5 Authority Boundary

Keep GAP-104 open. No SDK, network, credentials, account, provider selection,
realtime activation, data promotion, product, factor, signal, order, or
execution authority is created.

## D6 Validation And Closeout

Run isolated, affected A-share and governance, all FCP, full pytest, and
all-checks suites; restore generated outputs; audit exact files, ASCII, hashes,
and `git diff --check`; then commit, push, merge, revalidate, and synchronize.
