# BACKTEST-REVIEW-D3 Backtest Review Schema

Stage: BACKTEST-REVIEW-D3
App: BACKTEST-REVIEW-APP-1

Purpose:
Define a paper-only local backtest review schema.

The schema can describe:
- review_id
- review_label
- review_type
- market_scope
- asset_classes
- replay_window
- source_metadata_ids
- scenario_ids
- data_quality_state
- confidence_level
- review_status
- operator_review_required
- backtest metric definitions

Allowed review types:
- paper_signal_replay
- scenario_outcome_review
- quality_gated_replay
- operator_decision_review
- archive_replay
- risk_flag_replay

Safety:
- review result must not become a profit guarantee
- review metric must not become a trade instruction
- review status must not bypass operator review
- review packet must not become an order ticket
- no automatic position sizing
- no automatic portfolio action
- no live market order
- no real account state
- no future return prediction
- no guaranteed performance claim
