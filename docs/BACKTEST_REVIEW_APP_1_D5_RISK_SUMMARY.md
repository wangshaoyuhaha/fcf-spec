# BACKTEST-REVIEW-D5 Backtest Risk Summary

Stage: BACKTEST-REVIEW-D5
App: BACKTEST-REVIEW-APP-1

Purpose:
Generate a paper-only local backtest risk summary.

Risk item fields:
- risk_id
- review_id
- result_packet_id
- risk_category
- risk_level
- description
- evidence_metric_ids
- mitigation_note
- operator_review_required

Risk summary fields:
- summary_id
- stage_id
- review_id
- result_packet_id
- overall_risk_level
- risk_items
- risk_flags
- limitations
- summary_status
- operator_review_required
- safety_flags
- generated_at_utc
- notes

Safety:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- risk summary must not become a trade instruction
- risk summary must not become a profit guarantee
- no order ticket
- no real execution
- no real account access
- no real position access
- no automatic position sizing
- no automatic portfolio action
- no future return prediction
- no guaranteed performance claim
