# UI-APP-D3 Ranked Watchlist View Model

## Purpose

UI-APP-D3 converts the AI-CONTEXT handoff ranked watchlist into a local read-only UI view model.

## Inputs

- ranked_watchlist
- score_breakdown
- reason_codes
- risk_flags
- data_quality_state
- confidence_level
- operator_review_required

## Outputs

- local read-only ranked watchlist rows
- candidate score display values
- reason code display lists
- risk flag display lists
- operator review requirement state

## Safety boundary

The view model does not include:

- buy buttons
- sell buttons
- order buttons
- trade execution actions
- broker actions
- exchange actions
- credential access
- core mutation

All rows remain paper-only and operator-review-required.
