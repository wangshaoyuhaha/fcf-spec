# FCF V2 Factor, Realtime, and Cognitive Gap and Backlog Register

Register status: AUTHORITATIVE_FUTURE_WORK_REGISTER

No entry in this register is delivered merely because it is documented.

## Status Definitions

- `ACCEPTED_ARCHITECTURE`: accepted future design without runtime evidence
- `BACKLOG`: required or useful future work with no implementation approval
- `RESEARCH_REQUIRED`: evidence, vendor, formula, policy, or feasibility is not
  sufficient for implementation
- `NOT_IMPLEMENTED`: the named runtime capability does not currently exist
- `PLANNED`: ordered future work, still not approved to start
- `OUTSIDE_CURRENT_AUTHORIZATION`: intentionally excluded from current
  authority and not queued for implementation

## Foundation Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-001 | production Factor Registry runtime | NOT_IMPLEMENTED |
| V2-FR-GAP-002 | forecast-target and label registry | NOT_IMPLEMENTED |
| V2-FR-GAP-003 | State-Sync Lock runtime | NOT_IMPLEMENTED |
| V2-FR-GAP-004 | macro-to-micro transmission registry | NOT_IMPLEMENTED |
| V2-FR-GAP-005 | factor dependency DAG and invalidation propagation | NOT_IMPLEMENTED |
| V2-FR-GAP-006 | multi-horizon conflict resolver and UI | NOT_IMPLEMENTED |
| V2-FR-GAP-007 | versioned factor lifecycle and retirement process | NOT_IMPLEMENTED |

V2-R1 supplies contract-only schemas, append-only in-memory validation, and a
local State-Sync anchor. The first three foundation production-runtime gaps
remain NOT_IMPLEMENTED; target selection remains RESEARCH_REQUIRED and no
factor is activated.

## Factor and Research Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-008 | complete technical indicator library | BACKLOG |
| V2-FR-GAP-009 | robust factor normalization and missing-state implementation | BACKLOG |
| V2-FR-GAP-010 | factor correlation, clustering, VIF, and ablation validation | RESEARCH_REQUIRED |
| V2-FR-GAP-011 | transparent initial Champion factor set | RESEARCH_REQUIRED |
| V2-FR-GAP-012 | target, horizon, benchmark, and success metric selection | RESEARCH_REQUIRED |
| V2-FR-GAP-013 | market-regime and dynamic-threshold validation | RESEARCH_REQUIRED |
| V2-FR-GAP-014 | advanced multiple-testing and overfitting controls | BACKLOG |

## Capital-Flow and Microstructure Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-015 | capital-flow proxy definition and confidence classes | RESEARCH_REQUIRED |
| V2-FR-GAP-016 | aggressor-classification validation | RESEARCH_REQUIRED |
| V2-FR-GAP-017 | order-book snapshot and delta synchronization | NOT_IMPLEMENTED |
| V2-FR-GAP-018 | sequence, checksum, resync, and replay behavior | NOT_IMPLEMENTED |
| V2-FR-GAP-019 | depth, OFI, microprice, CVD, and book-life factors | NOT_IMPLEMENTED |
| V2-FR-GAP-020 | hidden-liquidity and aggregation-error treatment | RESEARCH_REQUIRED |
| V2-FR-GAP-021 | impact, partial-fill, and capacity calibration | RESEARCH_REQUIRED |

## Realtime and Operations Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-022 | approved realtime source selection | RESEARCH_REQUIRED |
| V2-FR-GAP-023 | license, permitted use, retention, and cost review | RESEARCH_REQUIRED |
| V2-FR-GAP-024 | realtime ingestion process and queue | NOT_IMPLEMENTED |
| V2-FR-GAP-025 | data interruption, clock, and multi-source conflict runtime | NOT_IMPLEMENTED |
| V2-FR-GAP-026 | intraday anomaly radar | NOT_IMPLEMENTED |
| V2-FR-GAP-027 | alert state machine and fatigue controls | NOT_IMPLEMENTED |
| V2-FR-GAP-028 | latency, throughput, queue, expiry, and recovery objectives | RESEARCH_REQUIRED |
| V2-FR-GAP-029 | deterministic fault injection and restart replay | BACKLOG |
| V2-FR-GAP-030 | realtime storage and retention cost | RESEARCH_REQUIRED |
| V2-FR-GAP-031 | multi-asset concurrency and resource isolation capacity | RESEARCH_REQUIRED |

## AI and Governance Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-032 | asynchronous AI invocation boundary implementation | NOT_IMPLEMENTED |
| V2-FR-GAP-033 | task timeout, registered fallback, and cancellation runtime | NOT_IMPLEMENTED |
| V2-FR-GAP-034 | uncertainty, calibration, and abstention layer | NOT_IMPLEMENTED |
| V2-FR-GAP-035 | macro-to-micro evidence challenge workflow | NOT_IMPLEMENTED |
| V2-FR-GAP-036 | Operator alert capacity and review-budget validation | RESEARCH_REQUIRED |
| V2-FR-GAP-037 | human-feedback bias and post-hoc contamination controls | BACKLOG |

## Paper Research Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-038 | A-share intraday Paper replay | NOT_IMPLEMENTED |
| V2-FR-GAP-039 | BTC short-horizon Paper leverage research | NOT_IMPLEMENTED |
| V2-FR-GAP-040 | fee, funding, liquidation, delay, and book-depth calibration | RESEARCH_REQUIRED |
| V2-FR-GAP-041 | Paper order and virtual-account runtime | OUTSIDE_CURRENT_AUTHORIZATION |

## Product and Business Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-042 | first MVP market selection | RESEARCH_REQUIRED |
| V2-FR-GAP-043 | MVP success, failure, and stop thresholds | RESEARCH_REQUIRED |
| V2-FR-GAP-044 | data and compute unit economics | RESEARCH_REQUIRED |
| V2-FR-GAP-045 | commercial willingness to pay | RESEARCH_REQUIRED |
| V2-FR-GAP-046 | legal and regulatory professional review | RESEARCH_REQUIRED |
| V2-FR-GAP-047 | repository-owner LICENSE decision | RESEARCH_REQUIRED |

## Market Session and Intraday Baseline Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-048 | versioned Market Session Registry and exchange calendar | NOT_IMPLEMENTED |
| V2-FR-GAP-049 | same-time-of-day and regime baseline engine | NOT_IMPLEMENTED |
| V2-FR-GAP-050 | A-share call-auction source fields and venue-rule validation | RESEARCH_REQUIRED |
| V2-FR-GAP-051 | auction imbalance, cancellation, stability, and convergence factors | NOT_IMPLEMENTED |
| V2-FR-GAP-052 | A-share 14:30 late-session and closing research contract runtime | NOT_IMPLEMENTED |
| V2-FR-GAP-053 | entrusted-order ratio, volume ratio, and turnover definition registry | NOT_IMPLEMENTED |

## Sector and Cross-Market Context Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-054 | point-in-time sector and theme taxonomy | RESEARCH_REQUIRED |
| V2-FR-GAP-055 | sector breadth, rotation, leader, and diffusion graph | NOT_IMPLEMENTED |
| V2-FR-GAP-056 | cross-asset and macro lead-lag hypothesis validation | RESEARCH_REQUIRED |
| V2-FR-GAP-057 | multiple-taxonomy conflict and membership uncertainty handling | NOT_IMPLEMENTED |

## Candidate and Operator Workspace Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-058 | research candidate lifecycle and immutable review history | NOT_IMPLEMENTED |
| V2-FR-GAP-059 | negative evidence, invalidation, expiry, cooldown, and deduplication | NOT_IMPLEMENTED |
| V2-FR-GAP-060 | read-only Operator research control plane | NOT_IMPLEMENTED |
| V2-FR-GAP-061 | session-aware alert budget and Operator fatigue controls | NOT_IMPLEMENTED |
| V2-FR-GAP-062 | observed-versus-inferred field presentation and confidence UI | NOT_IMPLEMENTED |

## Adaptive Research and Evaluation Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-063 | offline adaptive-research proposal pipeline | NOT_IMPLEMENTED |
| V2-FR-GAP-064 | deterministic Challenger evaluation and promotion evidence | NOT_IMPLEMENTED |
| V2-FR-GAP-065 | automatic learning, promotion, and self-modification runtime | OUTSIDE_CURRENT_AUTHORIZATION |
| V2-FR-GAP-066 | session-aware precision, calibration, lead-time, and false-alert metrics | NOT_IMPLEMENTED |
| V2-FR-GAP-067 | auction and late-session point-in-time replay realism | NOT_IMPLEMENTED |
| V2-FR-GAP-068 | clock alignment, latency, and cross-market time reconciliation | NOT_IMPLEMENTED |
| V2-FR-GAP-069 | spoofing, manipulation, and participant-identity non-claim controls | NOT_IMPLEMENTED |
| V2-FR-GAP-070 | BTC continuous-session analysis-window and regime adapter | NOT_IMPLEMENTED |

## Institutional Calendar and Causal Market Intelligence Gaps

| ID | Gap | Status |
| --- | --- | --- |
| V2-FR-GAP-071 | official institutional and macro event calendar with point-in-time availability | NOT_IMPLEMENTED |
| V2-FR-GAP-072 | five-clock regime context and market-specific clock adapters | NOT_IMPLEMENTED |
| V2-FR-GAP-073 | overlapping event-state stack and deterministic conflict resolver | NOT_IMPLEMENTED |
| V2-FR-GAP-074 | policy, industry-supply, and capital-transmission graph contracts for POLICY_NOVELTY_ALIGNMENT and CAPITAL_TRANSMISSION_PRESSURE | RESEARCH_REQUIRED |
| V2-FR-GAP-075 | point-in-time consensus, revision, and expectation-gap contract for EARNINGS_SURPRISE | RESEARCH_REQUIRED |
| V2-FR-GAP-076 | EVENT_REACTION_QUALITY measurement and matured outcome labels | NOT_IMPLEMENTED |
| V2-FR-GAP-077 | A-share earnings lifecycle and accounting-quality audit contract | RESEARCH_REQUIRED |
| V2-FR-GAP-078 | EXPIRY_BASIS_ROLL_STRESS research for index-futures basis, open interest, roll, and expiry | RESEARCH_REQUIRED |
| V2-FR-GAP-079 | EQUITY_SUPPLY_PRESSURE ledger for lock-up, reduction, pledge, forced sale, and absorption | RESEARCH_REQUIRED |
| V2-FR-GAP-080 | FX_TRANSMISSION_SENSITIVITY research for rates, DXY, USD/CNY, USD/CNH, and operating exposure | RESEARCH_REQUIRED |
| V2-FR-GAP-081 | INSTITUTIONAL_CROWDING and WINDOW_DRESSING_PRESSURE research with disclosure latency, exit days, and rebalance evidence | RESEARCH_REQUIRED |
| V2-FR-GAP-082 | HOLIDAY_LIQUIDITY_STRESS state machine for holiday, settlement, and thin-liquidity regimes | NOT_IMPLEMENTED |
| V2-FR-GAP-083 | Two Sessions, July, December, and policy-language event studies | RESEARCH_REQUIRED |
| V2-FR-GAP-084 | data freshness, revision lineage, evidence digest, and observed-versus-inferred integrity | NOT_IMPLEMENTED |
| V2-FR-GAP-085 | institutional-factor lifecycle, rejection history, and Operator approval registry | NOT_IMPLEMENTED |
| V2-FR-GAP-086 | leakage, survivorship, multiple-testing, sensitivity, ablation, capacity, and out-of-sample validation | RESEARCH_REQUIRED |

## Roadmap Backlog

| Phase | Scope | Status |
| --- | --- | --- |
| V2-R1 | Factor Contract Foundation | COMPLETED / CONTRACT_FOUNDATION_ONLY |
| V2-R2 | Historical Factor Baseline | COMPLETED / REGISTERED_LOCAL_ARTIFACT_ONLY |
| V2-R3 | Realtime Ingestion Foundation | COMPLETED / LOCAL_REGISTERED_EVENT_ONLY |
| V2-R4 | Intraday Anomaly Radar | COMPLETED / LOCAL_REGISTERED_ANOMALY_RESEARCH_ONLY |
| V2-R5 | Realtime Cognitive Shield | COMPLETED / LOCAL_REGISTERED_COGNITIVE_SHIELD_ONLY |
| V2-R6 | Paper Simulation Research | COMPLETED / LOCAL_REGISTERED_SCENARIO_RESEARCH_ONLY |
| V2-R7 | Local Market Session Registry Foundation | COMPLETED / REGISTERED_LOCAL_CALENDAR_ONLY |
| V2-R8 | Local Same-Time Baseline Foundation | COMPLETED / REGISTERED_LOCAL_HISTORY_ONLY |
| V2-R9 | Local Volume-Ratio Research Foundation | COMPLETED / REGISTERED_LOCAL_VOLUME_EVIDENCE_ONLY |
| V2-R10 | Local Turnover-Definition Research Foundation | COMPLETED / REGISTERED_LOCAL_TURNOVER_EVIDENCE_ONLY |
| V2-R11 | Local Factor Registry Foundation | COMPLETED / REGISTERED_LOCAL_FACTOR_DEFINITION_ONLY |
| V2-R12 | Local Technical Indicator Foundation | COMPLETED / REGISTERED_LOCAL_TECHNICAL_CALCULATION_ONLY |
| V2-R13 | Local Momentum Indicator Foundation | COMPLETED / REGISTERED_LOCAL_MOMENTUM_CALCULATION_ONLY |
| V2-R14 | Local Trend Indicator Foundation | COMPLETED / REGISTERED_LOCAL_TREND_CALCULATION_ONLY |
| V2-R15 | Local Volatility Indicator Foundation | COMPLETED / REGISTERED_LOCAL_VOLATILITY_CALCULATION_ONLY |
| V2-R16 | Local Range Channel Indicator Foundation | COMPLETED / REGISTERED_LOCAL_CHANNEL_CALCULATION_ONLY |
| V2-R17 | Local Stochastic Oscillator Foundation | COMPLETED / REGISTERED_LOCAL_STOCHASTIC_CALCULATION_ONLY |
| V2-R18 | Local Directional Trend Strength Foundation | COMPLETED / REGISTERED_LOCAL_DIRECTIONAL_STRENGTH_CALCULATION_ONLY |
| V2-R19 | Local Percentage Price Oscillator Foundation | COMPLETED / REGISTERED_LOCAL_PERCENTAGE_OSCILLATOR_CALCULATION_ONLY |
| V2-R20 | Local Triple Exponential Oscillator Foundation | COMPLETED / REGISTERED_LOCAL_TRIPLE_EXPONENTIAL_OSCILLATOR_CALCULATION_ONLY |
| V2-R21 | Local Robust Normalization Foundation | COMPLETED / REGISTERED_LOCAL_ROBUST_NORMALIZATION_ONLY |
| V2-R22 | Local Robust Normalization Integrity Hardening | COMPLETED / REGISTERED_LOCAL_NORMALIZATION_INTEGRITY_ONLY |
| V2-R23 | Local Institutional Calendar Evidence Foundation | COMPLETED / REGISTERED_LOCAL_EVENT_EVIDENCE_ONLY |
| V2-R24 | Local Multi-Clock Event State Foundation | COMPLETED / REGISTERED_LOCAL_CLOCK_STATE_ONLY |
| V2-R25 | Local Causal Transmission Graph Foundation | COMPLETED / REGISTERED_LOCAL_CAUSAL_HYPOTHESIS_ONLY |
| V2-R26 | Local Consensus Expectation Gap Foundation | COMPLETED / REGISTERED_LOCAL_EXPECTATION_EVIDENCE_ONLY |
| V2-R27 | Local Event Reaction Quality Foundation | COMPLETED / REGISTERED_LOCAL_REACTION_EVIDENCE_ONLY |
| V2-R28 | Local A-Share Earnings Lifecycle Accounting Quality Foundation | COMPLETED / REGISTERED_LOCAL_ACCOUNTING_CHALLENGE_ONLY |
| V2-R29 | Local Index Futures Basis Roll Expiry Foundation | COMPLETED / REGISTERED_LOCAL_DERIVATIVES_EVIDENCE_ONLY |
| V2-R30 | Local Equity Supply Pressure Foundation | COMPLETED / REGISTERED_LOCAL_EQUITY_SUPPLY_EVIDENCE_ONLY |
| V2-R31 | Local FX Transmission Sensitivity Foundation | COMPLETED / REGISTERED_LOCAL_FX_TRANSMISSION_EVIDENCE_ONLY |
| V2-R32 | Local Institutional Crowding Foundation | COMPLETED / REGISTERED_LOCAL_INSTITUTIONAL_CROWDING_EVIDENCE_ONLY |
| V2-R33 | Local Holiday Liquidity State Foundation | COMPLETED / REGISTERED_LOCAL_HOLIDAY_LIQUIDITY_EVIDENCE_ONLY |
| V2-R34 | Local Policy Window Language Evidence Foundation | COMPLETED / REGISTERED_LOCAL_POLICY_LANGUAGE_EVIDENCE_ONLY |
| V2-R35 | Local Evidence Integrity Foundation | COMPLETED / REGISTERED_LOCAL_EVIDENCE_INTEGRITY_ONLY |
| V2-R36 | Local Institutional Factor Lifecycle Foundation | COMPLETED / REGISTERED_LOCAL_FACTOR_GOVERNANCE_ONLY |
| V2-R37 | Local Factor Validation Evidence Foundation | COMPLETED / REGISTERED_LOCAL_FACTOR_VALIDATION_EVIDENCE_ONLY |
| V2-R38 | Local Operator Factor Governance Projection Foundation | COMPLETED / REGISTERED_LOCAL_OPERATOR_GOVERNANCE_PROJECTION_ONLY |
| V2-R39 | Browser Operator Factor Governance Projection Integration | APPROVED / NOT_STARTED / REGISTERED_LOCAL_BROWSER_GOVERNANCE_PROJECTION_ONLY |

Next product implementation phase: V2-R39 / APPROVED.

No successor phase after V2-R39 starts automatically.

## Entry Gate

No backlog item becomes an implementation phase until its dependencies, data
rights, fields, formulas, labels, safety boundary, tests, rollback, cost,
acceptance metrics, stop rules, and Control Center approval are complete.

Only one first realtime MVP market may be selected. A-share, BTC, and futures
realtime work cannot begin together without a new explicit architectural
decision.

## Permanent Restrictions

No entry authorizes P1-P47 mutation, P48, live retrieval, credentials, account,
balance, position, wallet, broker, exchange, order, execution, automatic
approval, automatic promotion, tag, release, or deployment.
