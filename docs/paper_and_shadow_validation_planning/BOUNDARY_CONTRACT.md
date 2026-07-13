# Paper and Shadow Validation Planning Boundary Contract

## Phase

PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1

## Delivery

D1 - Paper Validation and Shadow Observation Boundary

## Status

PLANNING_ONLY

NO_RUNTIME_IMPLEMENTATION

NO_SHADOW_TRADING_RUNTIME

NO_MODEL_INVOCATION

## Purpose

This phase defines the governed architecture for paper validation and passive
shadow observation.

It does not create a live validation service, scheduler, market-data adapter,
model runtime, trading runtime, broker connection, exchange connection, or
order path.

## Authority hierarchy

The authority hierarchy remains:

1. Operator Policy
2. FCF Hard Policy
3. Deterministic Engine
4. Validated Data and Registered Evidence
5. Validation Coordinator
6. AI Models
7. External Narrative

The deterministic FCF engine remains the calculation and policy authority.

Registered artifacts remain the evidence authority.

The Operator remains the final review authority.

A validation result does not become an execution instruction.

A model comparison does not become an automatic governance decision.

## Paper validation boundary

Paper validation may evaluate registered artifacts using:

- historical replay
- fixed evaluation datasets
- frozen benchmark snapshots
- registered deterministic results
- registered controlled AI outputs
- preserved risk flags
- preserved contradictions
- approved evaluation baselines

Paper validation must remain reproducible, versioned, evidence-traceable, and
correlation-preserving.

Historical replay must not be presented as forward observation.

Historical performance must not be presented as guaranteed future performance.

## Shadow observation boundary

Shadow observation means passive forward observation without capital, account,
position, wallet, order, or execution authority.

Shadow observation may later compare registered predictions or research
outputs with subsequently registered outcomes.

Shadow observation must not:

- place or cancel an order
- simulate access to a real account
- read a real balance or position
- create a broker or exchange connection
- activate a model automatically
- promote a candidate automatically
- modify production weights automatically
- create an automatic portfolio action

This planning phase does not implement shadow observation runtime behavior.

## Historical replay and forward observation separation

Historical replay and forward observation require separate:

- dataset identifiers
- time boundaries
- evidence manifests
- evaluation runs
- result packets
- status labels
- correlation identifiers
- Operator review records

Data known after a historical decision timestamp must not enter that replay
unless it is explicitly labelled as post-event evidence.

Forward observation must not silently reuse future-known historical data.

## Deterministic benchmark authority

Benchmark definitions, metric calculations, eligibility gates, hard limits,
and comparison rules remain deterministic.

AI may explain a benchmark result.

AI may not:

- change a benchmark calculation
- suppress a failed metric
- remove a risk flag
- erase a contradiction
- change an eligibility result
- declare a candidate approved
- promote a Champion
- activate learning

## Baseline and candidate boundary

A baseline and candidate comparison must preserve:

- baseline identifier
- candidate identifier
- Schema version
- Config Snapshot
- Prompt version when applicable
- model registration when applicable
- dataset version
- evaluation-window definition
- content hashes
- metric definitions
- correlation_id
- evidence references
- risk flags
- contradiction records
- Operator decision

Comparison eligibility does not equal approval.

A better metric does not automatically authorize promotion.

## Registered artifact boundary

Only registered, versioned, and authorized artifacts may enter validation.

Missing, stale, corrupted, unregistered, incompatible, or correlation-broken
artifacts must not be silently accepted.

Source artifacts remain read-only.

Validation planning must not overwrite, delete, or mutate source evidence.

## Required states

The validation architecture must preserve at least:

- DRAFT
- ELIGIBILITY_CHECK
- READY
- RUNNING
- REVIEW_REQUIRED
- ACCEPTED
- REJECTED
- BLOCKED
- DEGRADED
- INVALID
- CANCELLED

No state may silently become ACCEPTED.

REVIEW_REQUIRED requires explicit Operator action.

BLOCKED, DEGRADED, and INVALID must remain visibly distinct.

## Operator review

Operator review remains mandatory for:

- benchmark acceptance
- candidate acceptance
- exception handling
- degraded evidence acceptance
- risk acknowledgement
- contradiction disposition
- baseline replacement
- Champion promotion
- learning activation

The Operator may reject, stop, or return a validation packet for revision.

No AI model or coordinator may approve on behalf of the Operator.

## Permanent prohibitions

This phase must not provide:

- P1-P47 frozen Core mutation
- P48 creation
- real trading
- real execution
- broker or exchange connectivity
- trading credential access
- wallet or private-key access
- balance or position access
- real order placement
- automatic position sizing
- automatic portfolio action
- automatic model selection
- automatic model switching
- automatic provider routing
- automatic Prompt execution
- automatic Champion promotion
- automatic baseline replacement
- automatic learning activation
- automatic approval
- automatic archive
- archive writing
- tag creation
- release creation
- deployment

## D1 acceptance boundaries

D1 passes only when:

- paper validation is explicitly separated from real execution
- historical replay is separated from forward observation
- deterministic benchmark authority is preserved
- registered artifacts are required
- correlation_id traceability is required
- Operator review is mandatory
- BLOCKED, DEGRADED, and INVALID remain explicit
- automatic Champion promotion is prohibited
- automatic learning activation is prohibited
- no runtime implementation is created
- paper-only remains mandatory
- read-only remains mandatory
- sidecar-only remains mandatory
- P1-P47 remain frozen
- P48 is not created
