# MARKET-SCENARIO-D3 Scenario Definition Schema

Stage: MARKET-SCENARIO-D3
App: MARKET-SCENARIO-APP-1

Purpose:
Define a paper-only local market scenario definition schema.

The schema can describe:
- scenario_id
- scenario_label
- scenario_type
- market_scope
- asset_classes
- time_horizon
- source_metadata_ids
- data_quality_state
- confidence_level
- scenario_score
- scenario_review_status
- operator_review_required
- notes

Allowed scenario types:
- base_case
- risk_off
- risk_on
- liquidity_stress
- data_quality_degraded
- policy_event
- earnings_event
- crypto_volatility
- futures_basis_shift

Safety:
- scenario_label must not become a trade instruction
- scenario_score must not become a trade instruction
- scenario_review_status must not bypass operator review
- scenario packet must not become an order ticket
- no automatic position sizing
- no automatic portfolio action
- no live market order
- no real account state
- no real execution
