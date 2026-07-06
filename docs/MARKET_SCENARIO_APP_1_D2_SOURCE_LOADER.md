# MARKET-SCENARIO-D2 Source Loader

Stage: MARKET-SCENARIO-D2
App: MARKET-SCENARIO-APP-1

Purpose:
Load local scenario source metadata for paper-only scenario review.

Allowed source groups:
- report_archive_outputs
- data_quality_ops_outputs
- operator_review_outputs
- ui_ai_stock_handoff_metadata

Loader rules:
- metadata only
- no source content mutation
- no source deletion
- no source overwrite
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

The loader does not convert scenario metadata into trade instructions.
