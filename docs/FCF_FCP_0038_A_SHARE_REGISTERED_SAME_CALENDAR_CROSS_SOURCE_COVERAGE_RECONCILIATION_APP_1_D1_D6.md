# FCF FCP 0038 A Share Registered Same Calendar Cross Source Coverage Reconciliation App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Explicit Source Roles

Require exactly one QMT local-export role and one independent-reference role
with distinct registered dataset and source identities.

## D2 Shared Calendar Authority

Require both canonical datasets and the FCP-0037 registered expected-date
profile to identify exactly one identical A-share instrument. An unresolved
calendar rights state is visible and forces quarantine review.

## D3 Per-Source Coverage

Compute missing and unexpected dates separately for QMT and the independent
reference against the same immutable expected-date set.

## D4 Cross-Source Quality

Reuse FCP-0021 for deterministic price, amount, volume, adjustment, status,
clock, rights, retention, and dataset-lineage reconciliation.

## D5 Review Boundary

Quarantine any coverage or FCP-0021 mismatch, preserve every lineage hash,
forbid source selection, and require Operator review. Synthetic tests do not
close GAP-109. The result contract rejects invalid A-share identifiers, invalid
ISO dates, equal role hashes, and finding sets that disagree with evidence.

## D6 Validation And Closeout

Run the isolated FCP-0038 suite, affected FCP-0021/FCP-0037 and governance
suite, all FCP governance tests, full pytest, `scripts/run_all_checks.py`,
generated-output restoration, exact changed-file review, and `git diff --check`.

Validation evidence before merge:

- Isolated FCP-0038 suite: `13 passed`.
- Affected FCP-0021/FCP-0037/FCP-0038 and governance suite: `95 passed`.
- All FCP governance suites: `746 passed`.
- Full pytest: `6083 passed`.
- `scripts/run_all_checks.py`: `ALL CHECKS PASSED`.
- Post-merge affected suite: `95 passed`.
- Generated outputs: restored; no generated-output delta remained.
