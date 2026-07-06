# BACKTEST-REVIEW-D2 Source Loader

Stage: BACKTEST-REVIEW-D2
App: BACKTEST-REVIEW-APP-1

Purpose:
Load local backtest review source metadata for paper-only historical review.

Allowed source groups:
- report_archive_outputs
- market_scenario_outputs
- operator_review_outputs
- data_quality_ops_outputs
- ui_ai_stock_handoff_metadata

Loader rules:
- metadata only
- no source content reading
- no source content mutation
- no source deletion
- no source overwrite
- no real account access
- no real position access
- no real trading
- no real execution
- no broker connection
- no exchange connection
- no API key storage
- no wallet private key access
- operator review required

Output:
- stage_id
- source_count
- source_kinds_found
- metadata records
- safety_flags

The loader does not convert historical metadata into trade instructions,
profit guarantees, order tickets, or execution requests.
