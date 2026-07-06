# WATCHLIST-LIFECYCLE-D3 Lifecycle Schema

## Purpose

D3 defines paper-only lifecycle states for local watchlist candidates.

It does not create trade instructions, position management, portfolio actions, future return predictions, or performance guarantees.

## States

- ENTRY_REVIEW
- ACTIVE_WATCH
- REVIEW_REQUIRED
- STALE_REVIEW
- DROP_REVIEW

## Allowed transitions

- ENTRY_REVIEW -> ACTIVE_WATCH, REVIEW_REQUIRED, DROP_REVIEW
- ACTIVE_WATCH -> REVIEW_REQUIRED, STALE_REVIEW, DROP_REVIEW
- REVIEW_REQUIRED -> ACTIVE_WATCH, STALE_REVIEW, DROP_REVIEW
- STALE_REVIEW -> REVIEW_REQUIRED, DROP_REVIEW
- DROP_REVIEW -> none

## Required record fields

- lifecycle_record_id
- candidate_id
- symbol
- current_state
- previous_state
- state_reason
- source_app_ids
- source_manifest_id
- operator_review_required
- operator_review_bypass_allowed
- trade_action_allowed
- real_execution_allowed
- position_management_allowed
- automatic_position_sizing_allowed
- automatic_portfolio_action_allowed
- future_return_prediction_allowed
- score_mutation_allowed
- reason_code_mutation_allowed
- risk_flag_deletion_allowed
- created_at_utc

## Required safety values

- operator_review_required = true
- operator_review_bypass_allowed = false
- trade_action_allowed = false
- real_execution_allowed = false
- position_management_allowed = false
- automatic_position_sizing_allowed = false
- automatic_portfolio_action_allowed = false
- future_return_prediction_allowed = false
- guaranteed_performance_claim_allowed = false
- score_mutation_allowed = false
- reason_code_mutation_allowed = false
- risk_flag_deletion_allowed = false
- source_content_mutation_allowed = false
- source_deletion_allowed = false
- source_overwrite_allowed = false

## D3 status

This stage only defines schemas and validation.
It does not load market data, alter upstream records, mutate scores, change reason codes, delete risk flags, or generate an executable action.
