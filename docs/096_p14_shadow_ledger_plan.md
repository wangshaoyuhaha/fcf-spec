# P14-D4 To P14-D6 Learning Engine Shadow Ledger

Status: completed after validation.

Scope:
- P14-D4: define paper-only shadow ledger event
- P14-D5: append counterfactual expert proposals to local JSON ledger
- P14-D6: summarize regimes and expert proposal counts

Purpose:
The shadow ledger records every expert paper proposal, including proposals not selected by the governor or operator.
This supports counterfactual learning without real execution.

Allowed:
- record paper expert proposals
- record selected expert id
- summarize expert proposal counts
- summarize regime counts

Forbidden:
- real exchange API
- real brokerage API
- API keys
- wallet private keys
- real balances
- real positions
- real orders
- real execution
- real money impact

Operator review remains required.
