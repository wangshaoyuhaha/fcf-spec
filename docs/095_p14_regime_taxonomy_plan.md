# P14-D1 To P14-D3 Learning Engine Regime Taxonomy Plan

Status: completed after validation.

Scope:
- P14-D1: define paper-only regime taxonomy
- P14-D2: add local regime classification stub
- P14-D3: regression tests for regime-first learning boundary

Reason:
Expert trust scoring must be conditioned by market regime.
Therefore regime taxonomy is defined before trust scoring.

Initial regime buckets:
- trend_up
- trend_down
- range_chop
- high_volatility_breakout
- low_volatility_compression
- liquidity_stress
- unknown

Safety boundary:
- paper-only
- local-only
- read-only
- no trading buttons
- no real exchange API
- no real brokerage API
- no API keys
- no wallet private keys
- no real orders
- no real execution
- no real balances or positions
- no real money impact
- operator review required
