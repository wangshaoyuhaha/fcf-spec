# Multi-Market Paper and Shadow Validation Stage 10 D1-D6

## Scope

Stage 10 composes the six deterministic market adapters, Paper portfolio
construction, historical Paper validation, forward Shadow observation, and the
FCF Web Console. It does not invoke models or activate learning.

## D1 - Contracts

- immutable six-market identity and validation boundary
- separate historical Paper and forward Shadow windows
- registered portfolio, benchmark, observation, and market evidence
- explicit Operator trigger and review

## D2 - Market Coverage

- China A-share, US equity, Hong Kong equity, gold/commodity, digital asset,
  and futures coverage
- adapter status, calendar, currency, freshness, data-quality, and evidence
  visibility
- missing or blocked markets fail closed

## D3 - Paper Portfolio Validation

- deterministic candidate-versus-benchmark return
- notional, maximum loss, turnover, transaction cost, exposure breach, and
  cross-market disagreement visibility

## D4 - Shadow Observation

- decision-time cutoff and later observation requirement
- PENDING and MATURE states
- no fabricated pending result
- historical-forward overlap rejection
- direction contradiction and maturity coverage visibility
- no execution

## D5 - Review

- immutable per-market findings
- cross-market coverage and aggregate metrics
- risk, disagreement, contradiction, stale, degraded, and blocked reason codes
- immutable Operator review packet
- no approval, promotion, learning, archive, or baseline replacement

## D6 - Product Integration

- Stage 8 Portfolio Construction view integration
- Paper portfolio and Shadow observation view integration
- Stage 10 acceptance keeps controlled learning/backtesting P0-P3 as the next
  phase

## Deferred

- controlled learning and deterministic backtesting P0-P3
- deferred enhancements P4
- Dify, model-provider, Prompt, and live model invocation configuration
