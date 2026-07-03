# P14-D25 To P14-D27 Governor Weight Proposal

Status: completed after validation.

Scope:
- P14-D25: normalize expert trust scores into paper governor weight proposal
- P14-D26: apply meta anomaly guard
- P14-D27: regression tests for no-auto-apply boundary

Purpose:
Turn regime-conditioned trust scores into a review-only governor weight proposal.

Allowed:
- generate paper weight proposal
- cap or zero weights under meta anomaly guard
- write local proposal report

Forbidden:
- auto-apply governor weights
- auto-switch mode
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
