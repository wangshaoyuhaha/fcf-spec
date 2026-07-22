# FCF FCP 0064 BTC Perpetual Paper Stress Evaluation Operand Evidence Registry App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Typed Input

Consume one exact typed FCP-0063 operand-schema snapshot.

## D2 Complete Operand Evidence

Register one exact local typed observation for every closed operand role with
the required metric identifier, unit, venue, contract, event time,
availability time, source artifact, content digest, and rights lineage.

## D3 Point-In-Time Pairing

Require baseline evidence to precede current evidence for collateral drawdown,
funding shock, price gap, and thin book. Preserve one threshold observation for
liquidation distance, loss streak, resync, and venue outage.

## D4 Fail-Closed Validation

Reject missing, duplicate, extra, cross-kind, untyped, future, time-reversed,
unit-incompatible, contract-incoherent, or domain-invalid evidence.

## D5 Immutable Registration Evidence

Emit one deterministic registration-only registry with mandatory Operator
review and no direction, evaluation, calculation, account-state, or execution
authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0064 suite: 29 passed
- affected BTC perpetual rule, stress, and governance suite: 358 passed
- all FCP suites: 1164 passed
- full pytest: 6501 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta
