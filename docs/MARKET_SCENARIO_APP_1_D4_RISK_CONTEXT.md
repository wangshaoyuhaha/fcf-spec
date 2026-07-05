# MARKET-SCENARIO-D4 Assumption and Risk Context Model

Stage: MARKET-SCENARIO-D4
App: MARKET-SCENARIO-APP-1

Purpose:
Define paper-only scenario assumptions and risk context records.

Scenario assumption fields:
- assumption_id
- scenario_id
- assumption_type
- description
- evidence_source_ids
- confidence_level
- data_quality_state
- operator_review_required
- trade_instruction_allowed
- real_execution_allowed

Risk context fields:
- risk_context_id
- scenario_id
- risk_level
- risk_factors
- risk_flags
- source_metadata_ids
- scenario_score_adjustment
- mitigation_notes
- operator_review_required
- scenario_score_as_trade_instruction
- automatic_position_sizing_allowed
- automatic_portfolio_action_allowed
- order_ticket_allowed
- real_execution_allowed

Safety:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no trade instruction
- no order ticket
- no automatic position sizing
- no automatic portfolio action
- no real execution
