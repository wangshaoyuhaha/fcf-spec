# FCF V2 Factor, Realtime, and Cognitive ADR Register

Register status: ACCEPTED_ARCHITECTURE

Implementation status: NOT_IMPLEMENTED

These decisions define future architecture. They do not prove that the
corresponding runtime exists.

## FCF-V2-ADR-001 Domain-Scoped Authority Model

Status: ACCEPTED_ARCHITECTURE

Decision: Use separate authority domains for Hard Policy, Deterministic
Engine, Registered Evidence, Operator, and AI. Hard circuit breakers cannot be
overridden. The Operator owns research adoption but not deterministic values.
AI remains advisory.

Consequence: Interfaces must expose authority and rejection reason. No global
rank may imply that AI or Operator can rewrite evidence or calculations.

Not authorized: runtime implementation or authority transition.

## FCF-V2-ADR-002 Deterministic Factor Registry

Status: ACCEPTED_ARCHITECTURE

Decision: Every official factor requires identity, hypothesis, formula,
parameters, inputs, horizon, processing, validation, risk, evidence, version,
owner, dependency, lifecycle, and deterministic test-vector registration.

Consequence: Temporary formulas and AI proposals cannot enter official scores.

Not authorized: Factor Registry code or factor activation.

## FCF-V2-ADR-003 State-Sync Lock and Snapshot Anchoring

Status: ACCEPTED_ARCHITECTURE

Decision: Detection, baseline, factors, evidence, and AI explanation must use
the same immutable snapshot and state hash. Expired state creates a new event
and preserves the old audit record.

Consequence: Every realtime research event needs event-time, source-time,
ingest-time, sequence, snapshot, hash, latency, factor version, and TTL.

Not authorized: realtime ingestion or snapshot runtime.

## FCF-V2-ADR-004 Historical and Realtime Closed Loop

Status: ACCEPTED_ARCHITECTURE

Decision: Historical research defines registered baselines and evaluation;
realtime observation uses the same versioned contracts and later feeds
immutable Outcome labels. Realtime results never rewrite history.

Consequence: Backtest, replay, forward observation, and learning share lineage
but retain separate authority and time windows.

Not authorized: live data or automatic learning.

## FCF-V2-ADR-005 Two-Level Market Scanning

Status: ACCEPTED_ARCHITECTURE

Decision: Use a low-cost first-level universe scan and bounded second-level
microstructure monitoring only for qualified candidates.

Consequence: Cost, alert volume, and Operator capacity remain bounded. Dynamic
thresholds are versioned and regime-aware.

Not authorized: market scanner or anomaly radar implementation.

## FCF-V2-ADR-006 Realtime Service and Resource Isolation

Status: ACCEPTED_ARCHITECTURE

Decision: Realtime and governance workloads use separate processes,
lifecycles, queues, budgets, and failure domains with structured event
communication.

Consequence: AI or governance failure cannot stop deterministic realtime
processing. Physical-machine separation is optional, not constitutional.

Not authorized: daemon, queue, remote compute, or service deployment.

## FCF-V2-ADR-007 AI Asynchronous Timeout Boundary

Status: ACCEPTED_ARCHITECTURE

Decision: Deterministic processing never waits for AI. Timeouts are
task-specific, configurable, policy-bounded, and audited. Fallback must be
registered and validated; otherwise explanation is skipped.

Consequence: `COGNITIVE_TIMEOUT` and visible degradation replace blocking.
No fixed eight-second constitutional timeout exists.

Not authorized: model invocation, routing, retry, or fallback execution.

## FCF-V2-ADR-008 Local Sovereign Operating Modes

Status: ACCEPTED_ARCHITECTURE

Decision: Offline Sovereign Mode is the current compatible direction. Live
Read-Only Sovereign and Secure Remote Compute modes remain separately gated
research candidates. Real Execution Mode is outside this repository.

Consequence: Current local-only and loopback-only restrictions remain binding.
Any external mode requires privacy, license, credential, cost, and security
approval.

Not authorized: external connection, credential use, or cloud deployment.

## FCF-V2-ADR-009 Point-in-Time Backtest Law

Status: ACCEPTED_ARCHITECTURE

Decision: A backtest may use data only when `available_at <= as_of_time` and
must preserve universe history, delisting, corporate actions, market rules,
cost, capacity, revision, and timestamp order.

Consequence: Train, validation, final test, walk-forward, purge, embargo,
regime, stress, and forward Paper evidence remain distinct. Anonymization only
reduces and does not eliminate leakage risk.

Not authorized: new backtest runtime beyond existing approved components.

## FCF-V2-ADR-010 Operator Cannot Override Hard Circuit Breakers

Status: ACCEPTED_ARCHITECTURE

Decision: The Operator cannot override data, license, security, evidence,
sequence, checksum, or execution-boundary circuit breakers.

Consequence: UI and audit records must show the blocked reason and recovery
conditions. Operator review cannot convert `BLOCKED` to a usable input.

Not authorized: new UI control or backend action.

## FCF-V2-ADR-011 Paper Leverage Simulation Boundary

Status: ACCEPTED_ARCHITECTURE

Decision: Future BTC leverage research, if separately approved, is a
deterministic registered simulation artifact covering fees, funding, slippage,
latency, maintenance margin, mark-price liquidation, and adverse conditions.

Consequence: It cannot contain an exchange connection, virtual-account
dispatcher, Paper order runtime, credential, or real-money path.

Not authorized: leverage engine or Paper order implementation.

## FCF-V2-ADR-012 No Real Execution in FCF Repository

Status: ACCEPTED_ARCHITECTURE

Decision: FCF ends at research, evidence, Paper portfolio or simulation
artifacts, advisory explanation, and Operator review. Real execution is not an
FCF repository mode.

Consequence: Any future execution research requires a separate repository,
permission domain, credentials, security audit, compliance review, deployment
boundary, and explicit Operator approval.

Not authorized: broker, exchange, order, account, balance, position, wallet,
withdrawal, transfer, tag, release, or deployment capability.

## FCF-V2-ADR-013 Versioned Market Session Registry

Status: ACCEPTED_ARCHITECTURE

Decision: Every intraday event resolves through a versioned exchange calendar
and Market Session Registry. Venue times, holidays, halts, auctions, breaks,
late-session boundaries, and instrument exceptions are governed data.

Consequence: A-share and continuously traded markets share a taxonomy without
sharing hardcoded clocks or false session equivalence.

Not authorized: calendar service, realtime clock, or market connection.

## FCF-V2-ADR-014 Auction and Continuous Trading Isolation

Status: ACCEPTED_ARCHITECTURE

Decision: Call-auction features, baselines, targets, and evaluation remain
separate from continuous-session features. Only source-observed auction fields
may be used; unavailable order events cannot be reconstructed as facts.

Consequence: Auction imbalance, cancellation, stability, and convergence are
interpreted under registered venue rules and visible source limitations.

Not authorized: auction data purchase, ingestion, or candidate runtime.

## FCF-V2-ADR-015 Time-of-Day and Regime-Relative Normalization

Status: ACCEPTED_ARCHITECTURE

Decision: Intraday volume, turnover, spread, depth, flow, and anomaly features
use point-in-time same-session baselines and regime-conditioned thresholds.

Consequence: One permanent threshold cannot govern opening, midday,
late-session, A-share, BTC, liquid, and illiquid observations.

Not authorized: new baseline runtime or factor activation.

## FCF-V2-ADR-016 Observable Proxy Semantics

Status: ACCEPTED_ARCHITECTURE

Decision: Entrusted-order ratio, aggressive flow, CVD, large-trade buckets,
depth, and vendor flow labels remain precisely defined observable or inferred
proxies. They do not establish intent or participant identity.

Consequence: The product must show formula, book levels, field coverage,
source class, confidence, and limitations and must not claim institutional or
manipulative activity without adequate evidence.

Not authorized: surveillance conclusion or capital-owner attribution.

## FCF-V2-ADR-017 Point-in-Time Sector Transmission Graph

Status: ACCEPTED_ARCHITECTURE

Decision: Sector, theme, industry-chain, index, ETF, futures, cross-asset, and
macro context use versioned memberships and registered lead-lag hypotheses.

Consequence: Multiple taxonomies and contradictory context are preserved.
Sector confirmation can adjust research confidence but cannot override a hard
gate or prove causation.

Not authorized: taxonomy vendor integration or cross-market runtime.

## FCF-V2-ADR-018 Research Candidate and UI Action Boundary

Status: ACCEPTED_ARCHITECTURE

Decision: Market detections create research candidates with evidence,
uncertainty, invalidation, expiry, cooldown, and Operator review. UI actions
are limited to watchlist, priority, evidence, replay, review, and revocation.

Consequence: Candidate state cannot be confused with a recommendation, order,
position, or execution action. Every Operator change is audited.

Not authorized: trading control, account control, or automatic acceptance.

## FCF-V2-ADR-019 Controlled Offline Adaptation

Status: ACCEPTED_ARCHITECTURE

Decision: Learning may produce offline Challenger proposals from immutable
observations and matured outcomes. Deterministic evaluation, Registered
Evidence, and explicit Operator review precede any separately approved change.

Consequence: No AI response, recent outcome, or Operator click automatically
changes formulas, weights, baselines, policy, or Champion status.

Not authorized: automatic learning, promotion, activation, or self-modifying
runtime.

## FCF-V2-ADR-020 Market-Specific Adapters and Horizon Isolation

Status: ACCEPTED_ARCHITECTURE

Decision: A-share auction and late-session research, BTC continuous-session
research, and future market adapters share contracts but keep market rules,
targets, baselines, costs, and scores isolated.

Consequence: The platform can become multi-market without creating one false
universal score or launching multiple realtime MVP markets together.

Not authorized: additional market adapter or realtime MVP implementation.

## FCF-V2-ADR-021 Five Concurrent Clocks and Overlapping Event States

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve Macro, Institutional, Capital, Industry, and Company clocks
as concurrent point-in-time contexts. Overlapping events form an immutable
state stack and are resolved by market and horizon without deleting conflict.

Consequence: One global calendar regime cannot overwrite another clock, hard
gate, negative evidence, or missing state.

Not authorized: regime runtime, automatic state selection, or factor effect.

## FCF-V2-ADR-022 Official Calendar and Availability-Time Semantics

Status: ACCEPTED_ARCHITECTURE

Decision: Scheduled events use registered official or licensed artifacts and
carry event, publication, ingest, first-available, and first-tradable times.
Recurring rules seed candidates but do not override confirmed schedules.

Consequence: Revisions, holiday shifts, venue rules, and disclosure latency are
replayable without look-ahead leakage.

Not authorized: network calendar service or live data source.

## FCF-V2-ADR-023 Three Versioned Causal Transmission Chains

Status: ACCEPTED_ARCHITECTURE

Decision: Use Policy Transmission, Industry Supply, and Capital Transmission
graphs with point-in-time membership, lag, decay, alternative explanations,
invalidation, and evidence quality.

Candidate linkage: `POLICY_NOVELTY_ALIGNMENT` and
`CAPITAL_TRANSMISSION_PRESSURE` remain research proposals under this decision.

Consequence: Correlation, keywords, and graph proximity cannot prove causation
or receive duplicate confidence as independent evidence.

Not authorized: automatic causal conclusion or weight change.

## FCF-V2-ADR-024 Separate Expectation Gap from Reaction Quality

Status: ACCEPTED_ARCHITECTURE

Decision: Measure actual-versus-consensus or prior expectation separately from
the first-tradable price, liquidity, breadth, futures, and persistence response.

Candidate linkage: `EARNINGS_SURPRISE` and `EVENT_REACTION_QUALITY` remain
separate research proposals.

Consequence: Favorable surprise with weak response and unfavorable surprise
with resilient response remain explicit, auditable evidence states.

Not authorized: AI-generated consensus, recommendation, or automatic score.

## FCF-V2-ADR-025 Earnings Lifecycle and Accounting-Quality Challenge

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve preannouncement, quick-report, formal-report,
first-tradable-reaction, reassessment, and matured-outcome stages. Registered
accounting-quality evidence challenges headline profit.

Consequence: Non-recurring gains, cash conversion, impairment, auditor opinion,
and revisions are not collapsed into one earnings number.

Not authorized: fraud diagnosis, auditor replacement, or formula override.

## FCF-V2-ADR-026 Equity Supply Is Not Equivalent to Selling

Status: ACCEPTED_ARCHITECTURE

Decision: Model unlock and issuance availability separately from reduction
notices, actual selling, pledge or debt pressure, judicial disposal, liquidity,
holder cost, and demand absorption.

Candidate linkage: `EQUITY_SUPPLY_PRESSURE` replaces raw unlock-only scoring as
the governed research proposal; `ESF` remains a non-registered source alias.

Consequence: Unlock ratios alone cannot trigger a bearish conclusion. Time
decay is piecewise around the event and remains stable after the event.

Not authorized: holder-intent claim or automatic technical-score discount.

## FCF-V2-ADR-027 Derivatives Evidence Requires Contract and Calendar Context

Status: ACCEPTED_ARCHITECTURE

Decision: Futures basis, open interest, roll, calendar spread, and expiry effects
use comparable timestamps, contract metadata, versioned venue calendars, and
regime-conditioned baselines.

Candidate linkage: `EXPIRY_BASIS_ROLL_STRESS` remains a research proposal.

Consequence: Discount does not prove a bottom, open interest does not reveal
intent, and a recurring expiry rule cannot replace the official calendar.

Not authorized: futures connection, order path, or automatic risk adjustment.

## FCF-V2-ADR-028 Rates, FX, and Foreign-Flow Latency Discipline

Status: ACCEPTED_ARCHITECTURE

Decision: FX sensitivity is a multivariate, horizon-specific, regime-aware
research model with market, sector, rates, Dollar, volatility, and company
operating-exposure controls. Foreign holdings retain publication latency.

Candidate linkage: `FX_TRANSMISSION_SENSITIVITY` replaces the simplified
`beta_FX` proposal alias.

Consequence: Simple covariance and delayed ownership cannot be labeled a causal
FX factor, realtime stock flow, or current investor intent.

Not authorized: live foreign-flow feed or automatic cross-market weight.

## FCF-V2-ADR-029 Crowding and Holiday Liquidity Use Dynamic Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Separate normalized fund concentration, total ownership, change,
disclosure age, exit days, rebalance hypotheses, and liquidity stress. Holiday
state uses registered calendar length and regime-conditioned market liquidity.

Candidate linkage: `INSTITUTIONAL_CROWDING`, `WINDOW_DRESSING_PRESSURE`, and
`HOLIDAY_LIQUIDITY_STRESS` remain distinct research proposals. `HI` and `WDF`
remain non-registered source aliases.

Consequence: Delayed holdings do not prove current manager behavior. Fixed
three-day, 30 percent, or percentile rules remain unvalidated hypotheses.

Not authorized: manipulation claim or automatic Hard Policy threshold.

## FCF-V2-ADR-030 Governed Institutional Factor Lifecycle

Status: ACCEPTED_ARCHITECTURE

Decision: An institutional factor advances from proposal through contract,
data availability, point-in-time validation, backtest, robustness review,
Operator approval, and registered Paper-factor status.

Consequence: No calendar, policy, supply, earnings, derivatives, FX, crowding,
or liquidity idea can acquire a direction, weight, score, or rank early. Failed
and superseded candidates remain recorded.

Not authorized: automatic activation, promotion, learning, or self-modification.

## FCF-V2-ADR-031 Canonical Typed Data and Provider Isolation

Status: ACCEPTED_ARCHITECTURE

Decision: Provider SDK, DataFrame, and vendor-specific objects terminate at an
adapter boundary. Canonical core observations are immutable typed records with
exact values, units, clocks, versions, quality state, and lineage digests.

Consequence: Provider replacement cannot silently change factor or replay
semantics, and a vendor SDK cannot become calculation or evidence authority.

Rejected shortcut: make Pandas DataFrame or one provider schema the core data
contract.

Not authorized: provider adapter implementation, SDK installation, network
access, credentials, or realtime activation.

## FCF-V2-ADR-032 Point-in-Time Raw, Adjustment, and Revision Lineage

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve raw observations, availability and first-tradable clocks,
revision chains, corporate-action events, adjustment-factor versions, trading
status, transformation lineage, and rights metadata before derived research.
Explicit trading status is authoritative; zero-volume or equal-price patterns
are fallback inferences only.

Consequence: Historical replay can reproduce what was knowable at T without
today's adjustment factors, later filings, or silent fill policy leaking into
the past. Material cross-source conflicts fail closed into quarantine.

Rejected shortcut: treat current forward-adjusted series, `raw * factor`, or
`volume == 0 and high == low` as sufficient canonical truth.

Not authorized: historical download, local trial-data retention, factor
activation, or gap closure.

## FCF-V2-ADR-033 Rights and Evidence Govern Source Cost and Routing

Status: ACCEPTED_ARCHITECTURE

Decision: Every source has an explicit `PRIMARY`, `VERIFICATION`,
`DEGRADED_FALLBACK`, or `RESEARCH_ONLY` role governed by rights, integrity,
coverage, latency, operational reliability, and incremental after-cost value.
Trial access does not imply permanent retention or commercial rights.

Consequence: Free data is not accepted merely because it is free, and paid data
is not purchased merely because it is convenient. RQData, MiniQMT market data,
Tushare, AkShare, and BaoStock remain unselected candidates. A-share and BTC
retain separate source semantics. MiniQMT market data and trading surfaces must
remain process-isolated, with trading surfaces prohibited in this repository.

Rejected shortcut: zero-cost absolutism, trial-period bulk harvesting without
rights, silent provider fallback, one mixed A-share/BTC adapter, or co-locating
market data and trading APIs.

Not authorized: procurement, renewal, provider selection, external activation,
broker or exchange integration, account access, order, or execution.

## FCF-V2-ADR-034 Separate BTC Signal, Contract, and Leverage Accounting

Status: ACCEPTED_ARCHITECTURE

Decision: BTC spot or short-horizon signals may be reused only as registered
research inputs. Perpetual contract identity, collateral, position mode,
margin, PnL, funding, liquidation, ADL, insurance-fund, venue lifecycle, and
cost evidence remain separate deterministic contracts with effective-time
versions.

Consequence: A profitable spot backtest cannot be labeled a leveraged result.
No leverage level is safe by implication, and last price cannot substitute for
index, mark, bankruptcy, or liquidation price. Venue defaults cannot become
universal FCF rules.

Rejected shortcut: multiply spot returns by leverage or model liquidation from
one fixed percentage without contract, collateral, tier, cost, and event-time
evidence.

Not authorized: leverage runtime, virtual account, Paper order, venue adapter,
wallet, credential, account, balance, position, real order, or execution.

## Register Rules

- An ADR change requires explicit Operator approval and impact analysis.
- An accepted ADR is not evidence of implementation.
- Detailed implementation remains subject to the Readiness Gate.
- External reports and model recommendations remain advisory.
- P1-P47 remain frozen and no P48 is created.
