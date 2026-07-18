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
