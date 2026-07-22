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

## FCF-V2-ADR-035 Preserve QMT Additive Adjustment as Reference Only

Status: ACCEPTED_ARCHITECTURE

Decision: Exact registered Guojin QMT raw daily exports may be normalized into
the FCP-0019 local bridge schema after explicit instrument registration,
YYYYMMDD date normalization, and exact 100-share lot conversion. A paired QMT
front-adjusted export is additive price-offset reference evidence only and
must not be converted into a multiplicative adjustment factor.

Consequence: The adapter preserves raw prices, amount, volume, source bytes,
requested and actual coverage, and front-reference boundaries. Calibration
remains blocked until independent adjustment-factor lineage, trading status,
and point-in-time supplements are registered. Filename inference, silent row
cap acceptance, and factor fabrication fail closed.

Rejected shortcut: derive one daily factor from adjusted close and apply it to
raw OHLC, treat the QMT front export as corporate-action authority, infer the
instrument from `price_600028.txt`, or accept `volumn` as shares.

Not authorized: MiniQMT SDK invocation, network retrieval, credential, provider
selection, raw repository retention, realtime activation, trading API, order,
execution, product phase, tag, release, or deployment.

## FCF-V2-ADR-036 Require Registered Trading Dates for Batch Completeness

Status: ACCEPTED_ARCHITECTURE

Decision: QMT batch completeness is the deterministic set comparison between
merged registered observations and an exact Operator-registered expected
trading-date artifact for the same instrument. Natural days, weekdays,
filenames, directory ordering, and silent row-cap assumptions are not session
authority. Batch sequence and every source digest are immutable lineage.

Consequence: Byte-identical overlaps may be deduplicated. A conflicting overlap
is removed from the merged artifact and quarantined. Missing, unexpected,
conflicting, and declared-row-cap observations remain visible findings.
Coverage completion cannot supply factor, trading-status, or point-in-time
authority.

Rejected shortcut: infer exchange sessions from Monday through Friday, accept
the latest duplicate silently, concatenate files in filesystem order, or label
a 500-row export complete because its final date matches the request.

Not authorized: SDK invocation, network retrieval, credential, provider
selection, raw repository retention, realtime activation, trading API, account,
balance, position, order, execution, product phase, tag, release, or deployment.

## FCF-V2-ADR-037 Make Expected Trading Dates a Versioned Registered Artifact

Status: ACCEPTED_ARCHITECTURE

Decision: An A-share expected trading-date set is authoritative only when exact
local bytes are Operator registered with immutable source, source revision,
market, instrument, range, rights, retention, observed, available, registered,
and revision lineage. Natural days and weekdays are not trading-calendar data.

Consequence: Completeness checks consume an ordered unique ISO date set whose
first and last dates match its declared range. Future revisions fail closed.
Unresolved rights remain visible, and compatibility with FCP-0036 requires an
explicit conversion rather than implicit type or filename inference.

Rejected shortcut: infer Monday through Friday, reuse a stale calendar without
revision identity, infer exchange from a path, ignore availability time, or
label synthetic dates as provider evidence.

Not authorized: calendar scraping, SDK invocation, network retrieval,
credential, provider selection, raw repository retention, realtime activation,
trading API, account, order, execution, product phase, tag, release, or
deployment.

## FCF-V2-ADR-038 Bind Cross-Source Coverage to One Registered Calendar

Status: ACCEPTED_ARCHITECTURE

Decision: QMT and independent-reference A-share datasets may be compared only
under explicit distinct source roles, one shared canonical instrument, and the
same FCP-0037 registered expected trading-date profile. Each source receives
its own missing and unexpected date findings before value reconciliation.

Consequence: FCP-0021 remains the deterministic value and lineage comparison
authority. The composite packet retains calendar, role, dataset, policy,
finding, and result hashes and cannot select a winning provider. Any coverage
or quality mismatch requires quarantine and Operator review.

Rejected shortcut: compare each provider to a different calendar, treat union
coverage as completeness, infer an independent role from a name, or accept
matching prices while dates are missing.

Not authorized: data acquisition, SDK invocation, network retrieval,
credential, provider selection, raw repository retention, realtime activation,
trading API, account, order, execution, product phase, tag, release, or
deployment.

## FCF-V2-ADR-039 Bind Cross-Source Roles to Disjoint Artifact Lineage

Status: ACCEPTED_ARCHITECTURE

Decision: A QMT role and an independent-reference role are cross-source only
when their complete ordered registered source-artifact digest sets are nonempty
and disjoint. Each role hash includes its digest set, and the composite result
includes a typed independence-proof hash.

Consequence: Distinct dataset or source names cannot disguise reused underlying
bytes. Any shared artifact digest fails before calendar coverage or value
comparison. Operator review remains mandatory and no source is selected.

Rejected shortcut: treat different labels as independent, sample only one row
digest, omit artifact lineage from role identity, or continue comparison after
detecting shared bytes.

Not authorized: data acquisition, SDK invocation, network retrieval,
credential, provider selection, raw repository retention, realtime activation,
trading API, account, order, execution, product phase, tag, release, or
deployment.

## FCF-V2-ADR-040 Keep Cross-Source Delta Diagnostics Non-Decisional

Status: ACCEPTED_ARCHITECTURE

Decision: Exact field-delta diagnostics consume only an existing FCP-0038
same-calendar result with its FCP-0039 artifact-independence proof. Diagnostics
operate only on overlapping registered row keys and bind role, dataset,
coverage, proof, field-summary, mismatch, and clock lineage into immutable
hashes.

Consequence: Raw OHLC, volume, amount, paired adjustment factor, factor
version, trading status, and registered clock differences remain visible as
exact descriptive evidence. No diagnostic value is a tolerance, score,
provider rank, or source-selection decision. Operator review remains mandatory.

Rejected shortcut: compare non-overlapping dates, discard missing factor pairs,
infer a preferred provider from the smallest delta, set an implicit tolerance,
or replace either registered source with a derived diagnostic.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, trading
API, account, order, execution, product phase, tag, release, or deployment.

## FCF-V2-ADR-041 Bind Aggregate Diagnostics to Exact Row Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Every aggregate FCP-0040 field-delta diagnostic may be expanded only
from the same typed roles and FCP-0038 coverage evidence into a complete stable
ledger ordered by instrument, trade date, and closed field order. Each entry
retains exact source values and its match, delta, or incomplete state.

Consequence: An aggregate difference can be traced to exact registered row
evidence without inventing a threshold or preferred source. The ledger binds
coverage, artifact-independence, role, diagnostic, and entry hashes. Operator
review remains mandatory.

Rejected shortcut: retain only mismatches, omit incomplete factor pairs, reorder
entries by delta size, accept a diagnostic from different inputs, or treat a
row ledger as authority to replace either source.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, trading
API, account, order, execution, product phase, tag, release, or deployment.

## FCF-V2-ADR-042 Separate Review Facts from Source Decisions

Status: ACCEPTED_ARCHITECTURE

Decision: An Operator delta-review packet derives only closed ordered field
facts and deterministic finding codes from one typed FCP-0041 ledger. Exact
parity still requires Operator confirmation; any delta or incomplete pair
requires Operator review.

Consequence: Review presentation can expose what differs and on which dates
without assigning severity, recommending a provider, setting a tolerance, or
granting acceptance authority. Packet identity binds the ledger and all
inherited upstream hashes.

Rejected shortcut: call exact parity accepted automatically, sort findings by
desirability, label a source better, collapse incomplete evidence into a match,
or turn descriptive counts into a recommendation.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, trading
API, account, order, execution, product phase, tag, release, or deployment.

## FCF-V2-ADR-043 Separate Review Completion from Evidence Acceptance

Status: ACCEPTED_ARCHITECTURE

Decision: One Operator review receipt may be created only from one typed
FCP-0042 packet and explicit safe review metadata. The receipt uses one closed
non-decisional disposition and binds the exact packet, ledger, review-state,
finding, and field-fact lineage.

Consequence: The system can prove that an Operator inspected a packet without
claiming that either source was validated, rejected, preferred, or selected.
Review completion does not close the underlying research gap.

Rejected shortcut: treat acknowledgement as evidence acceptance, accept free
text dispositions, omit the packet hash, mutate findings, infer a winning
source, or close GAP-109 from a synthetic receipt.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, trading
API, account, order, execution, product phase, tag, release, or deployment.

## FCF-V2-ADR-044 Preserve Operator Review Receipts as Immutable History

Status: ACCEPTED_ARCHITECTURE

Decision: A receipt ledger accepts only a nonempty typed FCP-0043 sequence,
orders it by registered review time and review ID, requires unique review IDs
and receipt hashes, and retains every exact packet identity and closed
disposition count.

Consequence: Later review activity cannot silently overwrite, delete, or hide
earlier receipts. Ledger identity commits to the complete ordered history but
does not confer evidence acceptance or source authority.

Rejected shortcut: retain only the latest receipt, sort by disposition, omit
zero counts, accept duplicate review identities, delete deferred reviews, or
infer that the most common disposition resolves GAP-109.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, trading
API, account, order, execution, product phase, tag, release, or deployment.

## Register Rules

## FCF-V2-ADR-050 Preserve QMT Dual-Export Facts Without Inventing Adjustment Authority

Status: ACCEPTED_ARCHITECTURE

Decision: Register exact local raw and front-adjusted QMT daily-export artifact
identity before parsing. Preserve the provider's exact ASCII header, ordered
rows, raw/front parity, 100-share-lot consistency evidence, additive adjustment
references, observed offset boundaries, exact row count, and visible row-cap
state. Keep actual raw bytes and local paths outside the repository.

Consequence: Operator review can audit facts derived from the exact two-file
export without treating a front-adjusted price difference as an official
factor, treating 500 observed rows as complete history, or hiding unresolved
rights, calendar, point-in-time, status, pagination, and independence gaps.

Rejected shortcut: commit provider bytes, store local paths, accept a different
header, use binary floats, infer trading sessions, declare a row-cap value from
row count alone, infer an official factor from additive deltas, or claim that
one paired export closes any source-research gap.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, broker,
account, balance, position, order, execution, product phase, P48, tag, release,
or deployment.

## Register Rules

## FCF-V2-ADR-049 Preserve Signed BTC Fee And Rebate Schedules As Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve BTC perpetual fee and rebate schedules as exact typed local
evidence. Bind each version to one immutable FCP-0046 contract entry and retain
signed maker and taker rates, contiguous trailing-volume tiers, measurement
asset and window, fee assets, and half-open UTC effective-time semantics.

Consequence: Later deterministic Paper cost accounting can consume reproducible
historical schedule evidence without treating current venue fees as timeless,
discarding rebates, or selecting a real account tier.

Rejected shortcut: use floats, clamp negative rebates to zero, infer a tier,
fill missing ranges, overlap volume bands or effective intervals, accept an
unbound contract, or let the registry calculate costs.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, realtime activation, wallet, account, balance, position,
account-tier selection, fee or rebate calculation, PnL, liquidation, funding,
order, execution, product phase, tag, release, or deployment.

## Register Rules

## FCF-V2-ADR-048 Resolve BTC Funding Rules Only From Exact Contract-Bound Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve BTC perpetual funding rules as exact typed local evidence.
Bind each version to one immutable FCP-0046 contract entry and preserve closed
method and basis semantics, interval, UTC anchor, signed rate bounds, interest
component, payer convention, and half-open UTC effective-time semantics.

Consequence: Later deterministic Paper accounting can consume reproducible
historical funding-rule evidence without treating current venue conventions as
timeless or confusing rule lookup with rate or payment calculation.

Rejected shortcut: use floats, infer a schedule from observations, fill
effective-time gaps, overlap versions, accept an unbound contract, assume the
positive-rate payer, or let the registry calculate rates or payments.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, realtime activation, wallet, account, balance, position,
funding-rate or payment calculation, PnL, liquidation, fee, order, execution,
product phase, tag, release, or deployment.

## Register Rules

## FCF-V2-ADR-047 Resolve BTC Margin Rules Only From Exact Contract-Bound Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve BTC perpetual margin rules as exact typed local evidence.
Bind each version to one immutable FCP-0046 contract entry, preserve closed
margin and position modes, contiguous exact risk tiers, collateral haircuts,
and half-open UTC effective-time semantics. Every lookup must return exactly
one registered rule or fail closed.

Consequence: Later deterministic Paper accounting can consume reproducible
historical rate evidence without treating current venue tiers as timeless or
confusing rule lookup with balance, position, margin, or liquidation math.

Rejected shortcut: use floats, infer missing tiers, fill effective-time gaps,
overlap notional bands, accept an unbound contract, use a current venue default,
or let the registry calculate balances, positions, PnL, or liquidation.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, realtime activation, wallet, account, balance, position,
margin calculation, PnL, liquidation, funding, fee, order, execution, product
phase, tag, release, or deployment.

## Register Rules

## FCF-V2-ADR-046 Resolve BTC Contract Rules Only by Registered Effective Time

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve every BTC perpetual contract-rule version as typed local
registered evidence with exact settlement, asset, multiplier, precision,
minimum, lifecycle, migration, and half-open UTC effective-time semantics.
Point-in-time resolution must return exactly one version or fail closed.

Consequence: Later Paper accounting can reference reproducible historical
contract semantics without treating current venue rules as timeless constants.

Rejected shortcut: hard-code one global BTC contract, accept float precision,
project linear rules onto inverse contracts, overlap versions, fill time gaps,
infer migration targets, or use the registry as a calculation or execution
engine.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, realtime activation, margin, liquidation, PnL, funding,
wallet, account, order, execution, product phase, tag, release, or deployment.

## Register Rules

## FCF-V2-ADR-045 Preserve Exact BTC Observation Deltas Across Every Source Pair

Status: ACCEPTED_ARCHITECTURE

Decision: Derive one immutable ledger only after exact FCP-0023 result
recomputation. Preserve all ordered dataset pairs, pairwise union keys, closed
observation fields, exact source values, exact applicable deltas, explicit
incomplete states, and complete upstream hash lineage.

Consequence: Operator review can inspect the exact value behind every BTC
cross-source finding or coverage gap without changing the registered
reconciliation policy or result.

Rejected shortcut: retain findings without values, compare only the all-source
intersection, fill missing observations, round decimal values, omit book
levels, change a tolerance, infer a better venue, or close a research gap.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, trading
API, wallet, account, order, execution, product phase, tag, release, or
deployment.

## FCF-V2-ADR-051 Require Positive Registered Proof Before Claiming QMT Historical Completeness

Status: ACCEPTED_ARCHITECTURE

Decision: Bind completeness assessment to one exact FCP-0050 record and a
closed requirement matrix. Requested-boundary coverage, expected trading-date
authority, pagination evidence, deterministic FCP-0036 multi-batch coverage,
conflict-free reconciliation, and point-in-time supplements must all be
positively registered before completeness can be true.

Consequence: The current 500-row export produces useful quality evidence and
an exact unresolved leading interval, while remaining blocked instead of being
mistaken for complete history. Future supplemental batches can satisfy the
same contract without changing upstream factor or strategy code.

Rejected shortcut: infer sessions from weekdays or natural days, treat a row
cap as a complete result, infer provider pagination, omit expected-date
authority, ignore overlap conflicts, or weaken the gate to accept absent
evidence.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, broker,
account, balance, position, order, execution, product phase, P48, tag, release,
or deployment.

## Register Rules

## FCF-V2-ADR-052 Derive QMT Coverage Supplements Only from Typed Coherent Lineage

Status: ACCEPTED_ARCHITECTURE

Decision: Bind FCP-0051 coverage supplements to typed FCP-0037 calendar and
FCP-0036 multi-batch evidence plus typed pagination, point-in-time, and row-cap
resolution records. Exact instrument, requested range, expected date-set hash,
and upstream manifest lineage must agree before supplement hashes are derived.

Consequence: A digest cannot be inserted as apparent proof for another
instrument, interval, calendar, or batch result. Missing real evidence remains
missing and the existing coverage gate remains fail closed.

Rejected shortcut: accept arbitrary hashes or counts, mix instruments or
ranges, treat one batch as multi-batch evidence, infer pagination, or derive a
row-cap resolution without exact pagination and batch lineage.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, broker,
account, balance, position, order, execution, product phase, P48, tag, release,
or deployment.

## FCF-V2-ADR-053 Resolve BTC Perpetual Rule Bundles Only from Coherent Point-in-Time Lineage

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one FCP-0046 contract lifecycle registry and the dependent
FCP-0047 margin, FCP-0048 funding, and FCP-0049 fee registries by exact
contract-registry hash. At one UTC instant, resolve exact versions for one
venue and contract, require every dependent rule to bind the resolved contract
entry, and emit only an immutable evidence-lineage snapshot.

Consequence: Downstream paper research can reference one coherent rule context
without silently mixing venue rule versions or granting any calculation or
execution authority. Missing, overlapping, or mismatched evidence fails
closed.

Rejected shortcut: combine independent registry lookups without checking their
shared contract registry, mix contract-entry versions, infer a missing rule,
select a preferred venue, or include account-dependent calculations.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-061 Use Kind-Specific Domains For Stress Scenario Parameters

Status: ACCEPTED_ARCHITECTURE

Decision: Validate exact typed FCP-0056 scenario parameters against a closed
kind-specific domain schema bound to exact FCP-0057 coverage. Funding shocks
remain signed and finite; ratios are bounded; and counts or seconds are
positive integral counts or seconds where a nonzero stress duration or
sequence is required.

Consequence: Later deterministic Paper evaluation cannot consume impossible
negative durations, fractional loss counts, or out-of-range stress ratios.

Rejected shortcut: validate units only, clamp values, accept binary floats, or
treat parameter validation as direction selection or stress evaluation.

Not authorized: acquisition, SDK, network, credential, realtime, product, P48,
exchange, wallet, account, balance, position, order, execution, tag, release,
or deployment.

## FCF-V2-ADR-062 Require Parameter-Domain-Coherent Stress Readiness

Status: ACCEPTED_ARCHITECTURE

Decision: Bind exact typed FCP-0060 readiness and FCP-0061 scenario-parameter
domain snapshots. Require exact coverage, complete-rule, venue, contract,
scenario, definition, parameter-schema, and monotonic UTC lineage.

Consequence: Later deterministic Paper evaluation cannot bypass the
kind-specific parameter-domain validation by consuming the earlier readiness
receipt alone.

Rejected shortcut: trust labels, accept either receipt independently, ignore
definition or schema hashes, permit time reversal, or treat coherence as a
stress result.

Not authorized: acquisition, SDK, network, credential, realtime, product, P48,
exchange, wallet, account, balance, position, order, execution, tag, release,
or deployment.

## FCF-V2-ADR-063 Register Complete Stress Evaluation Operands Before Direction

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0062 extended-readiness snapshot and
register closed operand roles, metric identifiers, and units for every BTC
perpetual Paper stress kind. Distinguish threshold-only observations from
paired baseline-current evidence before any direction or evaluation logic.

Consequence: A later deterministic Paper evaluator cannot infer a price gap,
collateral drawdown, funding shock, or depth-retention change from an
insufficient single-point observation.

Rejected shortcut: infer missing baselines, reuse one metric across roles,
accept arbitrary mappings, define direction implicitly, or treat operand
schema registration as a stress result.

Not authorized: acquisition, SDK, network, credential, realtime, product, P48,
exchange, wallet, account, balance, position, order, execution, tag, release,
or deployment.

## FCF-V2-ADR-064 Require Registered Evidence For Every Stress Operand

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0063 operand-schema snapshot and register one
typed local observation for every required role. Preserve exact metric, unit,
venue, contract, event, availability, source artifact, digest, and rights
lineage, with baseline observations preceding paired current observations.

Consequence: Later deterministic Paper evaluation cannot fill missing
baselines, reuse one observation across roles, or consume future or
unregistered operand evidence.

Rejected shortcut: infer operands from labels, duplicate one observation,
ignore point-in-time availability or rights, accept arbitrary mappings, or
treat registration as a stress result.

Not authorized: acquisition, SDK, network, credential, realtime, product, P48,
exchange, wallet, account, balance, position, order, execution, tag, release,
or deployment.

## FCF-V2-ADR-065 Bind Complete Typed Context Before Stress Formulas

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0056 scenario registry, one exact typed
FCP-0062 extended-readiness snapshot, and one exact typed FCP-0064 operand-
evidence registry before any direction or formula semantics are registered.
Require definition hashes, complete-rule bundle, venue, contract, operand-
schema ancestry, and monotonic UTC lineage to agree exactly.

Consequence: A later deterministic Paper formula registry cannot consume
orphan operands, stale definitions, cross-contract context, or substituted
scenario parameters.

Rejected shortcut: trust hash labels without typed upstream objects, infer
definitions from scenario names, join different as-of times, or treat context
coherence as a stress result.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-066 Register Explicit Stress Direction Before Formulas

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0065 evaluation context and register one
closed direction, comparison family, operand-role order, and equality policy
for each of the eight BTC perpetual Paper stress kinds before any threshold or
severity formula is registered.

Consequence: A later formula registry cannot reverse risk direction, silently
change an inclusive boundary, confuse baseline and current operands, or treat
signed funding and price changes as one-sided without explicit semantics.

Rejected shortcut: infer direction from scenario names, embed comparisons in
an evaluator, omit equality behavior, swap baseline and current roles, or
treat direction registration as a stress result.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-060 Require Coherent Stress Evaluation Readiness Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Bind exact typed FCP-0055 complete-rule, FCP-0057 coverage, and
FCP-0059 input-domain snapshots before any later BTC perpetual Paper stress
evaluation. Require exact snapshot hashes, venue and contract identities,
closed scenario coverage, and monotonic effective or as-of UTC ordering.

Consequence: Later deterministic evaluation can receive one immutable
readiness receipt without silently joining stale, cross-contract, or unrelated
rule, scenario, and input evidence.

Rejected shortcut: join by labels, accept arbitrary mappings, ignore snapshot
hashes, permit reversed time lineage, infer missing scenarios, or treat
readiness as an evaluation result.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-054 Preserve BTC Liquidation Mechanics As Versioned Evidence Before Calculation

Status: ACCEPTED_ARCHITECTURE

Decision: Register mark, index, bankruptcy, liquidation, partial-liquidation,
liquidation-fee, insurance-fund, ADL-ranking, and cascade-state mechanics as
exact point-in-time evidence bound to one FCP-0046 contract entry. Preserve
method and component lineage without implementing the calculations.

Consequence: Future deterministic Paper stress and risk engines can consume
one auditable venue-rule version without inventing a formula, mixing contract
versions, or granting the registry account or execution authority.

Rejected shortcut: derive liquidation rules from observed prices, assume one
venue formula, omit partial-liquidation tiers, treat insurance fund or ADL as
an execution instruction, or infer missing effective-time evidence.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-055 Require Liquidation Evidence In The Complete BTC Rule Bundle

Status: ACCEPTED_ARCHITECTURE

Decision: Harden the FCP-0053 point-in-time rule bundle with one exact typed
FCP-0054 liquidation-mechanics registry. Require both inputs to share the exact
FCP-0046 contract-registry hash and resolved contract-entry hash before
producing an immutable complete-rule snapshot.

Consequence: Later deterministic Paper stress and risk gates can consume one
coherent contract, margin, funding, fee, and liquidation evidence context
without independently joining rule versions or silently mixing effective time.

Rejected shortcut: attach an FCP-0054 hash without resolving its effective rule,
accept a different contract registry or contract entry, infer missing evidence,
or calculate liquidation, account state, or execution inside the gate.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-056 Register BTC Paper Stress Definitions Before Evaluation

Status: ACCEPTED_ARCHITECTURE

Decision: Register BTC perpetual Paper stress scenarios as immutable typed
definitions bound to one exact FCP-0055 complete rule-bundle snapshot. Use a
closed scenario-kind vocabulary and exact decimal parameters before any later
stress evaluator or risk gate is introduced.

Consequence: Later deterministic Paper evaluation can prove which venue-rule
context, scenario kind, severity, horizon, and parameter evidence it consumed
without inventing assumptions at evaluation time.

Rejected shortcut: reuse a generic portfolio scenario without BTC contract
lineage, accept arbitrary mappings or floats, treat definitions as evaluated
results, or infer missing calibration evidence.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-057 Require Complete Stress Coverage Before Evaluation

Status: ACCEPTED_ARCHITECTURE

Decision: Gate one exact FCP-0056 BTC perpetual Paper stress-definition
registry against a closed parameter schema before any evaluator is introduced.
Require every registered scenario kind and exact parameter identifiers and
units, then preserve one immutable coverage snapshot.

Consequence: Later deterministic Paper evaluation can consume a complete,
schema-checked suite without silently omitting venue outage, resync, funding,
loss, collateral, liquidation-distance, price-gap, or thin-book stress.

Rejected shortcut: treat registry presence as complete coverage, accept
arbitrary parameter names or units, infer missing scenarios, or reuse a generic
portfolio stress definition without exact FCP-0056 lineage.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-058 Require Registered Stress Inputs Before Evaluation

Status: ACCEPTED_ARCHITECTURE

Decision: Register one exact typed evaluation-input observation for every
closed FCP-0057 BTC perpetual Paper stress kind before any deterministic stress
calculation is introduced. Bind metric, unit, event time, availability time,
source artifact, digest, rights, and coverage-snapshot lineage.

Consequence: A later deterministic Paper evaluator can consume complete,
point-in-time input evidence without inventing missing prices, depth, funding,
heartbeat, resync, loss, collateral-reference, or liquidation-distance values.

Rejected shortcut: accept arbitrary mappings or floats, omit availability or
rights lineage, reuse one observation for multiple kinds, infer missing venue
evidence, or treat input registration as a calculated stress result.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-059 Use Metric-Specific Domains For Stress Inputs

Status: ACCEPTED_ARCHITECTURE

Decision: Validate FCP-0058 BTC perpetual Paper stress-evaluation inputs against
closed metric-specific numeric domains. Funding-reference rates are finite and
signed; price, depth, and collateral-index references are positive;
liquidation-distance ratios are bounded from zero through one; and count and
seconds inputs are nonnegative integers.

Consequence: Later deterministic Paper evaluation can consume valid negative
funding evidence without also admitting impossible negative prices, depth,
durations, counts, or liquidation-distance ratios.

Rejected shortcut: apply one nonnegative rule to every metric, silently clamp
invalid inputs, accept binary floats, infer missing signs, or treat domain
validation as a stress result or venue calibration.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-067 Register Closed Stress Measure Formulas Before Evaluation

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0066 direction registry and register one
closed symbolic measure formula family, operand and scenario-parameter roles,
output unit, parameter transform, and denominator policy for each of the eight
BTC perpetual Paper stress kinds before any evaluator is introduced.

Consequence: A later deterministic evaluator cannot substitute executable
expressions, reverse operands, change relative versus absolute measurement,
silently admit a zero denominator, or detach a formula from its registered
direction and scenario parameter.

Rejected shortcut: store arbitrary expression strings, calculate a result in
the registry, infer parameter units, divide by an unchecked baseline, collapse
absolute and relative change, or treat formula registration as stress evidence.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-068 Bind Closed Stress Trigger Predicates Before Evaluation

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0067 formula registry and register one
closed comparison operator, left-right role order, parameter transform, and
strict or inclusive boundary policy for each of the eight BTC perpetual Paper
stress kinds before any evaluator is introduced.

Consequence: A later deterministic evaluator cannot reverse comparison roles,
change strictness at a threshold boundary, detach a predicate from its formula
or parameter transform, or introduce arbitrary executable expressions.

Rejected shortcut: infer operators from names, store arbitrary predicates,
evaluate a boolean in the registry, ignore equality policy, reverse left and
right roles, or treat predicate registration as a stress result.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-069 Bind Registered Stress Inputs Before Evaluation

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0068 predicate registry, FCP-0064 operand
evidence registry, and FCP-0056 scenario registry into one closed ordered input
binding for each BTC perpetual Paper stress kind before an evaluator is
introduced.

Consequence: A later deterministic evaluator cannot substitute evidence,
reorder operand roles, select an unrelated parameter, cross venue or contract
lineage, or read observations that were unavailable at the registered cutoff.

Rejected shortcut: let an evaluator search arbitrary registries, bind raw
values by name, omit parameter hashes, ignore evidence order, or treat an input
binding as a calculated stress result.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-070 Evaluate Closed Stress Triggers With Exact Decimal Arithmetic

Status: ACCEPTED_ARCHITECTURE

Decision: Evaluate only the FCP-0067 closed formulas and FCP-0068 closed
predicates over exact FCP-0069-bound registered inputs. Use Decimal arithmetic,
explicit denominator rejection, registered transforms, and exact strict or
inclusive comparison boundaries.

Consequence: Paper stress results are deterministic, replayable, hash-bound,
unit-explicit, and reviewable without granting account or execution authority.

Rejected shortcut: use float arithmetic, infer formulas or comparisons from
names, accept unbound values, hide denominator failure, calculate account
state, or treat a synthetic Paper trigger as evidence that a Gap is closed.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-071 Bind Stress Trigger Results To Reviewable Scenario Evidence

Status: ACCEPTED_ARCHITECTURE

Decision: Register one immutable review record for every exact typed FCP-0070
trigger result and bind it to the exact FCP-0056 scenario identity, version,
severity, horizon, definition hash, evaluation hash, measure, parameter, and
trigger state. Preserve mandatory Operator review and add no calculation or
action recommendation.

Consequence: A later presentation or review workflow can inspect complete
stress findings without detaching a result from its scenario definition or
mistaking a trigger for account or execution authority.

Rejected shortcut: copy unbound result values, omit non-triggered records,
reclassify severity, infer an action from a boolean, calculate account state,
or treat a reviewed synthetic Paper result as evidence that a Gap is closed.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-072 Package Stress Trigger Review Evidence Without Disposition

Status: ACCEPTED_ARCHITECTURE

Decision: Build one immutable Operator review packet from one exact typed
FCP-0071 review registry. Preserve every ordered review-record hash and exact
triggered or non-triggered membership while exposing complete packet lineage
and mandatory Operator review state.

Consequence: A later explicit review receipt can refer to one complete packet
without dropping non-triggered evidence, rewriting scenario severity, or
detaching any result from its registered lineage.

Rejected shortcut: omit non-triggered records, reorder evidence, infer a
disposition, approve or reject a result, recommend an action, calculate
account state, or treat the synthetic Paper packet as Gap-closing evidence.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-073 Record Explicit Review Without Resolution Authority

Status: ACCEPTED_ARCHITECTURE

Decision: Register one immutable explicit Operator review receipt against one
exact typed FCP-0072 packet. Preserve packet and record-hash lineage, reviewer
reference, reviewed UTC time, and one closed non-authorizing disposition.

Consequence: Later audit can prove that an Operator inspected the complete
packet without treating review occurrence as evidence approval, rejection,
result resolution, action authorization, or Gap closure.

Rejected shortcut: omit packet records, accept an unregistered disposition,
backdate the receipt, approve or reject evidence, recommend an action,
calculate account state, or close a Gap from synthetic Paper review evidence.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, balance, position, order, execution, product phase, P48, tag,
release, or deployment.

## FCF-V2-ADR-074 Separate Reusable Signal Evidence From Derivative Mechanics

Status: ACCEPTED_ARCHITECTURE

Decision: Register one closed ordered BTC perpetual Paper evidence-domain
contract. Only `REUSABLE_MARKET_SIGNAL` may identify evidence eligible for
later cross-market signal research. Contract, leverage-margin, cost-funding,
liquidation-risk, and outcome-accounting evidence remain derivative-specific.

Consequence: Later research can prove which registered facts are reusable
without mixing leverage, liquidation, funding, execution-cost, or outcome
accounting into the signal definition.

Rejected shortcut: infer a domain from an artifact name, omit a closed domain,
reuse derivative-specific evidence as a signal, aggregate the domains into one
score, promote a factor, select a strategy, or claim profitability.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, exchange,
wallet, account, margin, leverage, liquidation, balance, position, PnL, order,
execution, product phase, P48, tag, release, or deployment.

## FCF-V2-ADR-075 Quarantine Unverified External Daily Data Before Promotion

Status: ACCEPTED_ARCHITECTURE

Decision: Register path-free deterministic quality findings for an external
candidate A-share daily corpus while keeping every raw row outside Git and
outside Registered Evidence authority. Structural validity, value quality,
coverage, adjustment ambiguity, provenance, and rights risk remain separate
closed evidence domains.

Consequence: The same fail-closed quality contract can later compare MiniQMT,
RQData, Tushare, or another approved provider without allowing a large or
well-formed downloaded corpus to become authoritative by appearance alone.

Rejected shortcut: copy third-party raw rows into Git, infer provider identity
or license, treat adjusted prices as official factors, infer suspension from a
missing row, equate schema consistency with accuracy, or promote quarantined
candidate observations to calculations or labels.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, broker,
exchange, account, balance, position, order, execution, product phase, P48,
tag, release, or deployment.

## FCF-V2-ADR-076 Fail Closed Before Candidate Daily Promotion

Status: ACCEPTED_ARCHITECTURE

Decision: Bind one exact typed FCP-0075 quarantine evidence artifact to a
closed ordered set of registered provider, rights, revision, corporate-action,
adjustment-factor, trading-status, expected-calendar, and point-in-time
authority references. Emit deterministic blockers and readiness for mandatory
Operator review only.

Consequence: Every downloaded file, RQData response, MiniQMT export, Tushare
dataset, or later provider candidate crosses the same explicit gate before any
separate promotion decision can be proposed.

Rejected shortcut: treat clean syntax as authority, waive observed anomalies,
infer rights or provenance, infer suspension from missing bars, infer official
adjustment factors, accept an incomplete authority domain set, or let the gate
promote data itself.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, broker,
exchange, account, balance, position, order, execution, product phase, P48,
tag, release, or deployment.

## FCF-V2-ADR-077 Separate Foundation Coverage From Data Authority

Status: ACCEPTED_ARCHITECTURE

Decision: Verify exact tracked implementation bytes and map their closed
capability claims to V2-FR-GAP-087 through V2-FR-GAP-093 without changing the
Gap registry. Foundation coverage and registered external authority are
different evidence classes.

Consequence: Existing schemas, clocks, storage layers, bridges,
reconciliations, and provider profiles become visible and reusable without
being mistaken for license, provenance, calendar, corporate-action,
adjustment-factor, trading-status, revision, point-in-time, or provider
authority.

Rejected shortcut: treat code presence as data authority, close a Gap because
foundation coverage is complete, accept an unverified file hash, hide missing
capabilities, select a provider, or promote candidate data from the matrix.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, broker,
exchange, account, balance, position, order, execution, product phase, P48,
tag, release, or deployment.

## FCF-V2-ADR-078 Preserve Exact Publication Time Without Inference

Status: ACCEPTED_ARCHITECTURE

Decision: Define one immutable A-share publication and availability clock
record with explicit timestamp precision, legal availability, retrieval,
ingest, first-tradable, revision, and predecessor lineage. Exact-time use must
fail closed when publication evidence is date-only or unknown.

Consequence: Point-in-time research can distinguish source publication from
later retrieval and local ingest. Existing institutional-calendar semantics
can be reused without treating a date label or ingestion time as publication.

Rejected shortcut: infer publication time from trade date, file modification
time, retrieval time, ingest time, or a default market-session boundary; treat
date-only publication as an exact instant; or ignore a later revision.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, data
authority, Gap closure, candidate promotion, broker, exchange, account,
balance, position, order, execution, product phase, P48, tag, release, or
deployment.

## FCF-V2-ADR-079 Separate Corporate Actions From Price Query Policy

Status: ACCEPTED_ARCHITECTURE

Decision: Preserve immutable corporate-action revisions, adjustment-factor
revisions, and explicit RAW or FORWARD_ADJUSTED query policies as distinct
lineage records. Point-in-time selection uses only source and factor revisions
observable at the query as-of time.

Consequence: A price view can prove which raw observation, action revision set,
factor revision, and query policy produced it. Source prices remain immutable,
and an adjusted view cannot silently inherit a provider's current factor.

Rejected shortcut: overwrite raw prices; derive an official action from price
jumps; use a future adjustment factor; accept an unspecified adjustment mode;
or treat one current forward-adjusted series as historical point-in-time truth.

Not authorized: acquisition, SDK invocation, network retrieval, credential,
provider selection, raw repository retention, realtime activation, data
authority, Gap closure, candidate promotion, broker, exchange, account,
balance, position, order, execution, product phase, P48, tag, release, or
deployment.

- An ADR change requires explicit Operator approval and impact analysis.
- An accepted ADR is not evidence of implementation.
- Detailed implementation remains subject to the Readiness Gate.
- External reports and model recommendations remain advisory.
- P1-P47 remain frozen and no P48 is created.
