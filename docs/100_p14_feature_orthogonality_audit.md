# P14-D16 To P14-D18 Feature Orthogonality Audit

Status: completed after validation.

Scope:
- P14-D16: classify high, medium, and low feature overlap
- P14-D17: generate local orthogonality audit report
- P14-D18: regression tests for no-auto-prune boundary

Purpose:
Avoid stacking redundant indicators that all describe the same underlying signal.
The system should seek incremental alpha, not repeated noise.

Example:
RSI, MACD, and KDJ may be highly correlated because they are all derived from price momentum.
If overlap is high, the report may propose reviewing one feature for deprioritization.

Allowed:
- detect redundant paper features
- generate review-only mute/deprioritize proposals
- write local audit report

Forbidden:
- auto-mute features
- auto-prune features
- auto-apply governor weights
- connect real exchange API
- connect real brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real money

Operator review remains required.
