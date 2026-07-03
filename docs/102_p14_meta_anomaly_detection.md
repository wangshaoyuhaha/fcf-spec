# P14-D22 To P14-D24 Meta Anomaly Detection

Status: completed after validation.

Scope:
- P14-D22: detect confidence inversion
- P14-D23: detect paper drawdown anomaly
- P14-D24: generate local meta anomaly report

Purpose:
Detect cases where the system is highly confident but paper outcomes are poor.
This helps identify overconfidence, calibration failure, and dangerous drawdown patterns.

Allowed:
- detect paper-only anomalies
- propose force_shadow_review
- generate local report

Forbidden:
- auto-switch live mode
- auto-trade
- connect real exchange API
- connect real brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real balances or positions
- affect real money

Operator review remains required.
