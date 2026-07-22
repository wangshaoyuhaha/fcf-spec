# FCF FCP 0050 Guojin QMT Registered Dual Export Quality Evidence App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Immutable Dual Artifact Registration

Require exact raw and front-adjusted artifact IDs, SHA-256 digests, byte
lengths, rights, retention, registration time, and Operator registration.
Actual provider bytes and local paths remain outside the repository.

## D2 Exact Schema And Row Quality

Require the exact ASCII header
`timetag,open,high,low,close,volumn,amount`, ordered unique valid dates, exact
decimal OHLC values, integral lots, nonnegative amount, and OHLC invariants.

## D3 Lot And Raw Front Parity Evidence

Validate raw notional-derived price against the daily raw range using exactly
100 shares per lot. Require exact raw/front date, volume, and amount parity.
These checks record consistency evidence and do not select a provider.

## D4 Adjustment Reference Ledger

Preserve one immutable raw-minus-front close-price offset for every registered
row, exact offset distribution, row-ledger hash, and observed boundary dates.
The ledger is additive reference evidence and never adjustment-factor authority.

## D5 Row Cap And Completeness Boundary

Bind the exact 500-row result to an explicit Operator-registered local-export
row-cap observation. The state is `AT_REGISTERED_CAP`; pagination authority and
historical-completeness authority remain false.

## D6 Registered Evidence And Closeout

The repository evidence records the two exact artifact hashes, 500 rows from
2024-06-28 through 2026-07-21, six offset-count regimes, five observed boundary
dates, immutable lineage hashes, and all blocking findings. It stores no raw
provider values, raw files, or local paths.

Read-only actual-file smoke result:

- raw SHA-256: `4c61b151c7dda4d321d1bbf6143d9cde2dec7db593f90d14a47fa79ac15e8da6`
- front SHA-256: `ca509e505f9df82812ee822de72726149a9df878b0ca6e47504a5818d4686c6c`
- row count: 500
- actual coverage: 2024-06-28 through 2026-07-21
- raw/front date, volume, and amount parity: exact
- 100-share-lot notional-range consistency: passed
- upstream quality state: `BLOCKED_PENDING_SUPPLEMENTS`

Validation evidence before merge:

- isolated FCP-0050 suite: 12 passed
- affected QMT and governance suite: 176 passed
- all FCP suites: 902 passed
- full pytest: 6239 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Merge and closeout evidence:

- governance approval: `222017630435802ec32dbf02d2dd7a5ea2ed5a31`
- sidecar delivery: `6de945a8530e8cc560d0e6feff4a64ab4ba7c85d`
- main delivery merge: `d60c1487f5c59af0977ed15131331ece58e323af`
- post-merge affected suite: 176 passed
- post-merge full pytest: 6239 passed
- post-merge `scripts/run_all_checks.py`: ALL CHECKS PASSED

GAP-104 through GAP-109 remain `RESEARCH_REQUIRED`. No acquisition, SDK,
network, credential, provider selection, raw repository retention, realtime,
broker, account, balance, position, order, execution, product, P48, tag,
release, or deployment authority is created.
