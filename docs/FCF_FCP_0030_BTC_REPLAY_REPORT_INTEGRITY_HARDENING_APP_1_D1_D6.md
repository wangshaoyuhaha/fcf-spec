# FCF FCP 0030 BTC Replay Report Integrity Hardening App 1 D1-D6

Status: COMPLETED_VALIDATED_PENDING_MERGE

## D1 Typed Replay Evidence

Replay reports accept only concrete book states, manifests, findings, and
registered latest-observation types.

## D2 Closed Manifest Contract

Replay manifests require exact lowercase SHA-256 values, one closed replay
layer, UTC replay clocks, and complete unique observation ID and digest pairs.

## D3 Deterministic Book State

Book state requires strict nonnegative integer clocks, concrete levels,
descending bids, ascending asks, and complete noncrossed synchronized depth.

## D4 Report Lineage and Authority

Accepted IDs agree exactly with manifest IDs, latest observation digests agree
with their paired manifest digests, the book hash agrees with the manifest,
and calculation, evidence, AI, and Operator-review identities remain exact.

## D5 Result Commitment and Regression Guard

The deterministic report hash commits to accepted IDs, book state, findings,
latest observation digests, and the replay manifest. The dedicated guard
checks synchronized authority evidence, implementation markers, isolated
tests, and all-check wiring.

## D6 Validation and Closeout

Validation order is the FCP-0030 isolated suite, affected BTC replay and bridge
suites, FCP governance stage suite, full pytest, `scripts/run_all_checks.py`,
generated-output restoration, exact changed-file verification, and
`git diff --check`.

Validated result:

- FCP-0030 isolated suite: 20 passed
- affected BTC replay and bridge suite: 55 passed
- FCP governance stage suite: 637 passed
- project governance suite: 21 passed
- full pytest: 5974 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: final run left no tracked generated changes
