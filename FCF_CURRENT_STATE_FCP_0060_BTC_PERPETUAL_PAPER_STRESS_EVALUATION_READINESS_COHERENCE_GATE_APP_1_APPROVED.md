# FCF Current State FCP 0060 BTC Perpetual Paper Stress Evaluation Readiness Coherence Gate App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0060-btc-perpetual-paper-stress-evaluation-readiness-coherence-gate-app-1`

Approved order:

- D1 bind exact typed FCP-0055, FCP-0057, and FCP-0059 snapshots
- D2 require exact snapshot, venue, contract, and scenario lineage
- D3 require monotonic effective and as-of UTC coherence
- D4 fail closed on stale, cross-lineage, incomplete, or untyped evidence
- D5 preserve immutable readiness-only evidence and Operator review
- D6 run guards, validation, merge, and final authority synchronization

The gate cannot evaluate stress or calculate prices, margin, leverage,
liquidation, balances, positions, PnL, insurance fund, ADL, orders, execution,
or source preference. It cannot close GAP-098, GAP-099, GAP-100, or GAP-101.
