# P14-D37 To P14-D39 Explanation Consistency Check

Status: completed after validation.

Scope:
- P14-D37: detect unsafe AI explanation phrases
- P14-D38: compare AI claims against Python report fields
- P14-D39: regression tests for no-override boundary

Purpose:
Ensure AI explanations do not contradict Python output or safety boundaries.

Allowed:
- compare explanation claims with Python report fields
- block inconsistent explanations for operator review
- write local consistency report

Forbidden:
- AI explanation overriding Python report
- auto-approve explanations
- auto-trade
- connect real exchange API
- connect real brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real balances or positions
- affect real money

Python report remains the source of truth.
Operator review remains required.
