# FCF Current State FCP 0059 BTC Perpetual Paper Stress Evaluation Input Domain Semantics Hardening App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0059-btc-perpetual-paper-stress-evaluation-input-domain-semantics-hardening-app-1`

Approved scope:

- bind one exact typed FCP-0058 stress-evaluation input registry
- permit finite signed funding-reference rates
- require positive price, depth, and collateral-index references
- require bounded liquidation-distance ratios
- require nonnegative integral count and seconds inputs
- preserve immutable domain-validation evidence and Operator review

The hardening cannot evaluate stress or calculate prices, margin, leverage,
liquidation, balances, positions, PnL, ADL, orders, execution, or source
preference. It cannot close GAP-098, GAP-099, GAP-100, or GAP-101. No
acquisition, SDK, network, credential, provider selection, raw repository
retention, realtime, product, P48, exchange, wallet, account, balance,
position, order, execution, tag, release, or deployment is authorized.
