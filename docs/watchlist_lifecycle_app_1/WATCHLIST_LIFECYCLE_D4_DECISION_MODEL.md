# WATCHLIST-LIFECYCLE-D4 Decision Model

## Purpose

D4 creates a paper-only lifecycle state evaluator for local watchlist candidates.

It reads candidate metadata and D2 source manifest metadata, then selects one of the D3 lifecycle states.

## Possible selected states

- ENTRY_REVIEW
- ACTIVE_WATCH
- REVIEW_REQUIRED
- STALE_REVIEW
- DROP_REVIEW

## Inputs

- candidate_id
- symbol
- previous_state
- risk_flags
- governance_status
- signal_validation_status
- operator_review_status
- source_app_ids
- source_manifest metadata

## Output

- selected_state
- decision_reasons
- risk_flags_observed
- blocking_risk_flags_observed
- source_health
- lifecycle_record
- lifecycle_record_valid
- lifecycle_record_issues

## Required boundary

- operator_review_required = true
- operator_review_bypass_allowed = false
- trade_action_allowed = false
- buy_instruction_allowed = false
- sell_instruction_allowed = false
- order_ticket_allowed = false
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

## D4 status

This stage only evaluates paper lifecycle states.
It does not trade, manage positions, size orders, mutate scores, rewrite reasons, delete risk flags, or predict returns.
