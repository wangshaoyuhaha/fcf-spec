# FCF FCP 0052 Guojin QMT Coverage Supplement Lineage Integrity Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Gate Binding

Require one typed FCP-0051 gate and preserve its instrument, requested range,
source lineage, cap state, and evidence hash.

## D2 Typed Calendar And Batch Lineage

Require typed FCP-0037 and FCP-0036 evidence with exact instrument, calendar
date-set, artifact, count, and multi-batch agreement.

## D3 Typed Supplemental Evidence

Register deterministic pagination, point-in-time, and row-cap-resolution
records with closed semantics and no runtime authority.

## D4 Fail-Closed Coherence

Reject cross-instrument, cross-range, cross-calendar, single-batch, mismatched
pagination, and mismatched row-cap lineage.

## D5 Derived FCP-0051 Supplements

Derive every supplement digest and date-set count from typed validated inputs.
Do not accept an arbitrary proof digest at the bundle boundary.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full pytest, `scripts/run_all_checks.py`, exact
path review, generated-output restoration, and `git diff --check` before merge.

The current real QMT evidence remains incomplete. Synthetic validation cannot
change FCP-0051, close GAP-105, GAP-107, or GAP-108, or authorize a provider or
runtime path.

Validated before merge:

- isolated FCP-0052 suite: 12 passed
- affected QMT lineage and governance suite: 147 passed
- all FCP suites: 931 passed
- full pytest: 6268 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained
