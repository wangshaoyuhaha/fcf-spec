# AI-CONTEXT-1 D1-D3 Explanation Contract

Status: created

Scope:
- D1 sidecar boundary and explanation contract
- D2 read STOCK-APP ranked_watchlist contract
- D3 reason_codes and risk_flags explanation dictionary

Purpose:
- Generate read-only explanation reports from structured sidecar outputs.
- Preserve deterministic scores, reason codes, and risk flags.
- Support operator review before any downstream workflow.

Allowed:
- Read ranked_watchlist
- Read score_breakdown
- Read reason_codes
- Read risk_flags
- Read data_quality_state
- Generate structured explanation JSON

Forbidden:
- No score mutation
- No reason code fabrication
- No risk flag suppression
- No buy or sell instruction
- No limit-up guarantee
- No real trading
- No exchange API
- No brokerage API
- No API key
- No wallet private key
- No real order
- No real execution
- No real balance
- No real position
- No real money impact
- No core modification

Next:
- AI-CONTEXT-D4 structured JSON explanation output
- AI-CONTEXT-D5 operator review summary report
- AI-CONTEXT-D6 final handoff to UI-APP workflow
