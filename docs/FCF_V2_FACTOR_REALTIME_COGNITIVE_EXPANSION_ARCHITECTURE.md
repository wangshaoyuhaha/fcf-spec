# FCF V2 Factor, Realtime, and Cognitive Expansion Architecture

Status: ACCEPTED_ARCHITECTURE

Implementation status: NOT_IMPLEMENTED

This document is the canonical future-architecture specification for factor
research, realtime market awareness, capital-flow research, order-book
microstructure, macro-to-micro analysis, asynchronous AI explanation, and
Operator review.

It consolidates the Operator proposal and the reviewed engineering additions.
It does not authorize product implementation, network access, data purchase,
credentials, model invocation, Prompt execution, training, or execution.

## 1. Status Vocabulary

Future capabilities use only these statuses:

- `ACCEPTED_ARCHITECTURE`
- `PLANNED`
- `BACKLOG`
- `RESEARCH_REQUIRED`
- `NOT_IMPLEMENTED`
- `OUTSIDE_CURRENT_AUTHORIZATION`

`OUTSIDE_CURRENT_AUTHORIZATION` means the capability is intentionally
excluded from current authority and is not a queued implementation phase.

They must not be labeled `COMPLETED`, `DELIVERED`, `PRODUCTION_READY`, or
`VALIDATED` until implementation and the full governed acceptance workflow
actually finish.

## 2. Permanent Authority Model

Authority is domain-scoped rather than represented by one global ranking.

### Hard Policy and Data-Quality or Security Gate

The gate has non-overridable blocking authority for:

- stale or interrupted data
- timestamp or sequence failure
- order-book desynchronization
- unregistered source or failed digest
- unresolved multi-source conflict
- unclear data rights
- sensitive-data exposure
- account or trading endpoint exposure
- any real-execution capability inside this repository

The Operator cannot override a hard circuit breaker.

### Deterministic Engine

Deterministic code is the only authority for:

- formulas, indicators, factors, normalization, and neutralization
- weights, ranking, risk penalties, and hard filters
- anomaly calculations and state transitions
- backtest, cost, slippage, capacity, and Paper simulation calculations
- calibration and system-confidence calculations

### Registered Evidence

Registered Evidence is the only authority for source identity and lineage:

- source, version, license, and permitted use
- event, publication, availability, ingestion, and retrieval time
- content digest and artifact lineage
- model and Prompt identity when applicable
- correlation and research-run identity

### Operator

The Operator may accept, reject, request evidence, acknowledge risk, and
authorize archive review. The Operator cannot alter deterministic scores,
delete risk flags, convert stale data to fresh, bypass a circuit breaker, or
turn Paper research into real execution.

### AI

AI may explain, summarize, challenge, compare, discuss scenarios, and propose
research hypotheses. AI cannot change factors, formulas, official weights,
risk flags, hard policy, evidence truth, or any execution state.

## 3. Four Capability Planes

### Realtime Data Plane

Future responsibilities:

- approved read-only market-data ingestion
- Tick, trade, quote, and order-book event handling
- time synchronization and event ordering
- data cleaning, quality, interruption, and conflict detection
- immutable snapshots and initial low-cost anomaly screening

Status: PLANNED / NOT_IMPLEMENTED

### Factor and Analytics Plane

Future responsibilities:

- Factor Registry and deterministic factor calculation
- technical, fundamental, capital-flow, breadth, and microstructure research
- market-regime classification and multi-horizon scoring
- factor validation, de-duplication, and attribution
- Champion and Challenger research
- backtesting, forward observation, and Paper simulation

Status: PLANNED / PARTIALLY SUPPORTED BY EXISTING STRUCTURAL FOUNDATIONS /
NEW FACTOR RUNTIME NOT_IMPLEMENTED

### Cognitive and Governance Plane

Future responsibilities:

- asynchronous AI explanation and contrarian review
- macro-to-micro narrative and causal-evidence inspection
- evidence, model, and Prompt governance
- privacy policy, uncertainty, contradiction, and audit records
- mandatory Operator review

Status: PLANNED / LIVE INVOCATION NOT_IMPLEMENTED

### Workspace Plane

Future responsibilities:

- candidate pools and multi-horizon views
- risk, invalidation, data-health, and circuit-breaker visibility
- alert review, history, replay, and Operator decisions
- read-only product status and audit presentation

Status: ACCEPTED_ARCHITECTURE / FUTURE INTERACTIVE FEATURES NOT_IMPLEMENTED

The four planes define ownership. They do not require four monolithic modules.
Future code remains decomposed into bounded Sidecars.

## 4. Service and Resource Isolation

Realtime services and research-governance services must have separate:

- processes and service lifecycles
- CPU and memory budgets
- queues and failure domains
- health and degradation states

They communicate through versioned structured event packages. Realtime failure
must not take down governance. AI failure must never block deterministic
processing. Different physical machines are not constitutionally required.

## 5. Deterministic Factor Registry

Every official factor must be registered before deterministic code may use it
in an official score.

Required identity and research fields:

- `factor_id`, `factor_name`, `factor_family`
- `financial_hypothesis`, `asset_class`, `market`, `instrument_scope`
- `research_horizon`, `input_frequency`, `output_frequency`
- `formula`, `formula_version`, `parameter_schema`, `parameter_version`
- `input_fields`, `source_requirements`, `point_in_time_required`
- `lookback_window`, `minimum_history`

Required processing fields:

- `normalization_method`, `winsorization_method`
- `missing_value_policy`, `outlier_policy`, `neutralization_policy`
- `expected_direction`, `valid_market_regimes`, `invalid_market_regimes`

Required governance fields:

- `risk_flags`, `known_failure_modes`, `validation_status`
- `champion_challenger_status`, `approved_by`, `evidence_refs`
- `correlation_id`, `effective_at`, `retired_at`
- `owner`, `dependency_factor_ids`, `dependency_data_fields`
- `calculation_unit`, `output_range`, `deterministic_test_vectors`
- `reference_implementation_version`, `compute_cost_class`
- `revision_policy`, `backfill_policy`, `replacement_factor_id`

Lifecycle:

`DRAFT -> RESEARCH -> CHALLENGER -> QUALIFIED -> CHAMPION -> DEGRADED -> RETIRED`

Temporary formulas cannot bypass this registry.

Status: CONTRACT_FOUNDATION_IMPLEMENTED / PRODUCTION_RUNTIME_NOT_IMPLEMENTED

V2-R1 implements the immutable metadata contract and append-only local
registry foundation. It does not calculate or activate a factor, populate a
production registry, or change an official score.

## 6. Forecast Target and Outcome Label Contract

No factor program may optimize an undefined statement such as "predict price."
Every research target must register:

- `target_id` and `target_version`
- instrument and market scope
- decision `as_of_time`
- forecast horizon and maturity rule
- target type and exact formula
- absolute or benchmark-relative basis
- return, volatility, drawdown, liquidity, or anomaly objective
- cost, slippage, and capacity treatment
- label availability time
- benchmark and neutralization policy
- missing, invalid, censored, and abstention behavior
- evaluation metrics and minimum sample policy

Candidate targets may include future relative return, realized volatility,
maximum favorable or adverse movement, anomaly persistence, breakout
durability, sector confirmation, liquidity deterioration, and order-flow
persistence.

Outcome labels must preserve the original prediction, original evidence,
decision time, observation window, actual outcome, data version, and evaluation
policy. Post-hoc information cannot be rewritten into the original label.

Status: CONTRACT_FOUNDATION_IMPLEMENTED / TARGET SELECTION RESEARCH_REQUIRED /
PRODUCTION_LABEL_RUNTIME_NOT_IMPLEMENTED

## 7. State-Sync Lock

Realtime detection, historical baseline, deterministic factors, and AI
explanation must refer to the same frozen state.

Every event package requires at least:

- `event_id`, `instrument_id`
- `event_time`, `source_event_time`, `ingest_time`, `processing_time`
- `snapshot_id`, `state_hash`, `snapshot_ttl`
- `baseline_version`, `source_sequence`, `factor_version`
- `data_quality_state`, `data_latency_ms`

Deterministic code freezes the state when it creates an anomaly event. AI may
explain only the registered state hash. It may not retrieve a later state and
replace the explanation basis.

Expired state behavior:

- set `STATE_EXPIRED`
- stop the official explanation for that event
- preserve the old event and audit record
- create a new event from a new snapshot when required

Status: CONTRACT_ANCHOR_IMPLEMENTED / PRODUCTION_RUNTIME_NOT_IMPLEMENTED

V2-R1 provides deterministic local canonical hashing, timestamp ordering, TTL,
and expiry validation for registered artifact metadata. It is not realtime
ingestion, remote synchronization, or a production State-Sync service.

## 8. Macro-to-Micro Transmission Contract

The official research chain is:

`Macro -> Asset Class -> Market -> Sector -> Instrument -> Microstructure`

Each transmission record requires:

- `transmission_id` and version
- registered macro event and publication time
- expected value, observed value, and surprise definition where applicable
- source evidence and availability time
- affected asset classes, markets, sectors, and instruments
- hypothesized direction, mechanism, horizon, and decay
- supporting and contradicting evidence
- market-regime dependency
- state hash and correlation identity
- invalidation, expiry, and uncertainty

The causal-evidence registry stores hypotheses and evidence. It does not claim
causal truth merely from correlation. Deterministic code calculates registered
features; AI may explain or challenge the transmission path.

Status: ACCEPTED_ARCHITECTURE / RESEARCH_REQUIRED

## 9. Research-Horizon Isolation

The platform maintains separate research outputs for:

- medium-horizon equity research: days to months
- short-horizon equity research: one to several days
- A-share intraday research: seconds, minutes, and close auction
- BTC short-horizon research: Tick, seconds, and one to fifteen minutes

Different horizons cannot share one mixed total score. Every output records its
horizon, maturity, benchmark, applicable regime, and invalidation conditions.

When horizons disagree:

- preserve every horizon result
- do not average conflicting results into false consensus
- allow a short-horizon hard-risk state to block a short-horizon alert
- do not silently delete a medium-horizon thesis
- show the conflict and evidence to the Operator

Status: ACCEPTED_ARCHITECTURE / CONFLICT RESOLVER NOT_IMPLEMENTED

## 10. Security Master and Candidate Universe

The versioned Security Master must record market and date-dependent rules:

- instrument, venue, board, listing, suspension, and special-treatment status
- listing date, delisting state, price limits, and minimum tick
- sessions, auctions, settlement, and T+1 where applicable
- corporate actions, adjustment method, and effective date

Candidate-universe filters are versioned and may include listing age,
liquidity, turnover continuity, suspension, special treatment, price, size,
and data-quality class.

`WATCHLIST_ONLY` cannot rank with `CLEAN_UNIVERSE` as an equal-quality input.

## 11. Technical and Market Factor Catalog

All entries below are candidates until individually registered and validated.

### Trend

- SMA, EMA, MA5, MA10, MA20, and MA60
- moving-average alignment and slope
- price distance from moving averages
- Donchian channels, ADX, rising highs or lows, and trend duration

### Momentum and Mean Reversion

- cross-sectional and time-series momentum
- index-relative and sector-relative strength
- risk-adjusted momentum and recent-period exclusion
- MA and VWAP deviation
- Bollinger Z-score, RSI, short reversal, and gap reversion

### Breakout and Volatility

- range, prior-high, and Donchian breakout
- Bollinger Band Width and Bollinger breakout behavior
- ATR and volatility expansion
- historical and realized volatility
- Parkinson and Garman-Klass estimators
- upside or downside asymmetry and jump volatility

### Technical Oscillators

- MACD, RSI, KDJ, ROC, Momentum, TRIX, and PPO

Highly correlated indicators cannot all receive equal weight. Initial Champion
sets use a small representative subset; others remain Challengers.

### Volume, Turnover, and VWAP

- relative and same-time historical volume
- notional velocity and turnover change
- OBV, MFI, Volume Price Trend, and volume-price divergence
- VWAP level, slope, deviation, breakout, and retest
- multi-period VWAP and volume concentration zones

### Market Breadth and Sector Rotation

- advance or decline breadth and new highs or lows
- sector returns, participation, turnover share, and dispersion
- limit-up, failed-limit, leader, and follower structure
- instrument-relative sector strength

### Fundamental, Event, and Policy

- ROE, ROIC, margins, growth, cash flow, leverage, and earnings quality
- valuation, industry-relative valuation, and expectation revision
- reports, guidance, repurchase, ownership change, restructuring, penalties,
  industrial policy, product release, material contract, and macro event

Fundamental and event data must be point-in-time and publication-time aware.

### Risk Factors

- acceleration, repeated limit-up, gaps, illiquidity, and price impact
- concentration, crowding, volatility, stale data, and financial risk
- event uncertainty, order-book fragility, failed-limit decay
- market and sector retreat

Risk factors may penalize, limit, downgrade, or hard-block. AI cannot delete
them.

Status: BACKLOG / INDIVIDUAL FACTORS NOT_IMPLEMENTED UNLESS ALREADY REGISTERED
BY AN EXISTING COMPLETED COMPONENT

## 12. Capital-Flow Research Contract

Candidate fields include:

- aggressive buy and sell volume
- buy or sell ratio and CVD
- large-trade net flow and share of notional
- persistent direction and price-flow divergence
- sector-relative flow
- margin-financing change, ETF flow, eligible public cross-border flow
- public leader-board, block-trade, and concentration data

Every field must declare:

- vendor and venue coverage
- raw trade data or inferred proxy
- aggressor-classification algorithm
- frequency and history coverage
- license and permitted use
- correction and revision behavior
- known error and confidence class
- whether it may contribute to a hard decision

"Main capital flow" is never assumed to be verified institutional trading.

Status: RESEARCH_REQUIRED / NOT_IMPLEMENTED

## 13. Order-Book and Microstructure Research Contract

Candidate features include:

- spread, relative spread, five-level or ten-level depth
- depth slope, concentration, imbalance, thinning, and liquidity vacuum
- order-flow imbalance from adds, cancels, and aggressive trades
- microprice and CVD behavior
- cancel-to-order and cancel-to-trade ratios
- order lifetime, book half-life, replenishment, and execution realization
- Amihud illiquidity, Kyle lambda, Roll spread, level-by-level cost
- market impact, capacity, and partial-fill probability

Risk labels may include:

- `FLEETING_LIQUIDITY`
- `LOW_ORDER_PERSISTENCE`
- `HIGH_CANCEL_INTENSITY`
- `NON_DURABLE_DEPTH`
- `POTENTIAL_ORDER_BOOK_DISTORTION`

Order-book evidence alone cannot establish illegal manipulation. Hidden and
iceberg liquidity, aggregation error, sampling frequency, and network latency
must remain visible limitations.

Status: RESEARCH_REQUIRED / NOT_IMPLEMENTED

## 14. Realtime Event Semantics

Any future realtime source contract must define:

- snapshot and incremental-delta behavior
- source sequence and checksum
- duplicate, out-of-order, late, and missing-event behavior
- resynchronization and restart recovery
- exchange time, source time, receive time, and processing time
- clock-skew tolerance and drift state
- locked or crossed book handling
- correction, cancel, and backfill semantics
- idempotency and replay identity

Directional output stops when sequence, checksum, timing, or source conflict is
unresolved.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 15. A-Share Intraday Anomaly Radar

The first-level scan uses low-cost features such as short-window price change,
notional velocity, same-time relative volume, turnover change, intraday high,
VWAP deviation, index or sector strength, distance to price limit, sector
synchronization, and market breadth.

Only first-level candidates may enter second-level monitoring for order-book,
trade, aggressor, CVD, cancel, book-life, impact, sealed-limit, failed-limit,
and asynchronous explanation research.

Thresholds depend on market volatility, market turnover, instrument liquidity,
sector state, intraday time, and historical percentile. Permanent fixed volume,
speed, or synchronization thresholds are prohibited.

This radar improves discovery efficiency. It does not guarantee limit-up or
profitable outcomes.

Status: PLANNED / NOT_IMPLEMENTED

## 16. BTC Short-Horizon Paper Research

Research inputs may include Tick, order book, aggressive trades, CVD, open
interest, funding, basis, mark price, index price, liquidation, and
multi-venue prices.

Future deterministic Paper scenario research may model maker or taker fees,
level-by-level slippage, partial fills, network and compute delay, funding,
maintenance margin, mark-price liquidation, liquidation cost, extreme spread,
order-book thinning, outage, adverse movement, loss streak, and leverage
sensitivity.

This is simulation research only. It does not authorize a virtual account,
Paper order dispatcher, exchange connection, or leverage runtime in this
repository.

Slippage must prefer registered historical or approved realtime order-book
depth rather than a permanently hardcoded generic exponential function.
Funding rules must be registered by venue, contract, and effective time.

Status: RESEARCH_REQUIRED / NOT_IMPLEMENTED

## 17. Mathematical Processing

Supported research methods may include:

- simple, log, excess, sector-adjusted, and volatility-adjusted returns
- winsorization, quantile clipping, MAD, and Huber treatment
- percentile rank, robust Z-score, Z-score, and time-series normalization
- industry, size, beta, volatility, and liquidity neutralization

Missing values distinguish not-applicable, not-yet-published, missing,
source-failure, and true zero. Uniform zero filling is prohibited.

Factor direction must state higher-is-better, lower-is-better,
middle-range-is-better, or regime-specific behavior.

## 18. Factor De-Duplication and Composition

Research controls include Pearson, Spearman, clustering, VIF, condition
number, incremental contribution, and ablation tests. PCA and orthogonalization
are diagnostic or Challenger methods, not the sole initial official method.

The first Champion must be simple, low-parameter, explainable, and
reproducible. A candidate formula is:

`Total Score = Sum(Weight * Normalized Factor) - Risk Penalties`

Weights, component scores, group caps, correlation controls, hard gates, and
versions remain traceable. AI output never enters official weights directly.

Initial Champion weighting favors equal, grouped-equal, expert-constrained, or
fixed versioned weights. IC, ICIR, constrained regression, Logistic
Regression, Elastic Net, Gradient Boosting, Random Forest, Bayesian averaging,
regime-dependent weights, HMM, and Markov Switching remain Challengers. A
machine-learning method cannot silently replace a transparent Champion.

Interaction candidates may include trend by volume, breakout by sector
strength, flow by price confirmation, book imbalance by trade velocity, open
interest by price change, and closing acceleration by sealed-limit stability.
Every interaction needs a registered financial hypothesis. Unbounded feature
enumeration is prohibited.

## 19. Anomaly Detection and Alert Lifecycle

Transparent initial methods include historical percentile, robust Z-score,
EWMA, CUSUM, rolling median or MAD, same-time baseline, change rate, and
multi-signal confirmation.

Complex methods such as change-point detection, Isolation Forest, One-Class
SVM, Local Outlier Factor, Autoencoder, and Bayesian online change detection
remain Challengers. A complex model alone cannot trigger the highest alert.

Alert states:

- `NORMAL`, `WATCH`, `CONFIRMED`, `PRIORITY_REVIEW`
- `DEGRADED`, `INVALIDATED`, `COOLDOWN`, `ARCHIVED`

Escalation requires independent factor groups, qualified data, persistence,
no critical counter-risk, and supporting regime. De-escalation records signal
loss, reversal, state expiry, source degradation, or contrarian risk.

Alert-fatigue controls include event merge, instrument cooldown, sector
clustering, low-priority suppression, review budget, and archive policy.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 20. Data-Source Governance and Operating Modes

Any future paid or external data source requires license, purpose, field,
retention, recomputation, latency, cost, rate-limit, concurrency, revocation,
and rotation review. Any future credential must be read-only and isolated from
AI context, reports, logs, and Git. It must have no account, balance, position,
order, withdrawal, or execution permission.

Multi-source conflict sets `SPLIT_FAULT`, stops directional output, preserves
raw sources, enters quarantine, and emits a status report.

A Data Quality Credit Score may provide auxiliary confidence. It cannot
replace a hard circuit breaker.

Future external service roles remain separated:

- a data service may supply approved read-only market, order-book, trade,
  filing, announcement, news, and derivative data
- a compute service may run deterministic Python streams, scans, books,
  factors, databases, queues, replay, and backtests
- a model service may interpret news, announcements, policy, causal evidence,
  contrarian findings, and reports

A model service does not calculate Tick data, maintain an order book, compute
official technical indicators, produce official scores, or own hard policy.

Operating-mode candidates:

- Offline Sovereign Mode: ACCEPTED_ARCHITECTURE
- Live Read-Only Sovereign Mode: RESEARCH_REQUIRED / NOT AUTHORIZED
- Secure Remote Compute Mode: RESEARCH_REQUIRED / NOT AUTHORIZED
- Paper Simulation Artifact Mode: RESEARCH_REQUIRED / NO ORDER RUNTIME
- Real Execution Mode: OUTSIDE FCF AND PROHIBITED IN THIS REPOSITORY

Current permanent local-only and loopback-only boundaries remain binding.

## 21. AI Asynchronous Cognitive Shield

Deterministic processing never waits for AI. Future AI tasks require
configurable task-specific timeout, an absolute policy maximum, registered and
validated fallback, and `COGNITIVE_TIMEOUT` when unavailable.

If no approved fallback exists, explanation is skipped. AI failure cannot
block a deterministic alert. No permanent fixed timeout such as eight seconds
is constitutional.

Status: ACCEPTED_ARCHITECTURE / MODEL INVOCATION NOT_IMPLEMENTED

## 22. Uncertainty, Calibration, and Abstention

The system must support explicit non-answer states:

- `INSUFFICIENT_EVIDENCE`
- `DATA_CONFLICT`
- `LOW_CONFIDENCE`
- `REGIME_UNSUPPORTED`
- `STATE_EXPIRED`
- `ABSTAIN_REVIEW_REQUIRED`

Evaluation may include Brier score, calibration error, confidence interval,
sample size, regime coverage, and data-quality discount. Model confidence is
not system confidence.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 23. Operational Health, Replay, and Recovery

Future realtime services require versioned service objectives for:

- source and processing latency
- event throughput, queue depth, and loss rate
- sequence gaps and resynchronization
- factor-compute and explanation latency
- snapshot expiry and source availability
- replay consistency and idempotency
- recovery time, retained history, and capacity

Required degradation modes must remain visible. Historical replay, synthetic
fault injection, and deterministic recovery tests must cover interruption,
clock reversal, sequence gaps, source conflict, AI timeout, stale snapshot,
queue pressure, and restart.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 24. Backtest and Leakage Law

Required controls include point-in-time data, survivorship and delisting,
historical membership, filing publication time, corporate actions, suspension,
price limits, T+1, fees, slippage, capacity, partial fills, delay, revisions,
and timestamp order.

Validation uses separated train, validation, and final test data, walk-forward,
rolling or expanding windows, purging, embargo, regime partitions, stress,
parameter sensitivity, and forward Paper observation.

Advanced backlog includes false-discovery control, deflated Sharpe,
probability of backtest overfitting, White's Reality Check, and SPA tests.

AI historical explanation uses fixed registered evidence and cannot use live
retrieval. Model, Prompt, tool, and configuration versions remain fixed and
registered for reproduction. Explanation quality is evaluated separately from
strategy return. Anonymization can reduce but cannot eliminate leakage risk.

## 25. Evaluation Metrics

Factor evaluation may include IC, Rank IC, ICIR, quantile portfolios,
monotonicity, factor return, decay, turnover, stability, regime behavior,
capacity, and incremental contribution.

Strategy evaluation may include net return, benchmark excess, drawdown,
volatility, Sharpe, Sortino, Calmar, Profit Factor, win or loss ratio, tail
loss, VaR or CVaR, cost, slippage, turnover, and capacity.

Alert evaluation may include precision, recall, false-positive rate, lead time,
maximum favorable or adverse movement, persistence, repeat rate, Operator
acceptance, circuit-break rate, and latency.

## 26. Champion and Challenger

Promotion requires stable target improvement after cost and slippage, no
unacceptable risk deterioration, multi-regime stability, out-of-sample and
forward Paper evidence, parameter stability, attributable improvement,
multiple-testing review, and explicit Operator approval.

No mechanical rule requires every metric to exceed Champion. Promotion creates
a new version and never overwrites the old Champion.

Human feedback is evidence, not automatic truth. It records whether feedback
was pre-outcome or post-hoc. A conflict between human preference and
deterministic evaluation preserves both sides, creates a review artifact, and
blocks promotion until explicit conflict review. Model consensus never
replaces evidence.

## 27. Implementation Readiness Gate

No future product Sidecar branch may start until it has:

- business objective and research horizon
- exact data fields, rights, source, and cost estimate
- exact formula, target label, and interfaces
- safety and privacy boundary
- failure and degradation behavior
- test, replay, rollback, and generated-output plan
- acceptance metrics and stop criteria
- dependency and resource estimate
- Control Center approval record

Failure to pass this gate means `NOT_APPROVED` and `NOT_IMPLEMENTED`.

## 28. Single-Market MVP Gate

The first realtime MVP selects one market only. A-share, BTC, and futures
realtime work cannot start together.

Selection remains an Operator decision based on data rights, data reliability,
engineering objective, cost, and product fit.

Minimum MVP scope:

1. one approved read-only data source
2. data quality and State-Sync Lock
3. a small transparent factor set
4. first-level scan and bounded second-level monitoring
5. graded alerts and read-only browser status
6. historical replay and asynchronous advisory explanation
7. no real trading or execution

Status: PLANNED / MARKET NOT_SELECTED / NOT_IMPLEMENTED

## 29. MVP Success and Stop Rules

The MVP must define success, failure, and stop thresholds before development.
Possible stop conditions include unacceptable license terms, excessive data or
compute cost, insufficient latency, unstable out-of-sample results, excessive
false alerts, unmanageable Operator workload, unverified flow proxy,
insufficient order-book quality, and unproven product value.

Stopping an MVP preserves evidence and does not rewrite it as success.

## 30. V2-R Roadmap

- V2-R0: historical prerequisite reconciliation; satisfied by repository truth
- V2-R1: Factor Contract Foundation; COMPLETED / CONTRACT_FOUNDATION_ONLY
- V2-R2: Historical Factor Baseline; COMPLETED /
  REGISTERED_LOCAL_ARTIFACT_ONLY
- V2-R3: Realtime Ingestion Foundation; COMPLETED /
  LOCAL_REGISTERED_EVENT_ONLY
- V2-R4: Intraday Anomaly Radar; COMPLETED /
  LOCAL_REGISTERED_ANOMALY_RESEARCH_ONLY
- V2-R5: Realtime Cognitive Shield; COMPLETED /
  LOCAL_REGISTERED_COGNITIVE_SHIELD_ONLY
- V2-R6: Paper Simulation Research; COMPLETED /
  LOCAL_REGISTERED_SCENARIO_RESEARCH_ONLY
- V2-R7: Local Market Session Registry Foundation; COMPLETED /
  REGISTERED_LOCAL_CALENDAR_ONLY
- V2-R8: Local Same-Time Baseline Foundation; COMPLETED /
  REGISTERED_LOCAL_HISTORY_ONLY
- V2-R9: Local Volume-Ratio Research Foundation; COMPLETED /
  REGISTERED_LOCAL_VOLUME_EVIDENCE_ONLY
- V2-R10: Local Turnover-Definition Research Foundation; COMPLETED /
  REGISTERED_LOCAL_TURNOVER_EVIDENCE_ONLY
- V2-R11: Local Factor Registry Foundation; COMPLETED /
  REGISTERED_LOCAL_FACTOR_DEFINITION_ONLY
- V2-R12: Local Technical Indicator Foundation; COMPLETED /
  REGISTERED_LOCAL_TECHNICAL_CALCULATION_ONLY
- V2-R13: Local Momentum Indicator Foundation; COMPLETED /
  REGISTERED_LOCAL_MOMENTUM_CALCULATION_ONLY
- V2-R14: Local Trend Indicator Foundation; COMPLETED /
  REGISTERED_LOCAL_TREND_CALCULATION_ONLY
- V2-R15: Local Volatility Indicator Foundation; COMPLETED /
  REGISTERED_LOCAL_VOLATILITY_CALCULATION_ONLY
- V2-R16: Local Range Channel Indicator Foundation; COMPLETED /
  REGISTERED_LOCAL_CHANNEL_CALCULATION_ONLY
- V2-R17: Local Stochastic Oscillator Foundation; COMPLETED /
  REGISTERED_LOCAL_STOCHASTIC_CALCULATION_ONLY
- V2-R18: Local Directional Trend Strength Foundation; COMPLETED /
  REGISTERED_LOCAL_DIRECTIONAL_STRENGTH_CALCULATION_ONLY
- V2-R19: Local Percentage Price Oscillator Foundation; COMPLETED /
  REGISTERED_LOCAL_PERCENTAGE_OSCILLATOR_CALCULATION_ONLY
- V2-R20: Local Triple Exponential Oscillator Foundation; COMPLETED /
  REGISTERED_LOCAL_TRIPLE_EXPONENTIAL_OSCILLATOR_CALCULATION_ONLY
- V2-R21: Local Robust Normalization Foundation; COMPLETED /
  REGISTERED_LOCAL_ROBUST_NORMALIZATION_ONLY
- V2-R22: Local Robust Normalization Integrity Hardening; COMPLETED /
  REGISTERED_LOCAL_NORMALIZATION_INTEGRITY_ONLY
- V2-R23: Local Institutional Calendar Evidence Foundation;
  COMPLETED / REGISTERED_LOCAL_EVENT_EVIDENCE_ONLY
- V2-R24: Local Multi-Clock Event State Foundation;
  COMPLETED / REGISTERED_LOCAL_CLOCK_STATE_ONLY
- V2-R25: Local Causal Transmission Graph Foundation;
  COMPLETED / REGISTERED_LOCAL_CAUSAL_HYPOTHESIS_ONLY
- V2-R26: Local Consensus Expectation Gap Foundation;
  COMPLETED / REGISTERED_LOCAL_EXPECTATION_EVIDENCE_ONLY
- V2-R27: Local Event Reaction Quality Foundation;
  COMPLETED / REGISTERED_LOCAL_REACTION_EVIDENCE_ONLY
- V2-R28: Local A-Share Earnings Lifecycle Accounting Quality Foundation;
  COMPLETED / REGISTERED_LOCAL_ACCOUNTING_CHALLENGE_ONLY
- V2-R29: Local Index Futures Basis Roll Expiry Foundation;
  COMPLETED / REGISTERED_LOCAL_DERIVATIVES_EVIDENCE_ONLY
- V2-R30: Local Equity Supply Pressure Foundation;
  COMPLETED / REGISTERED_LOCAL_EQUITY_SUPPLY_EVIDENCE_ONLY
- V2-R31: Local FX Transmission Sensitivity Foundation;
  COMPLETED / REGISTERED_LOCAL_FX_TRANSMISSION_EVIDENCE_ONLY
- V2-R32: Local Institutional Crowding Foundation;
  COMPLETED / REGISTERED_LOCAL_INSTITUTIONAL_CROWDING_EVIDENCE_ONLY
- V2-R33: Local Holiday Liquidity State Foundation;
  COMPLETED / REGISTERED_LOCAL_HOLIDAY_LIQUIDITY_EVIDENCE_ONLY
- V2-R34: Local Policy Window Language Evidence Foundation;
  COMPLETED / REGISTERED_LOCAL_POLICY_LANGUAGE_EVIDENCE_ONLY
- V2-R35: Local Evidence Integrity Foundation;
  COMPLETED / REGISTERED_LOCAL_EVIDENCE_INTEGRITY_ONLY
- V2-R36: Local Institutional Factor Lifecycle Foundation;
  COMPLETED / REGISTERED_LOCAL_FACTOR_GOVERNANCE_ONLY
- V2-R37: Local Factor Validation Evidence Foundation;
  COMPLETED / REGISTERED_LOCAL_FACTOR_VALIDATION_EVIDENCE_ONLY
- V2-R38: Local Operator Factor Governance Projection Foundation;
  IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_OPERATOR_GOVERNANCE_PROJECTION_ONLY

V2-R1 prioritizes Factor Registry, forecast targets, State-Sync, and safety
contracts. Later phases cannot skip earlier dependencies. No phase starts
automatically.

## 31. Prohibited Claims

The project must not claim:

- architecture or regulatory completeness
- zero risk or elimination of AI hallucination
- guaranteed limit-up discovery or profit
- existing realtime surveillance or leverage capability
- permanent effectiveness of any indicator or fixed threshold
- perfect leakage prevention through anonymization
- institutional truth from inferred capital flow
- government or institutional endorsement
- enforcement coverage not proven by repository tests

## 32. Current Non-Authorization

This architecture registration does not create:

- a data-source selection or purchase decision
- a network collector or remote service
- a Factor Registry runtime or technical indicator library
- a scoring or candidate-ranking change
- order-book maintenance or realtime anomaly radar
- a virtual account, Paper order, leverage, or execution engine
- live AI invocation, Prompt execution, training, or fallback execution
- a V2-R implementation approval

## 33. Market Session Registry and Exchange Calendar

Every intraday research event must resolve through a versioned Market Session
Registry. Required fields include:

- `market_session_id`, `venue`, `market`, `timezone`, and `trade_date`
- calendar version, rule version, effective time, and source evidence
- local session start and end, holidays, half days, suspensions, and halts
- auction, continuous, break, late-session, close, and post-close boundaries
- instrument-specific exceptions, price-limit state, settlement, and T+1 state
- source event time, receive time, processing time, and clock-quality state

The common research taxonomy is:

`PRE_OPEN -> CALL_AUCTION -> CONTINUOUS_SESSION -> LATE_SESSION -> CLOSE -> POST_CLOSE`

Markets may omit or repeat states. BTC and other continuously traded markets
use versioned analysis windows and regime boundaries rather than pretending to
have an equity auction or official close.

Exchange times are data, not constitutional constants. For A-share research,
an initial `LATE_SESSION` candidate may begin at 14:30 Asia/Shanghai, but the
effective window must come from the registered calendar and may not be
hardcoded across venues or history.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 34. Same-Time-of-Day and Regime Baselines

Intraday comparisons must use information available at the decision time and
must distinguish:

- cumulative value versus interval value
- raw value versus same-minute historical percentile
- instrument baseline versus sector and market baseline
- normal day, event day, high-volatility day, and low-liquidity regime
- opening, continuous, late-session, and closing behavior

Volume ratio, turnover acceleration, spread, depth, cancel intensity, CVD,
VWAP deviation, and alert thresholds must not use one permanent threshold for
all instruments and sessions. Baselines require version, sample count,
lookback, missing policy, outlier policy, and effective time.

Future information, completed-day totals, revised classifications, or a later
session state cannot enter an earlier decision baseline.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 35. A-Share Call-Auction Research Contract

Call-auction research is isolated from continuous trading. Candidate inputs
may include only registered fields actually supplied by an approved source:

- prior close, indicative price, gap, matched amount, and matched volume
- unmatched bid and ask quantity, imbalance direction, and imbalance change
- indicative-price path, stability, cancel velocity, and final convergence
- distance to price limit, listing or special-treatment state, and liquidity
- sector breadth, leader confirmation, index context, and event context

Every auction feature records whether it came from full order events,
aggregated indicative fields, or an inferred proxy. Missing order events may
not be reconstructed and presented as observed truth.

Auction candidates require stability and negative-evidence checks. A large
imbalance that disappears, reverses, lacks sector confirmation, conflicts with
price-limit rules, or depends on stale data is downgraded or blocked.

Auction research may create a review candidate. It may not create a buy,
sell, order, account, position, or execution instruction.

Status: ACCEPTED_ARCHITECTURE / SOURCE FIELDS RESEARCH_REQUIRED /
NOT_IMPLEMENTED

## 36. Late-Session and Closing Research Contract

Late-session research evaluates whether a move is strengthening, exhausting,
or losing confirmation. Candidate features include:

- return and acceleration from the registered late-session boundary
- volume and notional concentration relative to the same time of day
- VWAP location, slope, reclaim, rejection, and closing-location value
- order-book resilience, replenishment, spread, and realized trade support
- sector synchronization, breadth, leader or follower behavior, and rotation
- distance to price limits, failed-limit state, and closing-auction behavior
- next-session target definition, maturity, invalidation, and gap-risk context

The platform must keep `LATE_SESSION_STRENGTH`, `LATE_SESSION_EXHAUSTION`,
`CLOSE_CONFIRMATION_MISSING`, and `DATA_INSUFFICIENT` distinguishable. It must
not label all late buying as informed capital or imply next-day profit.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 37. Entrusted Order, Volume Ratio, Turnover, and Flow Semantics

Common market labels require exact registered definitions.

An entrusted-order ratio candidate is:

`(registered_bid_quantity - registered_ask_quantity) /`
`(registered_bid_quantity + registered_ask_quantity)`

The record must name included book levels, snapshot time, denominator-zero
behavior, unit, source coverage, and whether cancellations were observable.
It is a displayed-liquidity proxy, not verified trading intent.

A volume-ratio candidate compares current volume pace with a registered
same-time historical baseline. It must state cumulative or interval basis,
lookback, comparable sessions, corporate-action treatment, and minimum sample.

Turnover must state the numerator and point-in-time denominator, including
whether free float, total shares, or vendor-defined tradable shares are used.
It cannot silently mix definitions across instruments or dates.

Observable capital-flow research separates aggressive-trade imbalance, CVD,
large-trade buckets, ETF or eligible public flow, financing change, and
vendor-inferred labels. No proxy may be renamed institutional, smart, main, or
government capital without evidence that supports that identity.

Status: ACCEPTED_ARCHITECTURE / INDIVIDUAL DEFINITIONS RESEARCH_REQUIRED

## 38. Sector, Theme, and Cross-Market Transmission Graph

Sector context requires a point-in-time taxonomy with versioned membership.
Candidate structures include:

- sector breadth, median return, dispersion, turnover share, and flow proxy
- leader, follower, laggard, failed-leader, and diffusion state
- index, ETF, futures, commodity, foreign-market, and macro-event context
- industry-chain upstream and downstream relationships
- theme overlap, crowding, concentration, and membership uncertainty
- lead-lag hypothesis, horizon, decay, evidence, and invalidation

The graph preserves multiple taxonomies rather than forcing one sector label.
Sector confirmation may strengthen confidence, but cannot erase instrument
risk, stale data, or contradictory evidence. Correlation and lead-lag do not
establish causation.

Status: ACCEPTED_ARCHITECTURE / TAXONOMY AND LEAD-LAG VALIDATION
RESEARCH_REQUIRED

## 39. Controlled Research Candidate Lifecycle

Market observations use this research-only lifecycle:

`OBSERVED -> QUALIFIED -> WATCHLISTED -> OPERATOR_REVIEW`

Operator review may produce:

- `ACCEPTED_FOR_PAPER_OBSERVATION`
- `REJECTED`
- `EXPIRED`
- `REVOKED`
- `MORE_EVIDENCE_REQUIRED`

Every candidate carries target, horizon, feature versions, state hash,
supporting evidence, negative evidence, uncertainty, invalidation, expiry,
cooldown, duplicate group, and review history. A later outcome appends an
immutable evaluation record and never rewrites the original candidate.

Candidate actions are research actions only: add to a watchlist, increase
observation priority, request evidence, open replay, compare scenarios, record
an Operator decision, or revoke a stale candidate.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 40. Read-Only Operator Research Control Plane

The future browser workspace may expose versioned controls for:

- selecting market, session, universe, horizon, and research module
- enabling or disabling approved observation modules
- setting alert sensitivity only within policy-approved bounds
- managing watchlists, alert budgets, cooldowns, and review queues
- opening evidence, formulas, baselines, replay, and AI pro or con explanation
- accepting, rejecting, requesting evidence, or revoking a research candidate

The UI must show data freshness, source class, factor version, blocked reason,
uncertainty, and whether a value is observed or inferred. Every control change
is an Operator-authored registered artifact.

The control plane cannot change deterministic formulas, bypass hard gates,
activate an unqualified factor, invoke automatic learning, or expose an order,
account, balance, position, wallet, broker, or exchange action.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 41. Controlled Offline Adaptation and Learning Boundary

Adaptive research is an offline governed loop:

`immutable observations -> matured outcomes -> evaluation -> candidate change`
`-> Challenger -> Operator review -> separately approved activation`

Candidate changes may include threshold, baseline, factor, model, taxonomy,
or alert-budget proposals. Each proposal requires training window, validation
window, final test, leakage controls, metric deltas, segment analysis, failure
modes, rollback, and reproducibility evidence.

No observation, AI response, Operator click, or recent win may automatically
rewrite production formulas, weights, baselines, Champion status, or policy.
AI may propose and critique a change; deterministic evaluation and Registered
Evidence remain authoritative.

Status: ACCEPTED_ARCHITECTURE / AUTOMATIC LEARNING OUTSIDE CURRENT
AUTHORIZATION

## 42. Session-Aware Evaluation and Failure Law

Evaluation must be segmented by market, session, horizon, liquidity, regime,
sector, and candidate type. Minimum measures include:

- precision, recall, precision at K, false-alert rate, and alert volume
- calibrated probability, Brier score, abstention quality, and coverage
- median and tail lead time before the defined target event
- maximum favorable and adverse movement under registered cost assumptions
- stability across time, instruments, regimes, and data vendors
- Operator review load, duplicate rate, expiry rate, and evidence completeness

Auction and late-session replay must reproduce historical calendars, auction
rules, price limits, halts, T+1, corporate actions, point-in-time sector
membership, source latency, and field availability. If vendor history cannot
reproduce the information set, that test is blocked rather than approximated
and overclaimed.

Potential spoofing, manipulation, institutional identity, or informed trading
must remain uncertainty labels unless supported by legally and technically
adequate evidence. The platform is a research system, not a surveillance or
enforcement authority.

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED

## 43. Control and Change Rule

Every future change requires repository-truth precheck, Readiness Gate,
explicit Operator approval, dedicated Sidecar, tests, full validation,
generated-output restoration, authority synchronization, and clean Git state.

P1-P47 remain frozen. No P48 is created. Deterministic Engine and Registered
Evidence remain authoritative. AI remains advisory. Operator review remains
mandatory. No tag, release, or deployment is authorized.

## 44. Institutional Calendar and Causal Market Intelligence Architecture

Architecture ID:

- `FCF-V2-INSTITUTIONAL-CALENDAR-CAUSAL-MARKET-INTELLIGENCE`

Short design name:

- `Five-Clock Three-Chain Architecture`

Status: ACCEPTED_ARCHITECTURE / NOT_IMPLEMENTED / PHASE_NONE

This extension organizes macro, institutional, capital, industry, and company
evidence without converting calendar effects, correlations, or narratives into
automatic decisions. It supports A-share and BTC research through separate
market adapters, point-in-time evidence, deterministic calculations, causal
challenge, and mandatory Operator review.

## 45. Five-Clock Regime Context

The platform preserves five concurrent clocks rather than forcing one global
market state:

- `Macro Clock`: inflation, growth, rates, credit, liquidity, fiscal policy,
  monetary policy, commodities, and global risk conditions
- `Institutional Clock`: exchange rules, settlement, index-futures expiry,
  disclosure windows, Two Sessions, July and December policy windows, holidays,
  lock-up expiry, and regulatory changes
- `Capital Clock`: market turnover, breadth, ETF and fund flows, financing,
  foreign-ownership disclosures, futures basis, open interest, and crowding
- `Industry Clock`: policy exposure, capacity, inventory, pricing, orders,
  upstream and downstream transmission, and sector diffusion
- `Company Clock`: earnings guidance, quick reports, formal reports, corporate
  actions, unlocks, reductions, pledges, cash flow, and accounting quality

Each clock carries event time, publication time, ingest time, first legally
available time, first tradable time, source, digest, freshness, revision state,
market, horizon, confidence, and missing-state semantics. Conflicting clocks
remain visible.

## 46. Three Causal Transmission Chains

Three versioned point-in-time graphs explain how evidence may reach an
instrument:

- `Policy Transmission Chain`: official decision -> macro variable -> industry
  mechanism -> company exposure -> observable market response
- `Industry Supply Chain`: upstream input -> capacity and inventory -> pricing
  -> margin and orders -> company earnings exposure
- `Capital Transmission Chain`: funding and rate condition -> asset allocation
  -> vehicle or venue flow -> sector breadth -> instrument liquidity

Every edge requires source, direction hypothesis, horizon, lag, decay,
alternative explanations, invalidation, and evidence quality. A graph edge is a
research hypothesis, not proof of causation. The system preserves negative and
contradictory evidence and does not count correlated nodes as independent
confirmation.

## 47. Official Event Calendar and Point-in-Time Registry

The registry covers scheduled and unscheduled institutional events, including:

- official macro releases, central-bank decisions, major policy meetings, and
  exchange-rule changes
- A-share Two Sessions, July policy review, December policy review, and other
  officially scheduled policy windows
- earnings previews, guidance, quick reports, formal reports, and revisions
- index-futures expiry, contract roll, index rebalance, lock-up expiry,
  reductions, dividends, placements, convertible actions, and holidays
- BTC protocol, market-structure, macro, and cross-market events when an
  approved local registered source exists

Dates are resolved from registered official or licensed artifacts. Recurring
calendar rules may seed a candidate event but cannot replace a confirmed
schedule. Revised releases preserve the original value, revised value, and
availability timeline.

## 48. Multi-Clock Regime Orchestrator and Event State Stack

Overlapping events form an immutable stack, not one destructive state. Example
states include `PRE_EVENT`, `RELEASED_NOT_TRADABLE`, `FIRST_TRADABLE_REACTION`,
`POST_EVENT_DIGESTION`, `EXPIRY_WINDOW`, `HOLIDAY_LIQUIDITY`,
`EARNINGS_REBUILD`, and `STALE_OR_CONFLICTED`.

The deterministic conflict resolver produces supporting, opposing, neutral,
missing, stale, and blocked evidence groups by market and horizon. Hard data,
rights, security, and execution gates remain non-overridable. AI may summarize
the stack and propose alternative explanations but cannot select a state,
remove a conflict, or change a deterministic effect.

## 49. Expectation Gap and Event Reaction Quality

The `Expectation Gap Engine` separates:

- actual value versus registered consensus
- actual value versus prior release and prior revisions
- official language versus the previous official language
- company result versus point-in-time guidance and analyst range
- observed price response versus a registered price-implied baseline

The `Event Reaction Quality Engine` measures first-tradable gap, intraday path,
close location, continuation or reversal, volume, turnover, spread, depth,
breadth, futures basis, volatility, and cross-market confirmation. Surprise and
reaction are separate evidence: favorable news with weak price response and
unfavorable news with resilient response must remain observable.

Consensus coverage, dispersion, age, provider, survivorship, and revision
history are mandatory. Missing consensus cannot be replaced by AI-generated
numbers.

## 50. Earnings Lifecycle and Accounting Quality

The earnings state machine preserves market-specific stages:

`EXPECTATION -> PREANNOUNCEMENT -> QUICK_REPORT -> FORMAL_REPORT`
`-> FIRST_TRADABLE_REACTION -> REASSESSMENT -> MATURED_OUTCOME`

Deterministic research may compare revenue, profit, adjusted profit, cash flow,
margin, working capital, debt, guidance, consensus dispersion, and revisions.
Accounting-quality checks include non-recurring gains, government grants,
asset sales, impairment, related-party exposure, receivables, inventory, cash
conversion, auditor opinion, and restatement history when registered evidence
exists.

AI may extract tables, compare statements, identify assumptions, and write a
pro and con explanation. It cannot invent consensus, diagnose fraud, replace an
auditor, or alter the deterministic score.

## 51. Index-Futures Expiry and Derivatives Context

Research may cover IF, IH, IC, IM, and other separately registered contracts:

- spot-futures basis and annualized basis by comparable timestamp
- basis percentile by contract, regime, horizon, and time to expiry
- open interest, volume, roll, calendar spread, and contract migration
- expiry-window liquidity, index and constituent response, and hedge proxies
- settlement rule, holiday shift, contract multiplier, and data revisions

No fixed third-Friday assumption may override a versioned exchange calendar.
Deep discount does not prove a bottom, open interest does not reveal intent,
and member ranking does not prove directional speculation. Slippage or alert
changes require registered event-study evidence and deterministic policy.

## 52. Equity Supply and Forced-Sale Pressure

The `Equity Supply and Forced-Sale Pressure System` separates legal
availability from actual selling. It may register:

- lock-up type, holder class, unlock date, legally sellable amount, free-float
  ratio, market value, and days of average traded value required for absorption
- IPO, placement, employee-plan, convertible, secondary-offering, and planned
  reduction supply
- pledge ratio, margin or debt pressure, judicial auction, disposal notice,
  historical reductions, and actual post-event selling evidence
- holder cost or profit proxy, liquidity, ownership concentration, and demand
  absorption

Unlock does not imply sale. A time-decay factor must be piecewise before and
after the event and cannot explode after the event because of a negative day
count. Any supply-pressure score requires point-in-time inputs, sensitivity
analysis, capacity testing, and explicit missing states.

## 53. Policy Windows and Local Institutional Cycles

Two Sessions, July, December, reporting seasons, quarter ends, and other local
institutional windows are registered event regimes, not deterministic bullish
or bearish labels. Research preserves pre-event expectation, official release,
first tradable response, post-event diffusion, and invalidation.

AI may compare official documents, extract changed language, identify named
industries, and challenge narrative consistency. Deterministic code maps only
registered concepts to point-in-time taxonomies and measures breadth, flow,
reaction, and persistence. No keyword may automatically increase a factor
weight, and no fixed percentage adjustment is accepted without event-study,
robustness, multiple-testing, and Operator approval evidence.

## 54. Rates, FX, and Cross-Market Transmission

The cross-market system may include Federal Reserve and FOMC decisions, CPI,
nonfarm payrolls, other registered central-bank decisions, sovereign yields,
yield curves, DXY, USD/CNY, USD/CNH, volatility, commodities, foreign markets,
approved ownership disclosures, and company operating FX exposure.

Simple return-to-FX covariance is insufficient for an official factor. A
candidate FX sensitivity model must define market and sector controls, rate and
Dollar controls, volatility regime, horizon, rolling window, structural breaks,
company revenue and cost currency exposure, and missing data. Foreign holding
data must display its actual publication latency; delayed disclosure cannot be
presented as realtime individual-stock flow or current investor intent.

## 55. Institutional Crowding, Rebalance, and Holiday Liquidity

Crowding research separates:

- normalized concentration among reporting funds
- total disclosed institutional ownership
- ETF and index-rebalance mechanical demand hypotheses
- ownership change, disclosure age, turnover capacity, and estimated exit days
- sector and style concentration, breadth, correlation, and liquidity stress

Fund holdings and letters are delayed registered evidence. They cannot prove a
current manager action, manipulation, or a quarter-end motive.

Quarter-end research distinguishes March, June, September, and December and
retains the actual disclosure and rebalance calendar. June and December
bank-liquidity or assessment pressure remains an observable research hypothesis
rather than a presumed market direction.

The holiday and settlement liquidity state machine uses holiday length,
overseas-open days, settlement mismatch, expected event risk, spread, depth,
volume, turnover, basis, and historical regime-conditioned distributions. A
fixed last-three-days rule or fixed 30 percent threshold remains a research
hypothesis, not Hard Policy.

The holiday taxonomy includes Spring Festival, May Day, National Day, and
other market-specific closures without assuming that all holidays have the
same liquidity or return effect.

## 56. Institutional Factor Lifecycle and Validation Order

Institutional factors follow this lifecycle:

`RESEARCH_PROPOSAL -> CONTRACT_DEFINED -> DATA_AVAILABLE`
`-> POINT_IN_TIME_VALIDATED -> BACKTESTED -> ROBUSTNESS_REVIEWED`
`-> OPERATOR_APPROVED -> REGISTERED_PAPER_FACTOR`

Failures, deferrals, and supersessions remain immutable. No factor receives a
direction, weight, score, rank, or alert effect before leakage, revision,
survivorship, availability-time, transaction-cost, capacity, subgroup,
multiple-testing, sensitivity, ablation, and out-of-sample checks pass.

Recommended research order is calendar and availability semantics, event stack
and state conflict, expectation and reaction measurement, earnings lifecycle,
equity supply, derivatives context, rates and FX, crowding and holiday
liquidity, transmission graphs, and only then registered factor candidates.

Status: ACCEPTED_ARCHITECTURE / RESEARCH_REQUIRED / NOT_IMPLEMENTED

## 57. Named Institutional Factor Research Candidates

The original proposals are preserved as named research candidates so their
intent is not lost. None is a registered or active factor:

- `EARNINGS_SURPRISE`: actual result relative to point-in-time consensus and
  estimate dispersion, with coverage, age, revision, and missing-consensus
  controls
- `EVENT_REACTION_QUALITY`: first-tradable gap, path, close, persistence,
  breadth, volume, spread, depth, volatility, and cross-market confirmation
- `EXPIRY_BASIS_ROLL_STRESS`: comparable-time basis, basis percentile, open
  interest, volume, calendar spread, roll migration, and time to expiry
- `EQUITY_SUPPLY_PRESSURE`: legally sellable supply, free float, unlock value,
  average traded value absorption days, reduction evidence, pledge or debt
  pressure, holder cost, and demand absorption
- `FX_TRANSMISSION_SENSITIVITY`: market-, sector-, rate-, Dollar-, volatility-,
  horizon-, regime-, and operating-exposure-controlled FX sensitivity
- `INSTITUTIONAL_CROWDING`: normalized concentration among reporting funds,
  total disclosed ownership, disclosure age, ownership change, exit days,
  liquidity, breadth, and correlation stress
- `WINDOW_DRESSING_PRESSURE`: observable quarter-end ownership, rebalance,
  price, volume, and liquidity patterns without a manager-intent claim
- `HOLIDAY_LIQUIDITY_STRESS`: holiday length, overseas-open days, settlement
  mismatch, event risk, spread, depth, volume, turnover, basis, and historical
  regime distributions
- `POLICY_NOVELTY_ALIGNMENT`: registered official-language change mapped to a
  point-in-time industry taxonomy and verified by breadth, flow, reaction, and
  persistence
- `CAPITAL_TRANSMISSION_PRESSURE`: registered funding, rate, vehicle-flow,
  breadth, and instrument-liquidity evidence with correlated-evidence controls

The source labels `ESF`, `HI`, `beta_FX`, `WDF`, and earnings surprise are
retained as proposal aliases only. An official contract may replace their
original simplified formulas when point-in-time, normalization, multivariate,
capacity, and robustness requirements are satisfied. The aliases cannot be
presented as implemented factors.

## 58. Module Ownership and Research Order

Future work is grouped to prevent unrelated concepts from being mixed:

1. `Calendar and Evidence Foundation`: official schedules, publication and
   tradable time, source rights, digests, revisions, and freshness; Gaps 071 and
   084
2. `Clock and Event State`: five clocks, market adapters, overlapping state
   stack, conflict resolution, expiry, holiday, and disclosure states; Gaps 072
   and 073
3. `Causal Transmission`: Policy, Industry Supply, and Capital Transmission
   graphs, edge evidence, lag, decay, alternatives, and invalidation; Gap 074
4. `Expectation and Corporate Events`: consensus, expectation gaps, reaction
   quality, earnings stages, and accounting-quality challenge; Gaps 075-077
5. `Derivatives and Equity Supply`: futures basis, roll, expiry, lock-up,
   issuance, reduction, pledge, forced-sale, and absorption research; Gaps
   078-079
6. `Macro and Institutional Liquidity`: rates, FX, policy windows, crowding,
   rebalance, quarter-end, holiday, and settlement liquidity; Gaps 080-083
7. `Factor Governance and Validation`: factor lifecycle, failure history,
   leakage, multiple testing, sensitivity, ablation, capacity, out-of-sample
   evaluation, and Operator approval; Gaps 085-086

Dependencies flow from Module 1 through Module 7. A later module cannot invent
missing calendar, rights, availability, evidence, or state semantics. This
ordering is architecture and backlog organization only; it does not select or
approve an implementation phase.
