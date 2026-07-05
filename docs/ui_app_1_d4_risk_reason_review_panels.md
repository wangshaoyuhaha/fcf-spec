# UI-APP-D4 Risk, Reason, and Operator Review Panels

## Purpose

UI-APP-D4 renders read-only local panels for:

- reason codes
- risk flags
- operator review summary

## Inputs

- ranked watchlist view model
- AI-CONTEXT handoff payload
- operator review summary

## Panels

- reason_codes_panel
- risk_flags_panel
- operator_review_summary_panel

## Safety boundary

These panels are display-only.

They do not provide:

- buy buttons
- sell buttons
- order buttons
- broker connection
- exchange connection
- real execution
- operator review bypass
- core mutation

All panels remain paper-only, local-only, read-only, sidecar-only, and operator-review-required.
