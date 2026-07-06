# SIGNAL-VALIDATION-APP-1 D4 Conflict Detector

## Stage

SIGNAL-VALIDATION-D4

## Purpose

D4 adds paper-only conflict and inconsistency detection for signal evidence.

It checks for conflicts such as:

- high score with data quality issue
- positive explanation with unresolved risk flag
- scenario and backtest mismatch
- missing operator review
- missing or partial source evidence
- archive integrity gap

## Output

D4 outputs a signal conflict report with:

- detection_status
- conflict_count
- blocking_conflict_count
- high_conflict_count
- conflict_type
- severity
- involved_layers
- evidence_refs
- operator_review_required

## Boundary

The conflict report is not a trade instruction.
It is not an order ticket.
It is not a position sizing rule.
It is not a portfolio action.
It is not a future return prediction.
It is not a guaranteed performance claim.

Operator review remains required.
