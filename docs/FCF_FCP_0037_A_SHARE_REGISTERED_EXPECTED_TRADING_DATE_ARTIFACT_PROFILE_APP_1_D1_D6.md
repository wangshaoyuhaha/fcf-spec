# FCF FCP 0037 A Share Registered Expected Trading Date Artifact Profile App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact Artifact Authority

Accept only exact Operator-registered local bytes whose SHA-256 and byte length
match the immutable registration. Require the exact ASCII `trade_date` schema.

## D2 Scope And Revision Lineage

Require explicit XSHG or XSHE market identity, one canonical A-share instrument,
source identity, source revision identity, and declared coverage boundaries.

## D3 Point-In-Time Availability

Require observed, available, registered, revision, and evaluation timestamps in
monotonic UTC order. A future revision fails closed.

## D4 Deterministic Date Set

Require nonempty, ordered, unique, canonical ISO dates whose first and last
values match the declared range. Natural-day and weekday inference are forbidden.

## D5 Rights And Compatibility Boundary

Preserve rights, retention, and local-only usage states. Unresolved rights remain
visible. Conversion to FCP-0036 is explicit and cannot grant provider authority.

## D6 Validation And Closeout

Run the isolated FCP-0037 suite, affected FCP-0036 and governance suite, all FCP
governance tests, full pytest, `scripts/run_all_checks.py`, generated-output
restoration, exact changed-file review, and `git diff --check`. Merge and final
authority synchronization occur only after all validation passes.

Validated before merge:

- FCP-0037 isolated suite: 21 passed
- affected calendar and governance suite: 66 passed
- FCP governance stage suite: 733 passed
- full pytest: 6070 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Evidence commits:

- governance approval: `fb15a36c79d36c257ae687322a9c97b13c7c2953`
- sidecar delivery: `db7f9b764b260072c24f1266667307a5c8c94592`
- main delivery merge: `e66907bf03035ae35cccce88e69083b68388d692`
- post-merge affected suite: 66 passed
