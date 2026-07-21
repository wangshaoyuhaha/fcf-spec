# FCF FCP 0023 BTC Cross-Source Venue Quality Reconciliation App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Registered Comparison Contract

Each dataset binds one exact registered BTC artifact, one source identity,
typed observations, immutable rights and retention state, and an as-of clock.

## D2 Canonical Comparison Identity

Instrument, instrument kind, observation kind, and event time form the closed
comparison key. Keys must be unique and deterministically ordered.

## D3 Deterministic Coverage and Pairwise Comparison

The reconciler computes union and overlap coverage and compares every source
pair without choosing a baseline authority or silently filling missing rows.

## D4 BTC-Specific Conflict Evidence

Venue, receive and ingest clocks, source sequence, trades, book snapshots and
deltas, reference prices, funding rates, and funding intervals are reconciled.

## D5 Quarantine Boundary

Any blocking finding produces `QUARANTINE_REVIEW_REQUIRED`. The result remains
immutable, selects no source, and requires Operator review.

## D6 Validation and Closeout

Validation order is the isolated FCP-0023 suite, FCP governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check` before merge and closeout.

Validated result:

- FCP-0023 isolated suite: 18 passed
- FCP governance targeted suite: 537 passed
- full pytest: 5853 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: four tracked check outputs restored exactly
