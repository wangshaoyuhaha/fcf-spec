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

## Roadmap Backlog

| Phase | Scope | Status |
| --- | --- | --- |
| V2-R1 | Factor Contract Foundation | PLANNED / NOT_APPROVED |
| V2-R2 | Historical Factor Baseline | PLANNED / NOT_APPROVED |
| V2-R3 | Realtime Ingestion Foundation | PLANNED / NOT_APPROVED |
| V2-R4 | Intraday Anomaly Radar | PLANNED / NOT_APPROVED |
| V2-R5 | Realtime Cognitive Shield | PLANNED / NOT_APPROVED |
| V2-R6 | Paper Simulation Research | PLANNED / NOT_APPROVED |

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
