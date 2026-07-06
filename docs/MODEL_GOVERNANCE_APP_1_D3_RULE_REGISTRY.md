# MODEL-GOVERNANCE-APP-1 D3 Rule Registry

## Stage

MODEL-GOVERNANCE-D3

## Purpose

D3 defines the paper-only model rule registry and scoring policy snapshot schema.

It records governance metadata for:

- scoring policy
- reason codes
- risk flags
- signal validation status
- operator review policy
- scenario review policy
- backtest review policy
- data quality policy

## Registry statuses

- GOVERNANCE_READY_FOR_OPERATOR_REVIEW
- GOVERNANCE_REVIEW_REQUIRED
- GOVERNANCE_BLOCKED

## Boundary

The model rule registry is not a trading rule engine.
It does not mutate scores.
It does not mutate reason codes.
It does not delete risk flags.
It does not modify source files.
It does not modify P1-P47 core.
It does not create buy or sell instructions.
It does not create order tickets.
It does not create position sizing.
It does not create future return predictions.
It does not create guaranteed performance claims.

Operator review remains required.
