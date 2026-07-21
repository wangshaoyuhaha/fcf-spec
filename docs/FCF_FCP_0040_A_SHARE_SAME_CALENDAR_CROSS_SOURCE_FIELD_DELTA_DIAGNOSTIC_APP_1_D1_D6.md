# FCF FCP 0040 A Share Same Calendar Cross Source Field Delta Diagnostic App 1 D1-D6

Status: VALIDATED_PENDING_MERGE

## D1 Typed Inputs

Require typed FCP-0038 coverage evidence and its FCP-0039 artifact-independence
proof with exact role, dataset, and artifact lineage agreement.

## D2 Overlap Boundary

Recompute exact overlapping instrument and date keys and reject empty or
coverage-disagreeing overlap before producing a diagnostic.

## D3 Exact Numeric Deltas

Summarize observation, nonzero, total absolute, and maximum absolute deltas for
raw OHLC, share volume, yuan amount, and paired adjustment factors.

## D4 Status And Clock Diagnostics

Count factor absence, factor-version mismatch, and trading-status mismatch and
summarize absolute seconds for the closed registered clock set.

## D5 Authority Boundary

Bind all summaries and upstream lineage into immutable hashes, require Operator
review, and forbid thresholds, rankings, source selection, or evidence
replacement. Synthetic evidence does not close GAP-109.

## D6 Validation And Closeout

Run the isolated FCP-0040 suite, affected cross-source and governance suites,
all FCP governance tests, full pytest, `scripts/run_all_checks.py`, generated
output restoration, exact changed-file review, and `git diff --check`.

Validation evidence before merge:

- Isolated FCP-0040 suite: `9 passed`.
- Affected FCP-0021/FCP-0037/FCP-0038/FCP-0039/FCP-0040 and governance suite:
  `118 passed`.
- All FCP governance suites: `769 passed`.
- Full pytest: `6106 passed`.
- `scripts/run_all_checks.py`: `ALL CHECKS PASSED`.
- Generated outputs: restored; no generated-output delta remained.
