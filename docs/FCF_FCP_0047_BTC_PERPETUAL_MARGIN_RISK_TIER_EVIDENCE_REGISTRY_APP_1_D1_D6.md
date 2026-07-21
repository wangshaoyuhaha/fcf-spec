# FCF FCP 0047 BTC Perpetual Margin Risk Tier Evidence Registry App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Registered Rule Evidence

Require immutable local JSON artifact identity, exact digest and byte length,
rights, observation time, registration time, and Operator registration.

## D2 Margin And Position Modes

Preserve closed ISOLATED or CROSS margin and ONE_WAY or HEDGE position-mode
semantics without creating a balance, account, position, or order state.

## D3 Risk Tiers And Collateral

Preserve exact contiguous notional tiers, initial and maintenance rates,
maintenance deductions, risk limits, collateral assets, valuation assets, and
haircuts. Reject floats and malformed ranges.

## D4 Effective Time And Contract Lineage

Bind every margin version to one exact FCP-0046 contract entry. Require unique
ordered identities, half-open UTC intervals, and no overlapping versions.

## D5 Fail-Closed Lookup And Authority

Resolve exactly one version, tier, or collateral rule from registered evidence.
Forbid balance, position, margin, PnL, liquidation, funding, fee, source, or
execution calculations and decisions.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- Isolated FCP-0047 suite: `17 passed`.
- Affected BTC margin and governance suite: `69 passed`.
- All FCP suites: `858 passed`.
- Full pytest: `6195 passed`.
- `scripts/run_all_checks.py`: `ALL CHECKS PASSED`.
- Generated outputs: no generated-output delta remained.
- Post-merge affected suite: `69 passed`.
- Generated runtime outputs: restored; no tracked generated changes remained.

The registry is implemented, merged, validated, and guarded. It grants no
balance, position, margin, PnL, liquidation, funding, fee, source-selection,
GAP-closure, acquisition, SDK, network, credential, realtime, wallet, account,
order, execution, product, P48, tag, release, or deployment authority. No
successor phase is selected.

Synthetic fixtures do not close GAP-097 or GAP-102 and grant no acquisition,
SDK, network, credential, realtime, wallet, account, balance, position, order,
execution, product, P48, tag, release, or deployment authority.
