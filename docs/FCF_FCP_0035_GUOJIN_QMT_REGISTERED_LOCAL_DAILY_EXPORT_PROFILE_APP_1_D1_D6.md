# FCF FCP 0035 Guojin QMT Registered Local Daily Export Profile App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Registered Source Contract

Accept exact Operator-registered ASCII bytes with the closed QMT seven-column
daily export header and immutable source digest. Real exports remain outside
the repository.

## D2 Identity, Date, And Unit Normalization

Require an explicit canonical A-share instrument identity, normalize
`YYYYMMDD` to ISO dates, and convert integral `volumn` lots to shares with an
exact factor of 100. Reject filename inference and fractional lots.

## D3 Deterministic Bridge Bytes

Emit exact ASCII code, exchange, date, raw OHLC, share volume, and yuan amount
bytes compatible with the FCP-0019 bridge. Preserve normalized registration,
profile, source, output, and manifest hashes.

## D4 Adjustment And Coverage Evidence

Compare paired raw and front exports only as additive price-offset reference
evidence. Preserve requested and actual coverage and expose mismatches without
inferring pagination, completeness, or a multiplicative factor.

## D5 Fail-Closed Authority Compatibility

Missing adjustment-factor lineage, trading status, and point-in-time
supplements remain blocking findings. The existing FCP-0017 and FCP-0019
contracts remain calculation and canonicalization authorities.

## D6 Validation And Closeout

Run the isolated FCP-0035 suite, FCP governance targeted suite, full pytest,
`scripts/run_all_checks.py`, generated-output restoration, exact changed-file
verification, and `git diff --check`. Merge and final authority synchronization
occur only after every validation passes.

Validated before merge:

- FCP-0035 isolated suite: 18 passed
- affected A-share bridge and governance suite: 81 passed
- FCP governance stage suite: 697 passed
- full pytest: 6034 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained
