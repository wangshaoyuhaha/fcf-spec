# FCF FCP 0061 BTC Perpetual Paper Stress Scenario Parameter Domain Semantics Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Typed Inputs

Consume exact typed FCP-0056 scenario-registry and FCP-0057 coverage evidence.

## D2 Exact Lineage

Require exact registry, coverage, complete-rule, venue, contract, scenario,
definition, and parameter-schema lineage.

## D3 Closed Parameter Domains

Require positive bounded collateral-drawdown and price-gap ratios, bounded
liquidation-distance and thin-book ratios, positive integral loss counts and
resync or outage seconds, and signed finite funding shocks.

## D4 Fail-Closed Validation

Reject untyped, substituted, cross-contract, schema-mismatched, non-integral,
negative, zero-forbidden, out-of-range, or authority-escalating evidence.

## D5 Immutable Validation Snapshot

Preserve one deterministic domain-validation hash with mandatory Operator
review and no direction, evaluation, calculation, account-state, or execution
authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0061 suite: 32 passed
- affected BTC stress-parameter and governance suite: 584 passed
- all FCP suites: 1104 passed
- full pytest: 6441 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

The hardening does not close GAP-098, GAP-099, GAP-100, or GAP-101 and grants
no acquisition, SDK, network, credential, realtime, exchange, wallet, account,
balance, position, order, execution, product, P48, tag, release, or deployment
authority.
