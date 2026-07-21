# FCF Future Capability Change Protocol

Status: ACTIVE_GOVERNANCE_CONTROL

This protocol keeps future product ideas durable without allowing an idea,
chat message, or intake record to authorize implementation.

## 1. Entry Point

Every new future capability starts in:

- `FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json`

Each proposal receives the next permanent `FCF-FCP-NNNN` identifier. Proposal
identifiers are never reused, reordered, or deleted.

The initial register preserves three non-authorizing research proposals for a
data entitlement and provenance control view, a counterfactual research
decision journal, and a correlated-evidence confidence budget. Their
`NEEDS_RESEARCH` status is not phase approval.

## 2. Required Proposal Fields

Every non-empty proposal record contains:

- `proposal_id`, `title`, `summary`, `source`, and `submitted_at_utc`
- `status` and `operator_decision`
- `architecture_refs`, `adr_refs`, `gap_refs`, and `evidence_refs`
- `phase_id` and `supersedes`

Human text may describe an idea. Identifiers, statuses, references, times, and
phase links remain machine-validated.

## 3. Status Lifecycle

Allowed statuses are:

- `PROPOSED`
- `NEEDS_RESEARCH`
- `ACCEPTED_ARCHITECTURE`
- `DEFERRED`
- `REJECTED`
- `OUTSIDE_CURRENT_AUTHORIZATION`
- `APPROVED_FOR_PHASE`
- `IMPLEMENTED`
- `SUPERSEDED`

`PROPOSED`, `NEEDS_RESEARCH`, and `ACCEPTED_ARCHITECTURE` do not authorize
implementation. `APPROVED_FOR_PHASE` requires an explicit Operator approval,
a named phase, Readiness Gate evidence, synchronized authority files, and an
approved manifest transition.

## 4. Review Flow

The governed flow is:

`intake -> duplicate check -> architecture impact -> safety and data review`
`-> Operator decision -> ADR and Gap linkage -> phase approval -> delivery`

Review must assess:

- business and user value
- affected market, asset class, horizon, and product surface
- required data fields, source rights, retention, latency, and cost
- deterministic formulas, targets, evidence, and failure behavior
- security, privacy, legal, regulatory, and execution-boundary impact
- dependency, migration, rollback, test, replay, and stop requirements
- overlap or conflict with accepted architecture and existing proposals

## 5. Preservation Rules

- A rejected, deferred, superseded, or implemented proposal remains recorded.
- Corrections append evidence or a superseding proposal; they do not erase the
  original decision history.
- ADR and Gap identifiers remain sequential and are never repurposed.
- Accepted architecture remains present until an explicit Operator-approved
  supersession is synchronized across current authorities.
- Chat memory, handoff prose, AI output, or a historical plan cannot delete or
  silently complete a proposal.

## 6. Implementation Gate

An intake record alone cannot:

- select the current phase
- change the manifest approval state
- activate a factor, score, model, Prompt, route, or learning process
- invoke a data source or external service
- create a Paper order, virtual account, or execution path

Implementation still requires the Control Center, current manifest, five
active authority sources, Readiness Gate, dedicated Sidecar, deterministic
tests, full validation, final synchronization, and a clean repository.

## 7. Permanent Boundary

P1-P47 remain frozen. No P48 is created. Paper-only, local-only,
loopback-only, sidecar-only, registered-artifact-only, read-only presentation,
Deterministic Engine calculation authority, Registered Evidence authority,
advisory AI, and mandatory Operator review remain binding.

No broker, exchange, credential, account, balance, position, wallet, order,
real execution, tag, release, or deployment capability is authorized.

## 8. Seven-File Governance System

The durable control suite is named the `FCF Seven-File Project Governance and
Memory System`. Its core files are the current-state manifest, Project Control
Center, canonical future architecture, ADR register, Gap and Backlog register,
this change protocol, and the Future Capability Intake Register.

Proposal `FCF-FCP-0004` registers the accepted architecture for institutional
calendar and causal market intelligence. It remains `phase_id: NONE` and
`NOT_IMPLEMENTED`. Its acceptance preserves the design and research backlog;
it does not approve data access, a runtime phase, automatic weighting, model
authority, or implementation.

The proposal preserves named research candidates for earnings surprise, event
reaction, expiry basis and roll, equity supply, FX transmission, institutional
crowding, quarter-end pressure, holiday liquidity, policy novelty, and capital
transmission. Candidate names and legacy aliases are not factor registration,
formula approval, or runtime activation.

Proposal `FCF-FCP-0005` registers a non-authorizing first-MVP market and product
readiness decision gate for `V2-FR-GAP-042` through `V2-FR-GAP-047`. The gate
compares registered target, stop, data-rights, unit-economics, commercial,
legal, and repository-license evidence without scoring, ranking, choosing a
winner, selecting a market, or authorizing a product phase. It remains
`NEEDS_RESEARCH`, `phase_id: NONE`, and `operator_decision: PENDING`.

Proposal `FCF-FCP-0016` registers the accepted trusted-data-supply-chain and
cost-aware-source-routing architecture. It extends FCP-0009 without replacing
its provider-neutral readiness contract. The proposal preserves typed canonical
records, point-in-time and revision lineage, corporate actions, trading status,
layered local storage, cross-source quarantine, explicit provider roles,
market-specific semantics, trial-rights discipline, and empirical after-cost
value gates.

FCP-0016 does not select RQData, MiniQMT, Tushare, AkShare, BaoStock, or another
provider. It does not authorize an SDK, network access, credentials, data
purchase, permanent trial-data retention, realtime activation, trading API,
product phase, or gap closure. MiniQMT market data and trading surfaces remain
process-isolated, and trading surfaces are prohibited in this repository.

Proposal `FCF-FCP-0034` registers the accepted, non-authorizing BTC perpetual
leverage Paper research architecture. It separates reusable signal evidence
from venue-versioned contract, collateral, position-mode, margin, PnL,
funding, liquidation, ADL, insurance-fund, cost, outage, lifecycle, and stress
evidence. It links ADR-034 and Gaps 039, 040, and 095 through 103.

FCP-0034 remains `phase_id: NONE` and `NOT_IMPLEMENTED`. It does not authorize
a leverage runtime, virtual account, Paper order, venue selection or adapter,
SDK, network, credential, wallet, account, balance, position, real order,
execution, realtime activation, product phase, P48, tag, release, or deploy.

Proposal `FCF-FCP-0035` registers the bounded Guojin QMT local daily-export
profile under the existing trusted-data-supply-chain architecture. It accepts
exact Operator-registered ASCII bytes, explicit instrument identity,
YYYYMMDD normalization, and 100-share lot conversion. It preserves requested
and actual coverage and treats QMT front-adjusted output as additive reference
evidence only.

FCP-0035 cannot derive a multiplicative adjustment factor, infer an instrument
from a filename, silently accept incomplete range coverage, or supply missing
point-in-time and trading-status evidence. It does not authorize MiniQMT SDK
invocation, network retrieval, credential, provider selection, raw repository
retention, realtime activation, trading API, product phase, P48, order,
execution, tag, release, or deployment.

Proposal `FCF-FCP-0036` registers deterministic reconciliation for multiple
exact Operator-registered Guojin QMT daily export batches. The bounded delivery
requires ordered batch lineage, an exact registered expected trading-date set,
identical-overlap deduplication, conflicting-overlap quarantine, missing and
unexpected date findings, declared-row-cap visibility, and deterministic merged
ASCII output compatible with FCP-0019.

FCP-0036 cannot infer sessions from natural days or weekdays, silently select a
duplicate, infer batch order from paths, acquire files, invoke an SDK, retrieve
network data, select a provider, retain raw files in the repository, activate
realtime, or authorize a product, account, order, or execution path.

Proposal `FCF-FCP-0037` registers a provider-neutral local profile for exact
Operator-registered A-share expected trading-date artifacts. It requires source
revision, market, instrument, declared range, rights, retention, and explicit
observed, available, registered, revision, and as-of lineage. Ordered unique ISO
dates are the only accepted expected set.

FCP-0037 cannot infer sessions from natural days or weekdays, scrape a calendar,
acquire files, invoke an SDK, retrieve network data, select a provider, retain
raw files in the repository, activate realtime, or authorize a product,
account, order, or execution path. Synthetic tests do not close GAP-107.

Proposal `FCF-FCP-0038` composes FCP-0021 and FCP-0037 into a local-only
same-calendar cross-source coverage packet. It requires distinct registered QMT
and independent-reference roles, one instrument, source-specific missing and
unexpected dates, nested deterministic quality findings, and immutable lineage.

FCP-0038 cannot acquire either dataset, infer roles, compare different calendar
authorities, select a source, activate realtime, or authorize a product,
account, order, or execution path. Synthetic tests do not close GAP-109.

Proposal `FCF-FCP-0039` hardens FCP-0038 by binding every source role to its
complete ordered registered source-artifact digest set and requiring disjoint
digest lineage across QMT and independent-reference roles.

FCP-0039 cannot prove corporate provider independence, acquire either source,
accept credentials, select a provider, activate realtime, or authorize a
product, account, order, or execution path. Synthetic tests do not close
GAP-109.

Proposal `FCF-FCP-0040` adds exact same-calendar field-delta diagnostics on top
of typed FCP-0038 coverage and FCP-0039 artifact-independence evidence. It
summarizes overlapping raw price, volume, amount, factor, status, and registered
clock differences with immutable lineage.

FCP-0040 cannot set a tolerance, rank or select a source, replace registered
evidence, acquire data, invoke an SDK, retrieve network data, accept credentials,
activate realtime, or authorize a product, account, order, or execution path.
Synthetic tests do not close GAP-109.

Proposal `FCF-FCP-0041` expands a typed FCP-0040 aggregate diagnostic into a
complete stable row-addressable evidence ledger. It preserves every exact
overlapping key and closed field, including matches and incomplete pairs, and
binds all upstream lineage into immutable hashes.

FCP-0041 cannot omit inconvenient rows, sort by desirability, set a tolerance,
rank or select a source, replace registered evidence, acquire data, invoke an
SDK, retrieve network data, accept credentials, activate realtime, or authorize
a product, account, order, or execution path. Synthetic tests do not close
GAP-109.

Proposal `FCF-FCP-0042` derives a deterministic Operator review packet from one
typed FCP-0041 ledger. It preserves complete per-field match, delta, incomplete,
and affected-date facts and emits only closed descriptive finding codes.

FCP-0042 cannot assign severity, recommend, set a tolerance, rank or select a
source, replace evidence, acquire data, invoke an SDK, retrieve network data,
accept credentials, activate realtime, or authorize a product, account, order,
or execution path. Synthetic tests do not close GAP-109.

Proposal `FCF-FCP-0043` records a deterministic local-only Operator review
receipt for one typed FCP-0042 packet. The receipt binds safe review identity,
reviewer reference, registered UTC time, one closed non-decisional disposition,
and exact packet, ledger, finding, and field-fact lineage.

FCP-0043 cannot validate or reject evidence, assign severity, recommend, set a
tolerance, rank or select a source, replace evidence, acquire data, invoke an
SDK, retrieve network data, accept credentials, activate realtime, authorize a
product, account, order, or execution path, or close GAP-109.

Proposal `FCF-FCP-0044` creates a deterministic local-only ledger from a
nonempty sequence of typed FCP-0043 receipts. It preserves every receipt in
stable registered-time and review-ID order, requires unique review IDs and
receipt hashes, and binds closed disposition counts and exact packet identities.

FCP-0044 cannot mutate or delete receipts, validate or reject evidence, assign
severity, recommend, set a tolerance, rank or select a source, replace evidence,
acquire data, invoke an SDK, retrieve network data, accept credentials, activate
realtime, authorize a product, account, order, or execution path, or close
GAP-109.
