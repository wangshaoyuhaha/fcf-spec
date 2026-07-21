# FCF FCP 0048 BTC Perpetual Funding Method Schedule Evidence Registry App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Registered Rule Evidence

Require immutable local JSON artifact identity, exact digest and byte length,
rights, observation time, registration time, and Operator registration.

## D2 Funding Method And Basis

Preserve closed PREMIUM_INDEX_CLAMPED or DIRECT_VENUE_RATE methods and closed
PREMIUM_INDEX, MARK_INDEX_BASIS, or DIRECT_RATE basis semantics.

## D3 Schedule And Direction

Preserve a positive integer interval, exact UTC anchor, signed cap and floor,
exact interest component, and closed positive-rate payer convention.

## D4 Effective Time And Contract Lineage

Bind every funding version to one exact FCP-0046 contract entry. Require unique
ordered identities, half-open UTC intervals, and no overlapping versions.

## D5 Fail-Closed Lookup And Authority

Resolve exactly one version at a registered UTC instant. Forbid funding-rate,
payment, balance, position, PnL, liquidation, fee, source, or execution use.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- Isolated FCP-0048 suite: `16 passed`.
- Affected BTC funding and governance suite: `84 passed`.
- All FCP suites: `874 passed`.
- Full pytest: `6211 passed`.
- `scripts/run_all_checks.py`: `ALL CHECKS PASSED`.
- Generated outputs: no generated-output delta remained.
- Post-merge affected suite: `84 passed`.
- Generated runtime outputs: restored; no tracked generated changes remained.

The registry is implemented, merged, validated, and guarded. It grants no
funding-rate, payment, balance, position, PnL, liquidation, fee, source,
GAP-closure, acquisition, SDK, network, credential, realtime, wallet, account,
order, execution, product, P48, tag, release, or deployment authority. No
successor phase is selected.

Synthetic fixtures do not close GAP-099 or GAP-102 and grant no acquisition,
SDK, network, credential, realtime, wallet, account, balance, position, order,
execution, product, P48, tag, release, or deployment authority.
