# STOCK-APP-D6 Ranked Watchlist Handoff

Status: implemented

Scope:
- Build ranked watchlist from limit-up potential scoring output.
- Build candidate report and operator review packet.
- Build read-only AI-CONTEXT handoff metadata.

Output:
- ranked_watchlist
- excluded
- candidate_report
- operator_review_packet
- handoff_to_ai_context

Boundary:
- Not a buy instruction.
- Not a sell instruction.
- Not a guaranteed limit-up claim.
- AI can explain only.
- AI cannot modify score.
- Operator review required.
- Paper-only.
- Real action blocked.
- No exchange API.
- No brokerage API.
- No API keys.
- No real orders.
- No real execution.
