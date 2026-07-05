# STOCK-APP-D3 Volume Price Anomaly Rules

Status: implemented

Scope:
- Build sidecar-only volume-price anomaly rules.
- Detect near limit-up price, volume expansion, turnover expansion, close near high, and price breakout.
- Produce volume_price_score, reason_codes, risk_flags, data_quality_state, and confidence_level.

Boundary:
- No core import.
- No P48 core expansion.
- No AI scoring.
- No buy or sell instruction.
- No guaranteed limit-up claim.
- No real trading.
- No exchange API.
- No brokerage API.
- No API keys.
- No real orders.
- No real execution.
- Operator review required.
