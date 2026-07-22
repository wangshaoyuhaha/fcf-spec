# FCF Current State FCP 0061 BTC Perpetual Paper Stress Scenario Parameter Domain Semantics Hardening App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0061-btc-perpetual-paper-stress-scenario-parameter-domain-semantics-hardening-app-1`

Approved order:

- D1 bind exact typed FCP-0056 registry and FCP-0057 coverage
- D2 register closed kind-specific parameter domains
- D3 preserve signed funding shocks and valid bounded ratios
- D4 reject invalid ratio, count, seconds, lineage, or untyped evidence
- D5 preserve immutable validation-only evidence and Operator review
- D6 run guards, validation, merge, and final authority synchronization

The hardening cannot define price direction, evaluate stress, or calculate
prices, margin, leverage, liquidation, balances, positions, PnL, ADL, orders,
or execution. GAP-098 through GAP-101 remain open.
