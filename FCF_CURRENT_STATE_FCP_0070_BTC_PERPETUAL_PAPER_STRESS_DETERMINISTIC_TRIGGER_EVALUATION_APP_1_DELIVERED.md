# FCF Current State FCP 0070 BTC Perpetual Paper Stress Deterministic Trigger Evaluation App 1 Delivered

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Implemented scope:

- exact typed FCP-0069 input-binding and upstream registry lineage
- exact Decimal execution of eight closed measure formulas
- registered parameter transforms and strict or inclusive trigger boundaries
- immutable reviewed local Paper measure-and-trigger evidence

The evaluator cannot calculate or mutate account, margin, leverage,
liquidation price, balance, position, PnL, insurance fund, ADL, order, or
execution state. GAP-098 through GAP-101 remain open.

Validation evidence:

- isolated FCP-0070 suite: 31 passed
- affected BTC perpetual rule, stress, and governance suite: 498 passed
- all FCP suites: 1304 passed
- full pytest: 6641 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked delta
