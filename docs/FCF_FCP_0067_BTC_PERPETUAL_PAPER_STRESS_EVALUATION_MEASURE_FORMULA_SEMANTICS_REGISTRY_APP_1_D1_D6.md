# FCF FCP 0067 BTC Perpetual Paper Stress Evaluation Measure Formula Semantics Registry App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact Typed Direction Registry

Consume one exact typed FCP-0066 direction-semantics registry.

## D2 Closed Formula Families

Register one exact symbolic measure formula family for every ordered scenario
kind without evaluating any observation.

## D3 Operand And Parameter Binding

Bind exact operand roles, scenario parameter and unit, output unit, parameter
transform, and denominator policy to the closed FCP-0066 direction semantics.

## D4 Fail-Closed Validation

Reject untyped lineage, missing, duplicate, reordered, extra, substituted, or
role-incompatible formulas, unsafe denominator policy, and reversed UTC lineage.

## D5 Immutable Formula Evidence

Emit deterministic formula-semantics-only evidence with mandatory Operator
review and no evaluation, calculation, account-state, or execution authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0067 suite: 24 passed
- affected BTC perpetual rule, stress, and governance suite: 419 passed
- all FCP suites: 1225 passed
- full pytest: 6562 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

Post-merge validation evidence:

- affected BTC perpetual rule, stress, and governance suite: 419 passed
- full pytest: 6562 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Evidence commits:

- governance approval: `94031b87437b5bb51c2698c2180b5c43d44710ff`
- sidecar delivery: `8761f0a4bcc019915f5d32c57d49ea1b06eb7a37`
- main delivery merge: `12931b414a36c9956b76237721d93656fa915879`
