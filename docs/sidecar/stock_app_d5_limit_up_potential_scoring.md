# STOCK-APP-D5 Limit Up Potential Scoring Contract

Status: implemented

Scope:
- Combine base filter, sector/theme linkage, volume-price anomaly, and public fund-flow proxy outputs.
- Produce limit_up_potential_score, potential_level, score_breakdown, reason_codes, risk_flags, data_quality_state, confidence_level, and data_sources.

Important boundary:
- This is a ranked candidate score, not a buy instruction.
- This does not guarantee a limit-up move.
- PASS_LIMITED records remain WATCH_ONLY and cannot be high-ranked.
- AI may explain the output later but cannot modify the score.

Forbidden:
- No buy instruction.
- No sell instruction.
- No guaranteed limit-up claim.
- No hidden position claim.
- No real trading.
- No exchange API.
- No brokerage API.
- No API keys.
- No real orders.
- No real execution.
- Operator review required.
