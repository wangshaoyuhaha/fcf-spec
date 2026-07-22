# FCF FCP 0066 BTC Perpetual Paper Stress Evaluation Direction Semantics Registry App 1 D1-D6

Status: VALIDATED_PENDING_MERGE

## D1 Exact Typed Context

Consume one exact typed FCP-0065 evaluation-context snapshot.

## D2 Closed Direction Semantics

Register one exact direction and comparison family for every ordered scenario
kind without evaluating any observation.

## D3 Operand And Equality Semantics

Bind baseline-current or observed operand-role order to the FCP-0063 closed
schema and make triggering or non-triggering equality behavior explicit.

## D4 Fail-Closed Validation

Reject untyped context, missing, duplicate, reordered, extra, substituted, or
role-incompatible semantics and reversed UTC lineage.

## D5 Immutable Semantics Evidence

Emit deterministic semantics-only evidence with mandatory Operator review and
no formula, evaluation, calculation, account-state, or execution authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0066 suite: 19 passed
- affected BTC perpetual rule, stress, and governance suite: 395 passed
- all FCP suites: 1201 passed
- full pytest: 6538 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta
