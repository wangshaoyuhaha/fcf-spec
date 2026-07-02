# Operator Console Paper Report

Status: paper-only operator console report

Created at UTC: 2026-07-02T16:46:16.714474+00:00

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

## Dashboard Summary

- Count: 3
- Symbols: BTCUSDT, AAPL, SPY
- Asset class counts: {"crypto": 1, "etf": 1, "stock": 1}
- Market counts: {"paper_binance": 1, "paper_us_equity": 1, "paper_us_etf": 1}
- Status counts: {"paper_review_allowed": 3}
- Action counts: {"approved": 1, "pending": 1, "rejected": 1}
- All reviewed: False
- Allowed global next step: continue_operator_review

## Review Actions

### BTCUSDT

- Queue ID: review-001
- Asset class: crypto
- Market: paper_binance
- Operator action: approved
- Workflow gate: paper_review_approved
- Allowed next step: archive_paper_review_result
- Real-world actions allowed: false

### AAPL

- Queue ID: review-002
- Asset class: stock
- Market: paper_us_equity
- Operator action: pending
- Workflow gate: paper_review_pending
- Allowed next step: wait_for_operator_review
- Real-world actions allowed: false

### SPY

- Queue ID: review-003
- Asset class: etf
- Market: paper_us_etf
- Operator action: rejected
- Workflow gate: paper_review_rejected
- Allowed next step: archive_rejection_and_wait
- Real-world actions allowed: false

## Final Notice

This console report is not financial advice.
This console report is not a real trading signal.
Approved only means paper review approved.
No real-world trading action is enabled.
