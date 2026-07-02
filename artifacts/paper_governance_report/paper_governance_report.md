# Paper Governance Report

Status: paper-only governance report

Created at UTC: 2026-07-02T16:46:16.168534+00:00

## Safety Boundary

- Paper-only: true
- Real exchange API: false
- Real API key required: false
- Wallet private key required: false
- Real order: false
- Real execution: false
- Real balance: false
- Real position: false
- Real money impact: false
- Operator review required: true

## Summary

- Count: 6
- Event count: 12
- Symbols: BTCUSDT, ETHUSDT, SOLUSDT, BTCUSDT, ETHUSDT, SOLUSDT
- Gate counts: {"paper_allowed_with_operator_review": 6}
- Regime counts: {"neutral": 2, "overextended_downside": 2, "overextended_upside": 2}
- Operator gate: operator_review_pending
- Operator allowed action: wait_for_operator_review

## Policy Constraints

- Required review: operator_review_required_for_all_items
- Failed gate count: 0
- Blocked actions: automatic_live_trading, real_api_key, real_balance, real_exchange_api, real_execution, real_money_impact, real_order, real_position, wallet_private_key

## Symbol Governance Items

### BTCUSDT

- Governor gate: paper_allowed_with_operator_review
- Allowed action: paper_analysis_review
- Risk level: medium
- Risk score: 15.62
- Signal: paper_watch_upside_bias
- Regime: neutral
- Policy gate: pass
- Policy approved action: paper_analysis_review
- Decision: governor_paper_only_no_real_trade

Blocked reasons:
- none

Warnings:
- none

### ETHUSDT

- Governor gate: paper_allowed_with_operator_review
- Allowed action: paper_analysis_review
- Risk level: medium
- Risk score: 27.78
- Signal: paper_watch_downside_bias
- Regime: overextended_downside
- Policy gate: pass
- Policy approved action: paper_analysis_review
- Decision: governor_paper_only_no_real_trade

Blocked reasons:
- none

Warnings:
- none

### SOLUSDT

- Governor gate: paper_allowed_with_operator_review
- Allowed action: paper_analysis_review
- Risk level: medium
- Risk score: 34.48
- Signal: paper_watch_upside_bias
- Regime: overextended_upside
- Policy gate: pass
- Policy approved action: paper_analysis_review
- Decision: governor_paper_only_no_real_trade

Blocked reasons:
- none

Warnings:
- none

### BTCUSDT

- Governor gate: paper_allowed_with_operator_review
- Allowed action: paper_analysis_review
- Risk level: medium
- Risk score: 15.62
- Signal: paper_watch_upside_bias
- Regime: neutral
- Policy gate: pass
- Policy approved action: paper_analysis_review
- Decision: governor_paper_only_no_real_trade

Blocked reasons:
- none

Warnings:
- none

### ETHUSDT

- Governor gate: paper_allowed_with_operator_review
- Allowed action: paper_analysis_review
- Risk level: medium
- Risk score: 27.78
- Signal: paper_watch_downside_bias
- Regime: overextended_downside
- Policy gate: pass
- Policy approved action: paper_analysis_review
- Decision: governor_paper_only_no_real_trade

Blocked reasons:
- none

Warnings:
- none

### SOLUSDT

- Governor gate: paper_allowed_with_operator_review
- Allowed action: paper_analysis_review
- Risk level: medium
- Risk score: 34.48
- Signal: paper_watch_upside_bias
- Regime: overextended_upside
- Policy gate: pass
- Policy approved action: paper_analysis_review
- Decision: governor_paper_only_no_real_trade

Blocked reasons:
- none

Warnings:
- none

## Final Notice

This governance report is not financial advice.
This governance report is not a real trading signal.
This governance report must not be used for real execution.
Operator approval still does not permit real-world trading actions.
