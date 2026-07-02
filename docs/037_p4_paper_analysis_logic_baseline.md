# P4-D1 To P4-D3 Paper Analysis Logic Baseline

Status: completed

Scope:
- P4-D1: price deviation analysis
- P4-D2: simple momentum and paper risk score
- P4-D3: paper signal draft and batch analysis baseline

Purpose:
- move from local data layer into analysis logic layer
- create the first rule-based paper-only signal draft
- preserve operator review before any later decision workflow

Current logic:
- compare price with reference_price
- classify deviation magnitude
- calculate simple momentum when price_history is available
- estimate baseline paper risk score
- draft paper-only signal
- support batch paper analysis

Important:
- This is not a real trading signal.
- This is not financial advice.
- This does not connect to exchanges.
- This does not place orders.
- This only creates paper-only analysis drafts.

Safety boundary:
- paper-only
- no real exchange API
- no real API key
- no wallet private key
- no real order
- no real execution
- no real balance
- no real position
- no real money impact
- operator review remains required

Architecture direction:
- BTC remains the first implementation line.
- Long-term target remains a general FCF-style finance platform for stocks and other markets.
