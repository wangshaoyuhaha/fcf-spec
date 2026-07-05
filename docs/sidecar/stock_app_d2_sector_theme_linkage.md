# STOCK-APP-D2 Sector Theme Linkage Contract

Status: implemented

Scope:
- Build a sidecar-only sector and theme linkage contract.
- Evaluate sector strength, theme heat, and market breadth.
- Produce sector_theme_score, reason_codes, risk_flags, and confidence_level.

Input fields:
- symbol
- name
- sector_code
- sector_name
- theme_tags
- sector_strength_score
- theme_heat_score
- market_breadth_score
- data_quality_state

Boundary:
- No core import.
- No P48 core expansion.
- No AI scoring.
- No buy or sell instruction.
- No real trading.
- No exchange API.
- No brokerage API.
- No API keys.
- No real orders.
- No real execution.
- Operator review required.
