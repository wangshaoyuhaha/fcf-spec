# P14-D13 To P14-D15 Risk-adjusted Expert Trust Scoring

Status: completed after validation.

Scope:
- P14-D13: add paper maximum drawdown penalty
- P14-D14: generate risk-adjusted expert trust report
- P14-D15: regression tests for risk-adjusted scoring boundary

Reason:
Two experts can both be correct, but one may require a deep paper drawdown before becoming correct.
The risk-adjusted score penalizes unstable paths.

Formula:
risk_adjusted_score = weighted_score / (1 + max_paper_drawdown_pct * penalty_multiplier)

Allowed:
- calculate paper drawdown penalty
- generate paper trust report
- propose governor weight input

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
