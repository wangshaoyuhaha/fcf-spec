# FCF FCP 0046 BTC Perpetual Venue Contract Lifecycle Registry App 1 D1-D6

Status: VALIDATED_PENDING_MERGE

## D1 Registered Rule Evidence

Require immutable local JSON artifact identity, exact digest and byte length,
rights, observation time, registration time, and Operator registration.

## D2 Contract Semantics

Preserve venue, contract, symbol, linear or inverse settlement, base, quote,
settlement and collateral assets, multiplier, tick, step, and minimums.

## D3 Lifecycle Versions

Preserve effective half-open intervals and closed ACTIVE, CLOSE_ONLY, DELISTED,
or MIGRATED states. A migrated version requires a distinct target contract.

## D4 Registry Integrity

Require unique ordered entry and version identities, exact artifact lineage,
nonoverlapping versions, point-in-time bounds, and immutable hashes.

## D5 Fail-Closed Lookup And Authority

Resolve exactly one version at a registered UTC instant. Reject gaps and
ambiguity. Forbid margin, liquidation, PnL, funding, source, or execution use.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- Isolated FCP-0046 suite: `14 passed`.
- Affected BTC contract and governance suite: `100 passed`.
- All FCP suites: `841 passed`.
- Full pytest: `6178 passed`.
- `scripts/run_all_checks.py`: `ALL CHECKS PASSED`.
- Generated outputs: no generated-output delta remained.

Synthetic fixtures do not close GAP-096 or GAP-102 and grant no acquisition,
SDK, network, credential, realtime, wallet, account, balance, position, order,
execution, product, P48, tag, release, or deployment authority.
