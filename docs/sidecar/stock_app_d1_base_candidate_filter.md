# STOCK-APP-D1 Base Candidate Filter Contract

Status: implemented

Scope:
- Build a sidecar-only base candidate filter contract.
- Accept DATA-APP clean universe or watchlist records.
- Produce base candidate, watch-only, and rejected buckets.

Boundary:
- No core import.
- No P48 core expansion.
- No real trading.
- No exchange API.
- No brokerage API.
- No API keys.
- No real orders.
- No real execution.
- No real balances or positions.
- Operator review required.

Output fields:
- reason_codes
- risk_flags
- data_quality_state
- operator_review_required
- paper_only
- real_action_blocked
