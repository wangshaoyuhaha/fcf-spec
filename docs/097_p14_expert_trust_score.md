# P14-D7 To P14-D9 Expert Trust Scoring

Status: completed after validation.

Scope:
- P14-D7: define paper-only expert outcome score
- P14-D8: define half-life weighted trust report
- P14-D9: regression tests for trust scoring boundary

Formula:
weighted_score = outcome_score * 0.5 ** (age_days / half_life_days)

Purpose:
Expert trust scores are calculated per expert and per regime.
They produce governor weight proposals only.

Allowed:
- score paper outcomes
- aggregate scores by expert and regime
- generate governor weight proposal data

Forbidden:
- auto-apply governor weights
- connect real exchange API
- connect real brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real balances or positions
- affect real money

Operator review remains required.
