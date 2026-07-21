# FCF FCP 0036 Guojin QMT Registered Local Daily Batch Coverage Reconciliation App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Expected-Date Authority

Accept only exact ASCII `trade_date` artifacts with immutable registration,
explicit instrument identity, ordered unique ISO dates, and no natural-day
inference.

## D2 Ordered Batch Lineage

Require nonempty, unique, contiguous registered batch order and preserve batch,
source artifact, profile, normalization manifest, and rights lineage.

## D3 Deterministic Merge

Normalize every batch through FCP-0035, sort by trade date, deduplicate only
byte-identical overlaps, and emit exact FCP-0019-compatible ASCII bytes.

## D4 Conflict And Coverage Findings

Remove conflicting dates from merged output, quarantine the conflict, compare
only with the registered expected set, and expose missing, unexpected, and
declared-row-cap observations.

## D5 Authority Boundary

Coverage reconciliation cannot provide adjustment factors, trading status,
point-in-time clocks, provider selection, realtime access, or trading authority.
Operator review remains mandatory.

## D6 Validation And Closeout

Run the isolated FCP-0036 suite, affected FCP-0019/FCP-0035 suite, governance
stage suite, full pytest, `scripts/run_all_checks.py`, generated-output
restoration, exact changed-file review, and `git diff --check`. Merge and final
authority synchronization occur only after all validation passes.

Validated before merge:

- FCP-0036 isolated suite: 15 passed
- affected QMT bridge and governance suite: 83 passed
- FCP governance stage suite: 712 passed
- full pytest: 6049 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained
