# FCF FCP 0054 BTC Perpetual Mark Index Liquidation Mechanics Evidence Registry App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Registered Rule Evidence

Require immutable local JSON artifact identity, exact digest and byte length,
rights, observation time, registration time, and Operator registration.

## D2 Price Method Evidence

Preserve closed mark and index methods, exact index-component-set lineage, and
registered bankruptcy and liquidation method identities without calculation.

## D3 Partial Liquidation Tiers

Preserve exact contiguous notional tiers, position-reduction rates,
liquidation-fee rates, and the closed full or partial-ladder mode.

## D4 Insurance Fund ADL And Cascade Policies

Preserve immutable liquidation-fee asset, insurance-fund policy, ADL-ranking
method, and cascade-state policy identities.

## D5 Effective Time And Authority

Bind every version to one exact FCP-0046 contract entry. Require half-open UTC
intervals and fail-closed lookup. Forbid price, margin, liquidation, account,
fund, ADL, source, or execution authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0054 suite: 20 passed
- affected BTC liquidation-registry and governance suite: 532 passed
- all FCP suites: 960 passed
- full pytest: 6297 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

Post-merge validation evidence:

- affected BTC liquidation-registry and governance suite: 532 passed
- full pytest: 6297 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Evidence commits:

- governance approval: `fce1b40ecebb5b50670a6e8315b95088b7befcd7`
- sidecar delivery: `746b81708457f79bf7973bd4f95ccf04c690adf2`
- main delivery merge: `ee94dc1973eb2dbd6c8db3cb8fa94b41e7c922d9`

Synthetic fixtures do not close GAP-098, GAP-100, GAP-101, or GAP-102 and
grant no acquisition, SDK, network, credential, realtime, exchange, wallet,
account, balance, position, order, execution, product, P48, tag, release, or
deployment authority.
