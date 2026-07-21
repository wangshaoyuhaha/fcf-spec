# FCF FCP 0049 BTC Perpetual Fee Rebate Schedule Evidence Registry App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Registered Rule Evidence

Require immutable local JSON artifact identity, exact digest and byte length,
rights, observation time, registration time, and Operator registration.

## D2 Exact Fee And Rebate Rates

Preserve exact signed maker and taker rates. Negative registered values remain
explicit rebates. Reject floats, nonfinite values, and rates outside unit range.

## D3 Volume Tiers And Fee Assets

Preserve contiguous trailing-volume tiers, measurement asset, positive integer
window, and ordered eligible fee assets without selecting a real account tier.

## D4 Effective Time And Contract Lineage

Bind every schedule version to one exact FCP-0046 contract entry. Require
unique ordered identities, half-open UTC intervals, and no overlapping versions.

## D5 Fail-Closed Lookup And Authority

Resolve exactly one schedule at a registered UTC instant. Forbid account-tier,
fee, rebate, balance, position, PnL, liquidation, funding, source, or execution
use.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0049 suite: 16 passed
- affected governance suite: 68 passed
- all FCP suites: 890 passed
- full pytest: 6227 passed
- `scripts/run_all_checks.py`: passed
- generated output restoration: no generated delta
- post-merge affected suite: 68 passed

The registry is implemented, merged, validated, and guarded. It grants no
account-tier selection, fee or rebate calculation, balance, position, PnL,
liquidation, funding, source, GAP-closure, acquisition, SDK, network,
credential, realtime, wallet, account, order, execution, product, P48, tag,
release, or deployment authority. No successor phase is selected.

Synthetic fixtures do not close GAP-099 or GAP-102 and grant no acquisition,
SDK, network, credential, realtime, wallet, account, balance, position, order,
execution, product, P48, tag, release, or deployment authority.
