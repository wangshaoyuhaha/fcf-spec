# FCF FCP 0104 Registered Volume Flow Indicator Runtime App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Phase: FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1

## D1 Exact Registered Input

Require exact Operator-registered ASCII JSON bytes, byte length, SHA-256,
closed schemas, explicit SHARES and CNY units, and exact FCP-0096 registry
identity.

## D2 Deterministic OBV

Calculate rolling On-Balance Volume from close direction and current volume
using Decimal arithmetic over eligible bars.

## D3 Deterministic MFI

Calculate rolling Money Flow Index from typical price and volume with
explicit neutral and zero-denominator states.

## D4 Deterministic Volume Price Trend

Calculate rolling Volume Price Trend from current volume and point-in-time
close returns without future data.

## D5 Catalog V2 Coverage

Compose the FCP-0103 catalog v1 foundations with FCP-0104 kinds. Register 17
supported kinds and expose 36 accepted candidates as missing.

## D6 Authority Boundary

Deterministic Engine remains calculation authority and Operator review
remains mandatory. Scoring, ranking, recommendation, external data, account,
order, execution, P48, tag, release, and deployment remain forbidden.

## Validation Closeout

Delivery commit: `1cf559155ea544cb8844dea49f7eeaa00fad2402`.

Merge commit: `6c84cadbb34a0f0382ea589bdfe908354cc8299c`.

Validation completed with 10 isolated tests, 57 affected-chain tests, 1918
all-FCP tests, 7255 full-pytest tests, and `run_all_checks.py` passing.
