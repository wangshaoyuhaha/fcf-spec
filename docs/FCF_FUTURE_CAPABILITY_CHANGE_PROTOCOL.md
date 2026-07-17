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
