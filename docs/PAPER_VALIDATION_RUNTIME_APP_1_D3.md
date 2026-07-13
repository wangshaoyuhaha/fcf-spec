# PAPER-VALIDATION-RUNTIME-APP-1 D3

## Scope

D3 implements deterministic candidate-versus-baseline metrics and policy
comparison.

## Metrics

The engine calculates:

- total, eligible, excluded, scored, and abstained sample counts
- candidate coverage
- baseline MAE
- candidate MAE
- MAE delta
- baseline classification accuracy
- candidate classification accuracy
- accuracy delta
- per-segment summaries

## Blocking policy

The engine can block on:

- insufficient eligible samples
- insufficient candidate coverage
- overall MAE regression
- overall accuracy delta below policy
- missing required segment
- insufficient required-segment samples
- required-segment MAE regression

## Result authority

A non-blocked result is only READY_FOR_OPERATOR_REVIEW.

It is never an approval, promotion, baseline replacement, activation, archive,
or execution authorization.

Outputs remain paper-only, deterministic, and Operator-reviewed.
