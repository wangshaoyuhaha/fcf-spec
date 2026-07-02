# Multi-Market Paper Report

Status: paper-only multi-market report

Created at UTC: 2026-07-02T16:46:16.459811+00:00

## Safety Boundary

- Paper-only: true
- Real exchange API: false
- Real brokerage API: false
- Real API key required: false
- Wallet private key required: false
- Real order: false
- Real execution: false
- Real balance: false
- Real position: false
- Real money impact: false
- Operator review required: true

## Summary

- Count: 3
- Symbols: BTCUSDT, AAPL, SPY
- Asset class counts: {"crypto": 1, "etf": 1, "stock": 1}
- Market counts: {"paper_binance": 1, "paper_us_equity": 1, "paper_us_etf": 1}
- Gate counts: {"paper_allowed_with_operator_review": 3}
- Regime counts: {"neutral": 3}

## Cards

### BTCUSDT

- Asset class: crypto
- Market: paper_binance
- Status: paper_review_allowed
- Risk level: medium
- Risk score: 15.62
- Regime: neutral
- Signal: paper_watch_upside_bias
- Governor gate: paper_allowed_with_operator_review
- Policy gate: pass
- Allowed action: paper_analysis_review

### AAPL

- Asset class: stock
- Market: paper_us_equity
- Status: paper_review_allowed
- Risk level: low
- Risk score: 10.64
- Regime: neutral
- Signal: paper_watch_upside_bias
- Governor gate: paper_allowed_with_operator_review
- Policy gate: pass
- Allowed action: paper_analysis_review

### SPY

- Asset class: etf
- Market: paper_us_etf
- Status: paper_review_allowed
- Risk level: low
- Risk score: 3.86
- Regime: neutral
- Signal: paper_neutral_watch
- Governor gate: paper_allowed_with_operator_review
- Policy gate: pass
- Allowed action: paper_analysis_review

## Final Notice

This report is not financial advice.
This report is not a real trading signal.
This report must not be used for real execution.
Stocks, ETFs, and crypto entries are paper-only contract inputs.
