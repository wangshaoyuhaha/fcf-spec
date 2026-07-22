# FCF Project Memory and Continuity Protocol

Status: ACTIVE_GOVERNANCE_CONTROL

This protocol makes repository evidence, rather than conversation memory, the
authority for resuming FCF work.

The seven core files named in Sections 1 and 2 are collectively the `FCF
Seven-File Project Governance and Memory System`. This stable name refers to
project status, completion evidence, future architecture, decisions, gaps,
change control, and durable intake. It does not refer to a product runtime or
market-analysis subsystem.

## 1. Required Read Order

A new development window must read and verify these sources in order:

1. `docs/FCF_EXECUTION_SAFETY_PROTOCOL.md`
2. `FCF_CURRENT_STATE_MANIFEST.json`
3. `docs/FCF_PROJECT_CONTROL_CENTER.md`
4. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md`
5. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md`
6. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md`
7. `docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md`
8. `FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json`
9. the latest applicable `FCF_CURRENT_STATE_*_FINAL.md` evidence
10. the five active authority sources
11. branch, HEAD, origin reference, and Git status

No implementation may start from chat recollection alone.

## 2. File Roles

The seven core governance and memory files are:

1. `FCF_CURRENT_STATE_MANIFEST.json`
2. `docs/FCF_PROJECT_CONTROL_CENTER.md`
3. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md`
4. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md`
5. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md`
6. `docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md`
7. `FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json`

Execution safety, this continuity protocol, historical evidence, and the five
active authority mirrors govern or support the seven-file system but are not
additional core status registers.

### Seven-File Write Ownership

New work must be separated by file responsibility:

- the manifest stores only current truth, accepted architecture identity, and
  approved phase state
- the Control Center stores human-readable registration, approval, completion,
  validation, merge, and safety lock state
- the future architecture stores module boundaries, contracts, dependencies,
  research order, and non-authorization statements
- the ADR register stores durable decisions, rejected shortcuts, consequences,
  and authority boundaries
- the Gap and Backlog register stores unfinished deliverables and research
  obligations with explicit status
- the change protocol stores intake, review, preservation, approval, and
  implementation-gate rules
- the intake register stores each proposal identity, decision, and links to its
  architecture, ADR, Gap, evidence, and phase records

Detailed formulas do not belong in the manifest or handoff mirrors. Completion
claims do not belong in the future architecture or intake record. A proposal
must not be copied into multiple independent backlogs; canonical identifiers
and references provide the linkage.

`FCF_CURRENT_STATE_MANIFEST.json` is the machine-readable current-truth
entry point. It records the latest completed product phase, the current
governance phase, the next product-phase approval state, the V2-R roadmap,
canonical file roles, and permanent boundaries.

`docs/FCF_PROJECT_CONTROL_CENTER.md` is the human governance authority. It
records approvals, completions, merges, validations, restrictions, and the
current control lock.

`docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md` defines the
accepted future product structure. Documentation in that file is not evidence
that a runtime capability exists.

`docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md` records accepted
architecture decisions and their consequences. ADR acceptance is not
implementation approval.

`docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md` is the authoritative
register for unfinished, research-required, and excluded future work.

`docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md` and
`FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json` are the durable entry point for
new ideas. Intake preserves proposals and review history but cannot authorize
implementation by itself.

`FCF_CURRENT_STATE_*_FINAL.md` files are immutable historical completion
evidence. Historical next-phase statements do not override the current
manifest.

The five active authority sources carry synchronized approval, lock, and final
state blocks. They must never disagree about current approval or safety state.

## 3. Precedence and Conflict Handling

For current phase and approval state, the current manifest wins over historical
handoff text. For future product meaning, the canonical future architecture
wins. For unfinished status, the Gap register wins. For decision rationale,
the ADR register wins. For completed evidence, the applicable final current
state and Git history win.

If two current authorities disagree, work is blocked. The disagreement must be
classified and repaired through an approved governance-only change before any
product implementation starts.

No historical implementation-order registry may select a new current phase.
Only the manifest plus explicit Operator approval may do so.

## 4. Status Discipline

Allowed future-capability statuses are:

- `ACCEPTED_ARCHITECTURE`
- `PLANNED`
- `BACKLOG`
- `RESEARCH_REQUIRED`
- `NOT_IMPLEMENTED`
- `OUTSIDE_CURRENT_AUTHORIZATION`

`OUTSIDE_CURRENT_AUTHORIZATION` is stronger than `NOT_IMPLEMENTED`. It means
the capability is intentionally excluded from current authority and is not a
queued implementation phase.

No future capability may be labeled completed, delivered, validated, or
production-ready without implementation evidence and governed acceptance.

## 5. Phase Transition Rule

Before a product phase starts:

- the manifest must name the phase
- `next_product_phase_approval` must be `APPROVED`
- all five authority sources must contain the same approval block
- the Readiness Gate must pass
- the repository must be clean
- the dedicated Sidecar branch must be created from the approved baseline

After merge and validation:

- the manifest must move the phase to latest completed truth
- the current implementation phase must return to `NONE`
- the next product phase must return to `NOT_SELECTED` unless separately
  approved
- all five authority sources must receive an identical final synchronization
  block
- generated outputs must be restored and Git must be clean

## 6. Future Architecture Coverage Invariants

The canonical future architecture must preserve these accepted but
not-implemented capability groups:

- deterministic factors, targets, State-Sync, and multi-horizon isolation
- technical, fundamental, flow, breadth, and microstructure research
- Market Session Registry and same-time-of-day baselines
- A-share call-auction, late-session, and closing research
- entrusted-order ratio, volume ratio, turnover, and observable flow semantics
- sector, theme, industry-chain, macro, and cross-market transmission context
- controlled research candidates and read-only Operator UI actions
- offline adaptive research without automatic learning or promotion
- session-aware replay, calibration, lead-time, failure, and stop evaluation
- A-share and BTC market-specific adapters without a universal mixed score
- five-clock regime context and policy, industry, and capital transmission
- point-in-time institutional calendars and overlapping event-state handling
- expectation-gap, event-reaction, and earnings-lifecycle research
- futures-expiry, equity-supply, rates, FX, crowding, and holiday-liquidity
  research
- governed institutional-factor lifecycle and data-freshness controls
- named institutional-factor research candidates without early activation
- provider-neutral typed observations and provider-edge SDK isolation
- point-in-time availability, revision, corporate-action, adjustment, and
  trading-status lineage
- immutable layered local storage, cross-source reconciliation, quarantine,
  explicit source roles, and visible degraded routing
- rights-aware RQData, MiniQMT market-data, Tushare, AkShare, and BaoStock
  candidate treatment without provider selection or trial-data harvesting
- separate A-share and BTC source semantics and evidence-based data-cost value
  gates without profitability claims
- BTC perpetual Paper research with venue-versioned contract, collateral,
  margin, PnL, funding, liquidation, ADL, insurance-fund, lifecycle, cost,
  stress, and hard-gate semantics separated from reusable signal evidence
- registered Guojin QMT local daily-export normalization with exact source
  bytes, explicit instrument identity, ISO dates, 100-share lot conversion,
  additive front-adjustment reference evidence, visible range mismatch, and
  fail-closed factor, trading-status, entitlement, and point-in-time gaps
- registered QMT multi-batch coverage reconciliation with immutable batch order,
  exact expected trading-date evidence, identical-overlap deduplication,
  conflicting-overlap quarantine, row-cap visibility, and no natural-day
  trading-session inference
- registered A-share expected trading-date artifact profiles with exact local
  ASCII bytes, source revision, market, instrument, coverage, rights, retention,
  point-in-time availability lineage, explicit FCP-0036 compatibility, and no
  weekday or natural-day inference
- registered same-calendar A-share cross-source coverage reconciliation with
  explicit QMT and independent-reference roles, one instrument, source-specific
  date gaps, nested FCP-0021 quality evidence, immutable lineage, quarantine,
  and no source selection
- cross-source artifact-independence integrity with complete ordered digest
  sets bound into role hashes, disjoint-lineage proof, fail-closed overlap, and
  no claim that synthetic evidence closes provider-independence research
- same-calendar cross-source field-delta diagnostics with exact overlap-only
  numeric and clock summaries, explicit factor and status mismatches, immutable
  upstream lineage, mandatory Operator review, and no threshold, ranking,
  selection, or evidence replacement
- cross-source row-delta evidence ledgers with complete exact-match, delta, and
  incomplete entries in stable instrument, date, and closed-field order; bound
  to upstream coverage, artifact-independence, role, and diagnostic hashes
- cross-source Operator delta-review packets with closed per-field facts,
  affected dates, deterministic finding codes, mandatory review, and no
  severity, recommendation, threshold, ranking, selection, or replacement
- cross-source Operator delta-review receipts with safe review metadata, exact
  packet lineage, three closed non-decisional dispositions, and no evidence
  validation, rejection, source selection, replacement, or GAP closure
- cross-source Operator review-receipt ledgers with complete immutable receipt
  history, stable registered-time order, unique review and receipt identities,
  closed disposition counts, and no mutation, deletion, or decision authority
- BTC cross-source exact observation-delta ledgers with every ordered dataset
  pair, pairwise union key, closed observation field, exact source value,
  explicit incomplete state, and immutable upstream reconciliation lineage
- BTC perpetual venue contract-lifecycle registries with registered rule
  artifacts, exact settlement and precision semantics, half-open effective
  intervals, explicit migration targets, and fail-closed point-in-time lookup
- BTC perpetual margin risk-tier registries with exact FCP-0046 contract
  lineage, closed margin and position modes, contiguous exact tiers,
  collateral haircuts, half-open effective intervals, and fail-closed lookup
- BTC perpetual funding method-schedule registries with exact FCP-0046 contract
  lineage, closed method and basis, interval, anchor, signed bounds, payer
  convention, half-open effective intervals, and fail-closed lookup
- BTC perpetual fee-rebate schedule registries with exact FCP-0046 contract
  lineage, signed maker and taker rates, contiguous volume tiers, fee assets,
  half-open effective intervals, and no real account-tier selection
- registered Guojin QMT dual-export quality evidence with exact raw and
  front-adjusted artifact identity, ASCII schema, 100-share-lot consistency,
  raw/front parity, additive adjustment references, visible row-cap state, no
  raw repository bytes, and no completeness or factor-authority claim
- QMT historical coverage completeness gates with exact FCP-0050 lineage,
  requested-versus-observed boundary relations, closed positive-proof
  requirements, explicit supplement needs, and no inferred trading sessions
- QMT coverage-supplement lineage hardening with typed FCP-0037 and FCP-0036
  evidence, exact instrument, interval, calendar, pagination, point-in-time,
  and row-cap bindings, and no arbitrary digest proof
- BTC perpetual point-in-time rule-bundle coherence gates with exact FCP-0046
  through FCP-0049 registry hashes, shared contract-entry lineage, immutable
  rule snapshots, and no account-dependent calculation or execution authority
- BTC perpetual mark-index-liquidation mechanics registries with exact
  FCP-0046 lineage, partial-liquidation tiers, insurance-fund, ADL-ranking,
  cascade-state evidence, and no price, liquidation, or execution calculation
- BTC perpetual complete-rule-bundle coherence hardening with exact FCP-0053
  and FCP-0054 registry, contract-entry, artifact-time, and effective-time
  agreement before later Paper stress or risk-gate consumption
- BTC perpetual Paper stress-scenario definition registries with exact FCP-0055
  complete-rule lineage, closed scenario kinds, typed parameters, immutable
  artifacts, and no evaluation, account, or execution authority
- BTC perpetual Paper stress coverage and parameter-schema gates with exact
  FCP-0056 lineage, all eight closed kinds, exact parameter identifiers and
  units, immutable coverage hashes, and no evaluation or execution authority
- BTC perpetual Paper stress-evaluation input evidence registries with exact
  FCP-0057 lineage, one typed observation slot per closed scenario kind,
  point-in-time source lineage, and no evaluation or execution authority
- BTC perpetual Paper stress-input domain hardening with exact FCP-0058
  lineage, finite signed funding rates, metric-specific positive or nonnegative
  domains, immutable validation hashes, and no evaluation authority
- BTC perpetual Paper stress-evaluation readiness coherence gates with exact
  FCP-0055, FCP-0057, and FCP-0059 hash, venue, contract, scenario, and UTC
  lineage, immutable readiness evidence, and no evaluation authority
- BTC perpetual Paper stress-scenario parameter domain hardening with exact
  FCP-0056 and FCP-0057 lineage, signed funding shocks, bounded ratios,
  positive integral counts or seconds, immutable validation-only evidence,
  and no evaluation authority
- BTC perpetual Paper stress-readiness parameter-domain coherence hardening
  with exact FCP-0060 and FCP-0061 lineage, immutable extended-readiness
  evidence, and no direction, evaluation, or execution authority
- BTC perpetual Paper stress-evaluation operand-schema registries with exact
  FCP-0062 lineage, closed threshold-only or paired baseline-current operand
  requirements, and no direction, evaluation, or execution authority
- BTC perpetual Paper stress-evaluation operand-evidence registries with exact
  FCP-0063 lineage, one registered local observation per operand role,
  baseline-before-current time order, and no evaluation authority
- BTC perpetual Paper stress-evaluation context coherence gates with exact
  typed FCP-0056, FCP-0062, and FCP-0064 lineage, definition and contract
  coherence, monotonic UTC order, and no direction or evaluation authority
- BTC perpetual Paper stress-evaluation direction-semantics registries with
  exact typed FCP-0065 lineage, closed direction, comparison, operand-order,
  and equality policies, and no formula or evaluation authority
- BTC perpetual Paper stress-evaluation measure-formula semantics registries
  with exact typed FCP-0066 lineage, closed symbolic formula, operand,
  parameter, output-unit, transform, and denominator policies, and no
  evaluation or calculation authority
- BTC perpetual Paper stress-evaluation trigger-predicate semantics registries
  with exact typed FCP-0067 lineage, closed comparison, role-order, transform,
  and strict or inclusive boundary policies, and no evaluation authority
- BTC perpetual Paper stress-evaluation input-binding registries with exact
  typed FCP-0068, FCP-0064, and FCP-0056 lineage, ordered predicate, operand,
  and parameter hashes, and no evaluation or calculation authority
- BTC perpetual Paper deterministic stress-trigger evaluations with exact
  typed FCP-0069-bound lineage, Decimal formula execution, registered predicate
  boundaries, reviewed result evidence, and no account or execution authority
- BTC perpetual Paper stress trigger-result review registries with exact typed
  FCP-0070 and FCP-0056 lineage, scenario identity, version, severity, horizon,
  and trigger evidence, and no calculation, recommendation, or action authority
- BTC perpetual Paper stress trigger-result Operator review packets with exact
  typed FCP-0071 lineage, complete ordered record hashes, triggered and
  non-triggered evidence groups, and no disposition, recommendation, or action
  authority
- BTC perpetual Paper stress trigger-result Operator review receipts with
  exact typed FCP-0072 packet lineage, complete record-hash evidence, reviewer
  reference, reviewed UTC time, and no approval, resolution, or action authority
- BTC perpetual Paper signal-evidence separation contracts with one closed
  ordered domain vocabulary, immutable artifact references, reusable-signal
  isolation, and no signal, strategy, profitability, account, or action authority
- A-share external candidate daily-corpus quality quarantine evidence with a
  path-free manifest, closed quality findings, explicit provenance and rights
  gaps, raw data outside Git, and no evidence-promotion authority
- A-share candidate daily promotion-readiness gates with exact typed quality
  evidence, closed registered authority-reference domains, deterministic
  blockers, mandatory Operator review, and no promotion authority
- A-share trusted data supply-chain coverage evidence matrices with exact
  tracked component hashes, closed GAP-087 through GAP-093 requirements,
  visible missing capabilities, and no Gap-closure or data-authority claim

These groups remain future structure until their Gap entries are closed by
implementation evidence. A new chat, handoff, or historical record cannot
delete them, mark them completed, or select their implementation phase.

## 7. Permanent Boundary

P1-P47 remain frozen. No P48 is created. FCF remains paper-only, local-only,
loopback-only, sidecar-only, registered-artifact-only, and read-only in product
presentation. Deterministic Engine remains calculation authority. Registered
Evidence remains evidence authority. AI remains advisory. Operator review is
mandatory.

No broker, exchange, credential, account, balance, position, wallet, order,
real execution, tag, release, or deployment path is authorized.
