# FCF FCP 0063 BTC Perpetual Paper Stress Evaluation Operand Schema Registry App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact Typed Input

Consume one exact typed FCP-0062 extended-readiness snapshot.

## D2 Closed Operand Schema

Register exact operand roles, metric identifiers, and units for every closed
BTC perpetual Paper stress scenario kind.

## D3 Operand Sufficiency

Require paired baseline-current operands for collateral drawdown, funding
shock, price gap, and thin book. Require one observed operand plus the already
registered scenario threshold for liquidation distance, loss streak, resync,
and venue outage.

## D4 Fail-Closed Validation

Reject missing, duplicate, extra, cross-kind, untyped, unknown-mode,
unit-incompatible, or hash-substituted operand schemas.

## D5 Immutable Schema Evidence

Emit one deterministic schema-only snapshot with mandatory Operator review and
no direction, evaluation, calculation, account-state, or execution authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0063 suite: 18 passed
- affected BTC perpetual rule, stress, and governance suite: 329 passed
- all FCP suites: 1135 passed
- full pytest: 6472 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

Post-merge validation evidence:

- affected BTC perpetual rule, stress, and governance suite: 329 passed
- full pytest: 6472 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Evidence commits:

- governance approval: `3e1d8207dee18c05895ad978a8e87d798c0f1b20`
- sidecar delivery: `047973f29f063ce97974662f6da02c81b1eafae3`
- main delivery merge: `9267ced604b24e795704778da3c00b51bf222932`
