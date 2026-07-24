# FCP-0105 Registered Price Shape Indicator Runtime App 1 D1-D6

## D1 Registered Input Contract

Accept exact Operator-registered ASCII JSON containing unique ordered local
close bars, CNY price identity, strict PIT bounds, and EXCLUDE suspension
policy.

## D2 Bollinger Shape Pack

Calculate deterministic Bollinger Band Width, Bollinger Breakout, and
Bollinger Z Score over the prior registered window. Zero reference dispersion
fails closed for Z Score.

## D3 Momentum and Moving Average Pack

Calculate deterministic Momentum, Moving Average Slope, and Price Distance
From Moving Average with Decimal arithmetic and no future data.

## D4 Breakout Pack

Calculate deterministic Prior High Breakout and signed Range Breakout against
the prior registered window.

## D5 Catalog V3 Coverage

Compose FCP-0104 catalog v2 coverage with eight FCP-0105 kinds. Register 25
supported kinds and expose 28 accepted candidates as missing.

## D6 Authority Boundary

Deterministic Engine remains calculation authority and Operator review
remains mandatory. Scoring, ranking, recommendation, external data, account,
order, execution, P48, tag, release, and deployment remain forbidden.

## Validation Closeout

Delivery commit: `4c4ee3ffa22355260970038668a9730b85e0ab9c`.

Merge commit: `9d127667683828041078a363162c1cd1130a2d4a`.

Validation completed with 11 isolated tests, 68 affected-chain tests, 1929
all-FCP tests, 7266 full-pytest tests, and `run_all_checks.py` passing.
