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

## Register Rules

- An ADR change requires explicit Operator approval and impact analysis.
- An accepted ADR is not evidence of implementation.
- Detailed implementation remains subject to the Readiness Gate.
- External reports and model recommendations remain advisory.
- P1-P47 remain frozen and no P48 is created.
