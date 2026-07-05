# STOCK-APP-D4 Public Fund Flow Proxy Inference

Status: implemented

Scope:
- Build sidecar-only public fund-flow proxy inference.
- Use only public signals such as dragon tiger signal, northbound flow score, ETF flow score, large trade proxy, amount expansion, and sector fund heat.
- Produce fund_flow_proxy_score, reason_codes, risk_flags, data_quality_state, and confidence_level.

Boundary:
- Public signal only.
- No hidden position claim.
- No claim that institutions definitely bought.
- No main force certainty claim.
- No buy or sell instruction.
- No guaranteed limit-up claim.
- No real trading.
- No exchange API.
- No brokerage API.
- No API keys.
- No real orders.
- No real execution.
- Operator review required.
