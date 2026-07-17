# FCF Project Memory and Continuity Protocol

Status: ACTIVE_GOVERNANCE_CONTROL

This protocol makes repository evidence, rather than conversation memory, the
authority for resuming FCF work.

## 1. Required Read Order

A new development window must read and verify these sources in order:

1. `docs/FCF_EXECUTION_SAFETY_PROTOCOL.md`
2. `FCF_CURRENT_STATE_MANIFEST.json`
3. `docs/FCF_PROJECT_CONTROL_CENTER.md`
4. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md`
5. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md`
6. `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md`
7. the latest applicable `FCF_CURRENT_STATE_*_FINAL.md` evidence
8. the five active authority sources
9. branch, HEAD, origin reference, and Git status

No implementation may start from chat recollection alone.

## 2. File Roles

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

## 6. Permanent Boundary

P1-P47 remain frozen. No P48 is created. FCF remains paper-only, local-only,
loopback-only, sidecar-only, registered-artifact-only, and read-only in product
presentation. Deterministic Engine remains calculation authority. Registered
Evidence remains evidence authority. AI remains advisory. Operator review is
mandatory.

No broker, exchange, credential, account, balance, position, wallet, order,
real execution, tag, release, or deployment path is authorized.
