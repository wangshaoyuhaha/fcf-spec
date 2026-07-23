# FCF FCP 0101 Registered Technical Indicator Core Runtime App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Phase: FCF-FCP-0101-REGISTERED-TECHNICAL-INDICATOR-CORE-RUNTIME-APP-1

## D1 Exact Registered Market Artifact

Accept exact Operator-registered bytes only. Byte length, SHA-256, rights,
registration time, ASCII decoding, closed schemas, units, and Decimal strings
fail closed.

## D2 Point-In-Time Bar Contract

Require positive finite OHLC, valid high-low ordering, nonnegative volume and
amount, unique strictly increasing UTC timestamps, and no bar after the
registered as-of time.

## D3 Core Deterministic Indicators

Calculate registered SMA, EMA, Bollinger, RSI, ATR, and VWAP requests with
Decimal arithmetic and fixed eight-decimal half-even output normalization.

## D4 Suspension And Missing-State Boundary

Require explicit suspension identity to match zero volume and amount. The
initial registered policy is `EXCLUDE`; insufficient eligible history fails
closed.

## D5 Immutable Calculation Evidence

Bind factor identity, factor version, indicator kind, window, suspension
policy, source timestamp, values, and deterministic result hashes into one
immutable snapshot.

## D6 Operator And Authority Boundary

Deterministic Engine remains calculation authority and Operator review remains
mandatory. The runtime creates no scoring, ranking, recommendation, account,
order, execution, P48, tag, release, or deployment authority.
