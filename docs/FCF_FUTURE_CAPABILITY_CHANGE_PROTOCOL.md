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

Proposal `FCF-FCP-0045` creates deterministic local-only exact BTC observation
delta evidence from typed FCP-0023 datasets, policy, and result. It recomputes
the result, enumerates every registered dataset pair and pairwise union key,
and preserves closed exact fields, deltas, incomplete states, and lineage.

FCP-0045 cannot change a tolerance, severity, or quality state, rank or select
a venue or source, replace evidence, acquire data, invoke an SDK, retrieve
network data, accept credentials, activate realtime, authorize a wallet,
product, account, order, or execution path, or close GAP-092 or GAP-095.

Proposal `FCF-FCP-0046` creates a deterministic local-only venue-versioned BTC
perpetual contract and lifecycle registry from registered rule evidence. It
preserves settlement, assets, multiplier, precision, minimums, effective-time
intervals, lifecycle state, migration target, and exact artifact lineage.

FCP-0046 cannot calculate margin, liquidation, PnL, funding, or execution,
select a source, acquire data, invoke an SDK, retrieve network data, accept
credentials, activate realtime, authorize a wallet, product, account, order,
or execution path, or close GAP-096 or GAP-102.

Proposal `FCF-FCP-0047` creates a deterministic local-only BTC perpetual margin
and risk-tier evidence registry bound to exact FCP-0046 contract lineage. It
preserves margin and position modes, exact risk tiers, rates, deductions,
limits, collateral haircuts, and effective-time rule versions.

FCP-0047 cannot calculate balances, positions, margin amounts, PnL,
liquidation, funding, fees, or execution, select a source, acquire data, invoke
an SDK, retrieve network data, accept credentials, activate realtime,
authorize a wallet, product, account, order, or execution path, or close
GAP-097 or GAP-102.

Proposal `FCF-FCP-0048` creates a deterministic local-only BTC perpetual
funding-method and schedule evidence registry bound to exact FCP-0046 contract
lineage. It preserves method, basis, interval, anchor, signed rate bounds,
interest component, payer convention, and effective-time rule versions.

FCP-0048 cannot calculate a funding rate, payment, balance, position, PnL,
liquidation, fee, or execution, select a source, acquire data, invoke an SDK,
retrieve network data, accept credentials, activate realtime, authorize a
wallet, product, account, order, or execution path, or close GAP-099 or GAP-102.

Proposal `FCF-FCP-0049` creates a deterministic local-only BTC perpetual fee
and rebate schedule evidence registry bound to exact FCP-0046 contract lineage.
It preserves exact signed maker and taker rates, contiguous trailing-volume
tiers, measurement asset and window, fee assets, and effective-time versions.

FCP-0049 cannot select a real account tier or calculate fees, rebates,
balances, positions, PnL, liquidation, funding, or execution, select a source,
acquire data, invoke an SDK, retrieve network data, accept credentials,
activate realtime, authorize a wallet, product, account, order, or execution
path, or close GAP-099 or GAP-102.

Proposal `FCF-FCP-0050` creates deterministic local-only quality evidence from
one exact Operator-registered Guojin QMT raw and front-adjusted daily-export
pair. It preserves artifact identity, exact ASCII schema, row invariants,
100-share-lot consistency evidence, raw/front parity, additive adjustment
references, observed regime boundaries, row count, and visible row-cap state.

FCP-0050 cannot treat adjustment references as factor authority, infer missing
sessions, claim historical completeness, select a provider, acquire data,
invoke an SDK, retrieve network data, accept credentials, activate realtime,
authorize a broker, product, account, balance, position, order, or execution
path, or close GAP-104 through GAP-109. Actual raw bytes and local paths remain
outside the repository.

Proposal `FCF-FCP-0051` creates a deterministic local-only historical coverage
completeness gate bound to one exact FCP-0050 evidence record. It preserves
requested and observed interval relations, row-cap ambiguity, a closed
requirement matrix, exact upstream lineage, and explicit supplement needs.

FCP-0051 cannot infer expected trading sessions, treat one capped batch as
complete, invoke FCP-0036 without registered inputs, acquire data, invoke an
SDK, retrieve network data, accept credentials, select a provider, retain raw
provider bytes, activate realtime, authorize a broker, product, account,
balance, position, order, or execution path, or close GAP-105, GAP-107, or
GAP-108.

Proposal `FCF-FCP-0052` creates deterministic local-only lineage integrity
hardening for FCP-0051 supplements. It binds typed FCP-0037 calendar and
FCP-0036 multi-batch evidence with typed pagination, point-in-time, and
row-cap-resolution records before deriving supplement hashes and counts.

FCP-0052 cannot accept arbitrary digest proof, mix instruments, ranges,
calendars, or batch manifests, manufacture missing evidence, change the actual
blocked gate, acquire data, invoke an SDK, retrieve network data, accept
credentials, select a provider, retain raw provider bytes, activate realtime,
authorize a broker, product, account, balance, position, order, or execution
path, or close GAP-105, GAP-107, or GAP-108.

Proposal `FCF-FCP-0053` creates a deterministic local-only point-in-time
coherence gate over the exact FCP-0046 through FCP-0049 BTC perpetual rule
registries. It resolves one immutable evidence bundle only when registry,
venue, contract, contract-entry, and effective-time lineage agree.

FCP-0053 cannot calculate margin, leverage, liquidation, funding payments,
fees, rebates, balances, positions, PnL, orders, execution, or source
preference, acquire data, invoke an SDK, retrieve network data, accept
credentials, select a provider, activate realtime, authorize an exchange,
wallet, account, order, or execution path, or close GAP-096, GAP-097, GAP-099,
or GAP-102.

Proposal `FCF-FCP-0054` creates a deterministic local-only evidence registry
for BTC perpetual mark, index, bankruptcy, liquidation, partial-liquidation,
insurance-fund, ADL-ranking, and cascade-state rules bound to exact FCP-0046
contract lineage and half-open effective intervals.

FCP-0054 cannot calculate a price, margin, liquidation, funding, fee, balance,
position, PnL, ADL action, order, or execution, select a source or venue,
acquire data, invoke an SDK, retrieve network data, accept credentials,
activate realtime, authorize an exchange, wallet, account, order, or execution
path, or close GAP-098, GAP-100, GAP-101, or GAP-102.

Proposal `FCF-FCP-0055` hardens the deterministic local-only FCP-0053 rule
bundle with exact typed FCP-0054 liquidation-mechanics evidence. The gate
requires shared FCP-0046 registry and contract-entry lineage plus coherent
artifact registration and effective-time resolution.

FCP-0055 cannot calculate prices, margin, leverage, liquidation, funding,
fees, balances, positions, PnL, insurance-fund changes, ADL actions, orders,
execution, or source preference, acquire data, invoke an SDK, retrieve network
data, accept credentials, activate realtime, authorize an exchange, wallet,
account, order, or execution path, or close GAP-098, GAP-100, GAP-101, or
GAP-102.

Proposal `FCF-FCP-0056` creates a deterministic local-only BTC perpetual Paper
stress-scenario definition registry bound to one exact FCP-0055 complete
rule-bundle snapshot. It preserves closed kinds, exact parameters, severity,
horizon, artifact lineage, and immutable definition hashes.

FCP-0056 cannot evaluate stress, calculate prices, margin, leverage,
liquidation, funding, fees, balances, positions, PnL, ADL actions, orders,
execution, or source preference, acquire data, invoke an SDK, retrieve network
data, accept credentials, activate realtime, authorize an exchange, wallet,
account, order, or execution path, or close GAP-098, GAP-099, GAP-100, or
GAP-101.

Proposal `FCF-FCP-0059` hardens one exact FCP-0058 BTC perpetual Paper stress
input registry with metric-specific numeric domains. It permits finite signed
funding-reference rates while keeping price, depth, collateral, distance,
count, and time semantics fail-closed.

FCP-0059 cannot evaluate stress, calculate prices, margin, leverage,
liquidation, balances, positions, PnL, ADL actions, orders, execution, or
source preference, acquire data, invoke an SDK, retrieve network data, accept
credentials, activate realtime, authorize an exchange, wallet, account, order,
or execution path, or close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0060` creates a deterministic local-only readiness coherence
gate over exact typed FCP-0055 complete-rule, FCP-0057 coverage, and FCP-0059
input-domain snapshots. It requires exact hash, venue, contract, scenario, and
monotonic UTC agreement before later Paper evaluation consumption.

FCP-0060 cannot evaluate stress, calculate prices, margin, leverage,
liquidation, balances, positions, PnL, ADL actions, orders, execution, or
source preference, acquire data, invoke an SDK, retrieve network data, accept
credentials, activate realtime, authorize an exchange, wallet, account, order,
or execution path, or close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0061` hardens exact typed FCP-0056 stress-scenario parameters
against closed kind-specific numeric domains bound to exact FCP-0057 coverage.
It preserves signed funding shocks and validates ratios, counts, and seconds.

FCP-0061 cannot define direction, evaluate stress, calculate prices, margin,
leverage, liquidation, balances, positions, PnL, ADL, orders, execution, or
close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0062` hardens exact typed FCP-0060 readiness with exact
FCP-0061 scenario-parameter domain evidence. It requires exact shared hashes,
identity, scenario, definition, schema, and monotonic UTC lineage.

FCP-0062 cannot define direction, evaluate stress, calculate prices, margin,
leverage, liquidation, balances, positions, PnL, ADL, orders, execution, or
close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0063` registers the exact operand roles, metric identifiers,
and units needed by every closed BTC perpetual Paper stress scenario. It binds
one exact FCP-0062 extended-readiness snapshot and distinguishes threshold-only
from paired baseline-current evidence requirements.

FCP-0063 cannot define direction, evaluate stress, calculate prices, margin,
leverage, liquidation, balances, positions, PnL, ADL, orders, execution, or
close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0064` registers one typed local observation for every exact
FCP-0063 stress-evaluation operand role. It preserves metric, unit, venue,
contract, event, availability, source, digest, and rights lineage and requires
paired baselines to precede current observations.

FCP-0064 cannot define direction, evaluate stress, calculate prices, margin,
leverage, liquidation, balances, positions, PnL, ADL, orders, execution, or
close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0058` creates a deterministic local-only BTC perpetual Paper
stress-evaluation input evidence registry bound to one exact FCP-0057 coverage
snapshot. It requires one registered observation slot for every closed scenario
kind with exact metric, unit, time, availability, source, digest, and rights
lineage before any later stress calculation.

FCP-0058 cannot evaluate stress, calculate prices, margin, leverage,
liquidation, funding, fees, balances, positions, PnL, ADL actions, orders,
execution, or source preference, acquire data, invoke an SDK, retrieve network
data, accept credentials, activate realtime, authorize an exchange, wallet,
account, order, or execution path, or close GAP-098, GAP-099, GAP-100, or
GAP-101.

Proposal `FCF-FCP-0057` creates a deterministic local-only coverage and
parameter-schema gate over one exact FCP-0056 BTC perpetual Paper stress
registry. It requires all eight scenario kinds and closed parameter identifiers
and units before any later evaluator can consume the suite.

FCP-0057 cannot evaluate stress, calculate prices, margin, leverage,
liquidation, funding, fees, balances, positions, PnL, ADL actions, orders,
execution, or source preference, acquire data, invoke an SDK, retrieve network
data, accept credentials, activate realtime, authorize an exchange, wallet,
account, order, or execution path, or close GAP-098, GAP-099, GAP-100, or
GAP-101.

Proposal `FCF-FCP-0065` creates a deterministic local-only BTC perpetual Paper
stress-evaluation context coherence gate. It binds exact typed FCP-0056,
FCP-0062, and FCP-0064 evidence before any formula or evaluator is introduced.

FCP-0065 cannot define direction, register formulas, evaluate stress,
calculate prices, margin, leverage, liquidation, balances, positions, PnL,
ADL actions, orders, execution, or source preference, acquire data, invoke an
SDK, retrieve network data, accept credentials, activate realtime, authorize
an exchange, wallet, account, order, or execution path, or close GAP-098,
GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0066` creates a deterministic local-only BTC perpetual Paper
stress-evaluation direction-semantics registry bound to one exact typed
FCP-0065 evaluation context. It registers one closed direction, comparison
family, operand-role order, and equality policy for every scenario kind before
any formula or evaluator is introduced.

FCP-0066 cannot calculate thresholds, magnitudes, severities, prices, margin,
leverage, liquidation, balances, positions, PnL, ADL actions, orders,
execution, or source preference, acquire data, invoke an SDK, retrieve network
data, accept credentials, activate realtime, authorize an exchange, wallet,
account, order, or execution path, or close GAP-098, GAP-099, GAP-100, or
GAP-101.

Proposal `FCF-FCP-0067` creates a deterministic local-only BTC perpetual Paper
stress-evaluation measure-formula semantics registry bound to one exact typed
FCP-0066 direction registry. It registers closed symbolic formula, operand,
parameter, output-unit, transform, and denominator-policy bindings before any
evaluator is introduced.

FCP-0067 cannot evaluate observations or calculate thresholds, magnitudes,
severities, prices, margin, leverage, liquidation, balances, positions, PnL,
ADL actions, orders, execution, or source preference, acquire data, invoke an
SDK, retrieve network data, accept credentials, activate realtime, authorize
an exchange, wallet, account, order, or execution path, or close GAP-098,
GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0068` creates a deterministic local-only BTC perpetual Paper
stress-evaluation trigger-predicate semantics registry bound to one exact typed
FCP-0067 measure-formula registry. It registers closed comparison, role-order,
parameter-transform, and strict or inclusive boundary semantics before any
evaluator is introduced.

FCP-0068 cannot evaluate observations or calculate triggers, thresholds,
magnitudes, severities, prices, margin, leverage, liquidation, balances,
positions, PnL, ADL actions, orders, execution, or source preference, acquire
data, invoke an SDK, retrieve network data, accept credentials, activate
realtime, authorize an exchange, wallet, account, order, or execution path, or
close GAP-098, GAP-099, GAP-100, or GAP-101.

Proposal `FCF-FCP-0069` creates a deterministic local-only BTC perpetual Paper
stress-evaluation input-binding registry bound to exact typed FCP-0068,
FCP-0064, and FCP-0056 lineage. It registers ordered predicate, operand
observation, and scenario-parameter hashes per kind before evaluation.

FCP-0069 cannot evaluate observations or calculate measures, triggers,
thresholds, magnitudes, severities, account state, or execution results. It
does not close GAP-098 through GAP-101 or authorize acquisition, credentials,
realtime activation, product work, P48, account, execution, release, or deploy.

Proposal `FCF-FCP-0070` creates a deterministic local-only BTC perpetual Paper
stress trigger evaluator bound to exact typed FCP-0069, FCP-0068, FCP-0064,
and FCP-0056 evidence. It uses exact Decimal formulas and registered predicate
boundaries to emit reviewed measure-and-trigger evidence.

FCP-0070 cannot calculate or mutate margin, leverage, liquidation price,
balance, position, PnL, insurance fund, ADL, order, or execution state. It does
not close GAP-098 through GAP-101 or authorize product work, P48, release, or
deployment.

Proposal `FCF-FCP-0071` creates a deterministic local-only BTC perpetual Paper
stress trigger-result review registry bound to one exact typed FCP-0070
evaluation and its exact typed FCP-0056 scenario registry. It binds result
evidence to scenario identity, version, severity, horizon, and evaluation
lineage for mandatory Operator review without adding calculations.

FCP-0071 cannot recommend or perform account, margin, leverage, liquidation,
balance, position, PnL, insurance, ADL, order, or execution actions. It does
not close GAP-098 through GAP-101 or authorize product work, P48, release, or
deployment.

Proposal `FCF-FCP-0072` creates one deterministic local-only BTC perpetual
Paper stress trigger-result Operator review packet bound to one exact typed
FCP-0071 review registry. It preserves all eight ordered record hashes and
exact triggered and non-triggered evidence groups for mandatory review.

FCP-0072 cannot assign a disposition, approve, reject, recommend, or perform
account, margin, leverage, liquidation, balance, position, PnL, insurance,
ADL, order, or execution actions. It does not close GAP-098 through GAP-101 or
authorize product work, P48, release, or deployment.

Proposal `FCF-FCP-0073` registers one deterministic local-only explicit
Operator review receipt against one exact typed FCP-0072 packet. It preserves
complete packet lineage, reviewer reference, reviewed UTC time, and one closed
non-authorizing review disposition.

FCP-0073 cannot approve or reject evidence, resolve a result, recommend, or
perform account, margin, leverage, liquidation, balance, position, PnL,
insurance, ADL, order, or execution actions. It does not close GAP-098 through
GAP-101 or authorize product work, P48, release, or deployment.

Proposal `FCF-FCP-0074` registers one deterministic local-only BTC perpetual
Paper signal-evidence separation contract. It separates reusable market signal
evidence from contract semantics, leverage and margin, cost and funding,
liquidation risk, and outcome accounting through one closed ordered domain set.

FCP-0074 cannot calculate a signal, promote a factor, select a strategy, infer
profitability, or close GAP-103. It authorizes no acquisition, SDK, network,
credentials, realtime, product work, P48, exchange, wallet, account, margin,
leverage, liquidation, balance, position, PnL, order, execution, release, or
deployment.

Proposal `FCF-FCP-0075` registers deterministic local-only quality and
quarantine evidence for one external candidate A-share daily CSV corpus. It
preserves a path-free manifest fingerprint, schema, coverage, structural and
value-quality findings, adjustment ambiguity, provenance gaps, and rights risk
without retaining raw rows in Git.

FCP-0075 cannot establish provider authority, accuracy, completeness, official
adjustment factors, corporate actions, trading status, point-in-time
availability, or Registered Evidence authority. It authorizes no acquisition,
SDK, network, credentials, realtime, product work, P48, broker, exchange,
account, order, execution, release, or deployment.

Proposal `FCF-FCP-0076` registers one deterministic local-only A-share
candidate daily promotion-readiness gate. It binds exact typed FCP-0075 quality
quarantine evidence to a closed registered authority-reference domain set and
emits exact blockers and readiness for mandatory Operator review.

FCP-0076 cannot promote candidate data, establish source or rights authority,
calculate factors, create labels, select a provider, access an SDK, use
credentials, activate realtime data, or close GAP-023 or GAP-087 through
GAP-093. It authorizes no product work, P48, broker, exchange, account, order,
execution, release, or deployment.

Proposal `FCF-FCP-0077` creates one deterministic local-only A-share trusted
data supply-chain coverage evidence matrix. It binds exact tracked component
SHA-256 identities to closed requirements for GAP-087 through GAP-093 and
separates foundation coverage from external authority evidence.

FCP-0077 cannot change or close a Gap, establish data authority, promote
candidate rows, select a provider, access an SDK, use credentials, activate
realtime data, calculate factors, create labels, or authorize product work,
P48, broker, exchange, account, order, execution, release, or deployment.

Proposal `FCF-FCP-0078` defines one deterministic local-only A-share
publication and availability clock contract. It preserves timestamp precision,
legal availability, retrieval, ingest, first-tradable, revision, predecessor
lineage, and fail-closed point-in-time selection.

FCP-0078 cannot infer source publication time, close GAP-088, establish data
authority, promote candidate rows, select a provider, access an SDK, use
credentials, activate realtime data, calculate factors, create labels, or
authorize product work, P48, broker, exchange, account, order, execution,
release, or deployment.

Proposal `FCF-FCP-0079` defines one deterministic local-only A-share
corporate-action and price-query-policy lineage contract. It preserves action
revisions, source digests, exact adjustment-factor revisions, RAW and
FORWARD_ADJUSTED policies, and fail-closed point-in-time resolution.

FCP-0079 cannot invent official corporate actions or adjustment factors, close
GAP-089, establish data authority, overwrite source prices, promote candidate
rows, select a provider, access an SDK, use credentials, activate realtime
data, calculate factors, create labels, or authorize product work, P48,
broker, exchange, account, order, execution, release, or deployment.

Proposal `FCF-FCP-0080` defines deterministic local-only Tushare, AkShare, and
BaoStock candidate compatibility profiles. It preserves explicit artifact
schema, canonical mapping, units, clocks, adjustment state, rights state, and
fail-closed blockers without provider invocation.

FCP-0080 cannot install or invoke an SDK, access a network, use credentials,
select or endorse a provider, infer missing semantics, close GAP-093,
establish data or rights authority, promote candidate rows, calculate factors,
create labels, or authorize product work, P48, broker, exchange, account,
order, execution, release, or deployment.

Proposal `FCF-FCP-0081` defines a deterministic local-only incremental
after-cost data-value experiment contract for A-share candidate providers. It
preserves exact baseline and candidate evidence, common windows, quality,
rights, retention, fixed cost, measured benefit, renewal, and stop evidence.

FCP-0081 keeps current authorized spend at zero. It cannot acquire data, invoke
an SDK or network, use credentials, select, endorse, purchase, renew, or cancel
a provider, infer missing observations, claim alpha or profitability, close
GAP-094, establish data authority, promote rows, calculate production factors,
create labels, or authorize product work, P48, broker, exchange, account,
order, execution, release, or deployment.
## FCP-0082 MiniQMT Entitlement Evidence Change Rule

Proposal `FCF-FCP-0082` is limited to deterministic local validation of exact
sanitized Guojin MiniQMT Python market-data entitlement and sidecar
compatibility evidence. The approved implementation may add immutable
contracts, a fail-closed evaluator, non-authorizing Operator review packets,
guards, tests, and closeout evidence.

It cannot ingest account identifiers or secrets, invoke MiniQMT or xtquant,
use a network, establish entitlement or Registered Evidence authority,
activate realtime data, select a provider, promote data, close Gap
V2-FR-GAP-104, start product work, create P48, or enable trading or execution.
## FCP-0083 MiniQMT Local Evidence Runner Change Rule

Proposal `FCF-FCP-0083` may add one read-only local runner, canonical output,
tests, guard, and closeout evidence over the exact FCP-0082 contract. Source
bytes remain outside Git and are neither copied nor changed.

The phase cannot invoke MiniQMT or xtquant, use a network, accept accounts or
credentials, establish entitlement or Registered Evidence authority, activate
realtime data, select a provider, promote data, close GAP-104, start product
work, create P48, or enable trading or execution.
## FCP-0084 QMT Local Export Coverage Evidence Change Rule

Proposal `FCF-FCP-0084` may add immutable sanitized export-batch contracts, a
bounded read-only local scanner, deterministic coverage topology, tests,
guard, and closeout evidence. Raw rows and local paths remain outside Git.

Implementation must delegate registered-byte parsing and normalization to
FCP-0035. It must not duplicate or bypass FCP-0036 expected-date reconciliation.

The phase cannot invoke MiniQMT or xtquant, use a network or credentials,
infer requested parameters, calendars, pagination, official row caps,
completeness, adjustment authority, or trading status, promote data, close
GAP-105, start product work, create P48, or enable trading or execution.
## FCP-0085 BTC Registered Local Export Runner Change Rule

Proposal `FCF-FCP-0085` may add one bounded read-only local runner, sanitized
aggregate output, tests, guard, and closeout evidence over frozen FCP-0022.
Source and canonical rows remain outside Git and are neither copied nor
changed.

The phase cannot duplicate FCP-0022 parsing or typed contracts, invoke an SDK
or network, use credentials, select a venue or provider, activate realtime,
promote evidence, calculate a signal, strategy, account, position, margin,
leverage, PnL, liquidation, order, or execution, close GAP-095, start product
work, create P48, tag, release, or deploy.
## FCP-0086 BTC Local Export Operator Review Packet Change Rule

Proposal `FCF-FCP-0086` may add one immutable packet contract, deterministic
builder, canonical renderer, tests, guard, and closeout evidence over the exact
typed FCP-0085 validation result.

The phase cannot duplicate FCP-0085 validation, disclose values or paths,
assign a disposition, approve or reject evidence, invoke an SDK or network,
use credentials, select a venue or provider, activate realtime or replay,
promote evidence, calculate a signal or trade, close GAP-095, start product
work, create P48, tag, release, or deploy.
## FCP-0087 BTC Local Export Operator Review Receipt Change Rule

Proposal `FCF-FCP-0087` may add one immutable receipt contract, canonical
renderer, tests, guard, and closeout evidence over an exact typed FCP-0086
packet.

The phase cannot duplicate packet construction, disclose values or paths,
approve or reject evidence, resolve findings, invoke an SDK or network, use
credentials, select a venue or provider, activate realtime or replay, promote
evidence, calculate a signal or trade, close GAP-095, start product work,
create P48, tag, release, or deploy.
## FCP-0089 QMT Local Runtime Footprint Readiness Change Rule

Proposal `FCF-FCP-0089` may add immutable path-free filesystem-footprint
contracts, a bounded non-recursive metadata scanner, canonical renderer,
tests, guard, and closeout evidence over one Operator-designated local Guojin
QMT `userdata_mini` directory.

The phase cannot read file contents, recurse into data, log, user, or account
directories, disclose paths or arbitrary entry names, invoke MiniQMT or
xtquant, inspect processes or accounts, use a network or credentials,
establish entitlement or availability, promote data, select a provider,
activate realtime, close GAP-104, start product work, create P48, tag, release,
or deploy.
## FCP-0090 QMT Local Terminal Liveness Change Rule

Proposal `FCF-FCP-0090` may add immutable path-free liveness contracts, a
local allowlisted process observer, canonical renderer, tests, guard, and
closeout evidence. It may inspect process names in memory only and must
discard every unregistered name immediately.

The phase cannot retain arbitrary process names, identifiers, owners,
sessions, command lines, executable paths, windows, account identifiers,
credentials, or market values; invoke MiniQMT or xtquant; use a network;
establish entitlement, rights, retention, or market-data availability; promote
data; select a provider; activate realtime; close GAP-104; start product work;
create P48; tag, release, or deploy.
## FCP-0091 QMT Local-Cache Loopback Probe Change Rule

Proposal `FCF-FCP-0091` may add immutable value-free probe contracts, an
injected evaluator, one FCP-0090-gated runtime adapter, canonical renderer,
tests, guard, and closeout evidence. Only `xtquant.xtdata.get_local_data` may be
called, once, with the exact registered local-cache request.

The phase cannot retain returned timestamps or market values, subscribe,
download, enable server retrieval, retry, use account or trading APIs, use
credentials, establish entitlement or rights, select a provider, activate
realtime, promote data, close GAP-104, start product work, create P48, tag,
release, or deploy.
## FCP-0092 QMT Probe Operator Review Packet Change Rule

Proposal `FCF-FCP-0092` may add immutable registered-evidence reference,
review-item, review-packet, deterministic builder, canonical renderer, tests,
guard, and closeout evidence over the exact FCP-0091 NOT_RUN evidence.

The phase cannot assign an Operator disposition, invoke an SDK or network,
use credentials, account or trading APIs, retain paths or market values,
accept or promote data, select a provider, activate realtime, close GAP-104,
start product work, create P48, tag, release, or deploy.

## FCP-0093 BTC Coin Metrics Reference-Rate CSV Validation Change Rule

Proposal `FCF-FCP-0093` may add one bounded local validator, immutable typed
registration and result contracts, canonical value-free rendering, tests,
guard, and closeout evidence over one exact Operator-registered Coin Metrics
Community `asset,time,ReferenceRateUSD` CSV.

The phase cannot invoke an SDK or network, use credentials, retain source rows,
values, or paths, select a provider or venue, activate realtime, promote data,
convert the neutral reference rate into mark or index authority, calculate a
signal or trade, close GAP-095, start product work, create P48, or authorize a
wallet, account, balance, margin, leverage, position, PnL, liquidation, order,
execution, tag, release, or deployment.

## FCP-0094 BTC Coin Metrics Reference-Rate Review Packet Change Rule

Proposal `FCF-FCP-0094` may add immutable review-item and review-packet
contracts, a deterministic builder, canonical renderer, tests, guard, and
closeout evidence over one exact typed FCP-0093 validation result.

The phase cannot assign an Operator disposition, approve or reject evidence,
invoke an SDK or network, use credentials, retain source values or paths,
select a provider or venue, activate realtime, promote data, grant mark or
index authority, calculate a signal or trade, close GAP-095, start product
work, create P48, or authorize a wallet, account, balance, margin, leverage,
position, PnL, liquidation, order, execution, tag, release, or deployment.

## FCP-0095 A-Share QMT Local Export Continuity Routing Change Rule

Proposal `FCF-FCP-0095` may add immutable runtime-evidence and continuity-route
contracts, a deterministic builder, canonical renderer, tests, guard, and
closeout evidence over the exact registered FCP-0090 and FCP-0091 runtime
observations.

The phase cannot repeat the SDK call, use a network or credentials, select or
endorse a provider, promote data, claim completeness, activate realtime,
change gap status, start product work, create P48, or authorize broker,
exchange, account, balance, position, order, execution, tag, release, or
deployment.

## FCP-0096 Registered Factor Registry Runtime Change Rule

Proposal `FCF-FCP-0096` may add immutable artifact, factor-record, and runtime
snapshot contracts, one bounded ASCII JSON loader, deterministic dependency
and retirement invalidation resolution, canonical reference rendering, tests,
guard, and closeout evidence.

The phase cannot calculate or score factors, promote candidates, assign an
Operator decision, change an authoritative Gap status, mutate P1-P47, create
P48, invoke a provider or network, use credentials, or authorize account,
balance, position, wallet, order, execution, tag, release, or deployment.

## FCP-0097 Registered Target Label Registry Runtime Change Rule

Proposal `FCF-FCP-0097` may add immutable artifact, label-definition, and
runtime snapshot contracts, one bounded ASCII JSON loader, deterministic
bidirectional target-label lineage, canonical reference rendering, tests,
guard, and closeout evidence.

The phase cannot select a target or benchmark, materialize labels, calculate
outcomes, score or promote candidates, assign an Operator decision, change an
authoritative Gap status, mutate P1-P47, create P48, invoke a provider or
network, use credentials, or authorize account, balance, position, wallet,
order, execution, tag, release, or deployment.

## FCP-0098 Registered State-Sync Lock Runtime Change Rule

Proposal `FCF-FCP-0098` may add immutable artifact and lock snapshot
contracts, one bounded ASCII JSON loader, sequence, expiry and supersession
resolution, canonical rendering, tests, guard, and closeout evidence.

The phase cannot mutate state, ingest external data, calculate or score,
change a Gap status, mutate P1-P47, create P48, use credentials, or authorize
account, balance, position, wallet, order, execution, tag, release, or
deployment.

## FCP-0099 Registered Macro-to-Micro Transmission Runtime Change Rule

Proposal `FCF-FCP-0099` may add immutable artifact, transmission-record, and
snapshot contracts, one bounded ASCII JSON loader, official-chain and
evidence-lineage validation, lifecycle resolution, canonical rendering,
tests, guard, and closeout evidence.

The phase cannot calculate factors, claim causal truth, score, recommend,
change a Gap status, mutate P1-P47, create P48, use credentials, or authorize
account, balance, position, wallet, order, execution, tag, release, or
deployment.

## FCP-0100 Registered Multi-Horizon Conflict Resolver Runtime Change Rule

Proposal `FCF-FCP-0100` may add immutable artifact, horizon-result,
conflict-set, grouped-result, and presentation snapshot contracts, one bounded
ASCII JSON loader, deterministic conflict grouping, canonical rendering,
tests, guard, and closeout evidence.

The phase cannot mix horizons into one score, collapse conflict into
consensus, calculate signals, recommend, change a Gap status, mutate P1-P47,
create P48, use credentials, or authorize account, balance, position, wallet,
order, execution, tag, release, or deployment.
## FCP-0088 QMT Dual Export And Offline SDK Compatibility Change Rule

Proposal `FCF-FCP-0088` may add immutable path-free compatibility contracts, a
deterministic builder and renderer, tests, guard, and closeout evidence over
exact typed FCP-0035 and FCP-0084 results plus an explicit offline SDK ABI load
observation.

The phase cannot connect to MiniQMT, invoke market-data functions, use a
network or credentials, disclose rows, values, or paths, establish entitlement
or rights, infer expected sessions, pagination, completeness, adjustment-factor
authority, trading status, or point-in-time supplements, promote data, select a
provider, activate realtime, close GAP-104 through GAP-106, start product work,
create P48, tag, release, or deploy.
