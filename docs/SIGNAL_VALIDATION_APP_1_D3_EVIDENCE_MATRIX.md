# SIGNAL-VALIDATION-APP-1 D3 Evidence Matrix Schema

## Stage

SIGNAL-VALIDATION-D3

## Purpose

D3 defines the paper-only evidence matrix schema for SIGNAL-VALIDATION-APP-1.

The evidence matrix records whether a candidate or review target has coherent
support across existing local sidecar layers.

## Evidence layers

- DATA-APP-1
- STOCK-APP-1
- AI-CONTEXT-1
- OPERATOR-REVIEW-APP-1
- REPORT-ARCHIVE-APP-1
- DATA-QUALITY-OPS-APP-1
- MARKET-SCENARIO-APP-1
- BACKTEST-REVIEW-APP-1

## Evidence states

- NOT_EVALUATED
- SUPPORTED
- PARTIAL
- CONFLICT
- MISSING
- BLOCKED
- REVIEW_REQUIRED

## Overall statuses

- EVIDENCE_COMPLETE
- EVIDENCE_PARTIAL
- CONFLICT_DETECTED
- VALIDATION_BLOCKED
- REVIEW_REQUIRED

## Boundary

The evidence matrix is not a trade instruction.
It is not a buy signal.
It is not a sell signal.
It is not an order ticket.
It is not a position sizing rule.
It is not a portfolio action.
It is not a future return prediction.
It is not a guaranteed performance claim.

Operator review remains required.
