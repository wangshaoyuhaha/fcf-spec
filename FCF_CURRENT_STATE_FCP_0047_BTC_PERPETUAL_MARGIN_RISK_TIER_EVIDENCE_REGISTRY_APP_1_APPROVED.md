# FCF Current State FCP 0047 BTC Perpetual Margin Risk Tier Evidence Registry App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0047-btc-perpetual-margin-risk-tier-evidence-registry-app-1`

Approved scope:

- register immutable local BTC perpetual margin and risk-tier rule evidence
- preserve isolated or cross margin and one-way or hedge position-mode semantics
- preserve exact initial and maintenance margin rates, risk limits, and deductions
- preserve collateral eligibility, haircut, valuation asset, and effective-time rules
- bind every rule version to one exact FCP-0046 contract-registry identity
- provide deterministic point-in-time lookup with gap and overlap rejection

The registry cannot calculate balances, positions, PnL, liquidation, funding,
fees, execution, or source preference. Synthetic fixtures do not close GAP-097
or GAP-102. No acquisition, SDK, network, credential, source selection, raw
repository retention, realtime, product phase, P48, wallet, account, balance,
position, order, execution, tag, release, or deployment is authorized.
