# BACKTEST-REVIEW-D1 Contract

Stage: BACKTEST-REVIEW-D1
App: BACKTEST-REVIEW-APP-1

Purpose:
Define the paper-only local sidecar boundary and backtest review contract.

Allowed inputs:
- report_archive_outputs
- market_scenario_outputs
- operator_review_outputs
- data_quality_ops_outputs
- ui_ai_stock_handoff_metadata

Allowed outputs:
- backtest_review_contract
- backtest_source_loader_contract
- backtest_review_schema
- backtest_result_packet
- backtest_risk_summary
- paper_only_backtest_review_packet
- final_workflow_handoff

Required boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator_review_required

Forbidden:
- no P48 core expansion
- no P1-P47 core mutation
- no source content mutation
- no source deletion
- no source overwrite
- no real trading
- no real execution
- no broker connection
- no exchange connection
- no API key storage
- no wallet private key access
- no real account access
- no real position access
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

Backtest-specific forbidden scope:
- backtest_result must not become a profit guarantee
- backtest_metric must not become a trade instruction
- backtest_review_status must not bypass operator review
- backtest packet must not become an order ticket
- no automatic position sizing
- no automatic portfolio action
- no live market order
- no real account state
- no future return prediction
- no guaranteed performance claim
