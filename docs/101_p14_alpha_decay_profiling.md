# P14-D19 To P14-D21 Alpha Decay Profiling

Status: completed after validation.

Scope:
- P14-D19: classify alpha windows
- P14-D20: estimate best paper contribution window for each feature or source
- P14-D21: regression tests for no-auto-weight-update boundary

Purpose:
Different information sources have different useful lifetimes.
Sentiment may be useful for hours.
Macro notes may be useful for days.
Market structure features may have different windows by regime.

Allowed:
- estimate paper alpha window
- classify source as ultra_short_term, short_term, medium_term, or long_term
- generate local report

Forbidden:
- auto-update weights
- auto-silence sources
- auto-prune features
- connect real exchange API
- connect real brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real balances or positions
- affect real money

Operator review remains required.
