# Portfolio Construction and Stress Test Stage 7 D1-D6

## Status

COMPLETED_VALIDATED_READY_FOR_MAIN_MERGE

## Applications

- `PORTFOLIO-CONSTRUCTION-APP-1`
- `PORTFOLIO-STRESS-TEST-APP-1`

## Approved flow

1. consume preserved deterministic ranked candidates
2. apply versioned eligibility and risk-budget configuration
3. calculate deterministic Paper weights and quantities
4. evaluate portfolio constraints and transaction costs
5. run versioned deterministic stress scenarios
6. create an immutable Paper proposal for Operator review

Portfolio Construction is downstream of ranking and is not an additional
selection factor.

## Deterministic controls

- single-asset, industry, theme, and factor concentration
- pair correlation, portfolio beta, and portfolio volatility
- source liquidity, stressed liquidity, and drawdown eligibility
- turnover and transaction-cost limits
- total risk budget and Paper lot sizing
- stress loss budget and position-level loss attribution

All thresholds and scenario shocks are supplied by immutable versioned policy
or scenario contracts. The source code does not establish constitutional
portfolio percentages.

## Paper proposal boundary

The output contains proposed Paper weights, notionals, and quantities only.
It cannot read an account, balance, or real position. It cannot rebalance,
submit an order, connect to a broker or exchange, or execute anything.

The Operator review packet preserves:

- original rank and deterministic score
- adapter identity and status
- evidence identities
- original risk inputs and factor exposures
- proposed Paper positions and cash weight
- exposure summaries and all constraint findings
- stress scenarios, loss attribution, and breach reasons

AI may explain this registered output but cannot calculate, modify, approve,
or activate authoritative weights.

## Permanent boundary

- P1-P47 frozen and no P48
- paper-only, local-only, loopback-only, sidecar-only
- registered-artifact-only and read-only inputs
- Operator review mandatory
- Deterministic Engine and Registered Evidence authority preserved
- AI advisory only
- no live data retrieval, model invocation, Prompt execution, credential,
  account, wallet, broker, exchange connection, balance, position read,
  automatic rebalance, order, execution, tag, release, or deployment path
