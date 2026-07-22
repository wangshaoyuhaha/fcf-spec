# FCF FCP 0070 BTC Perpetual Paper Stress Deterministic Trigger Evaluation App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact Bound Inputs

Consume one exact typed FCP-0069 input-binding registry and the exact typed
FCP-0068, FCP-0064, and FCP-0056 evidence bound by it.

## D2 Closed Decimal Measures

Execute only the eight registered formula families with exact Decimal
arithmetic and explicit nonpositive-baseline rejection.

## D3 Registered Trigger Boundaries

Apply the exact registered parameter transform and strict or inclusive
comparison operator for each stress kind.

## D4 Fail-Closed Lineage

Reject untyped or substituted registries, schemas, observations, parameters,
venue or contract identities, formula roles, or reversed UTC lineage.

## D5 Immutable Paper Evidence

Emit one deterministic measure-and-trigger result per kind with mandatory
Operator review and no account, margin, leverage, liquidation, balance,
position, PnL, insurance, ADL, order, or execution authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0070 suite: 31 passed
- affected BTC perpetual rule, stress, and governance suite: 498 passed
- all FCP suites: 1304 passed
- full pytest: 6641 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

Post-merge validation evidence:

- affected BTC perpetual rule, stress, and governance suite: 498 passed
- full pytest: 6641 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Evidence commits:

- governance approval: `3de0442dfcb245059e2c837a10acc6d05d9dfb7c`
- sidecar delivery: `af645800e27023c48e98cb34a318ae55066bd457`
- main delivery merge: `7ae811358fd1a941ccc2628a44b8759d47f0a3c3`
