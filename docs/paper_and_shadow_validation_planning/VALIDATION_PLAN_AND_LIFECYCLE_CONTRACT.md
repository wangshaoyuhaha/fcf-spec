# Validation Plan and Lifecycle Contract

## Phase

PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1

## Delivery

D5 - Validation Plan Packet, Lifecycle, Stop Conditions, and Controlled Handoff

## Status

PLANNING_ONLY

NO_RUNTIME_IMPLEMENTATION

NO_SCHEDULER

NO_BACKGROUND_WORKER

NO_AUTOMATIC_STATE_TRANSITION

## Purpose

This contract defines the future paper and shadow validation plan packet,
governed lifecycle, entry gates, stop conditions, restart rules, and controlled
handoff boundaries.

It does not start validation, schedule observation, fetch data, invoke a model,
run a worker, bind a port, write an archive, promote a candidate, or execute a
trade.

## Authority

The deterministic FCF engine remains the calculation and hard-policy
authority.

Registered artifacts remain the evidence authority.

Registered validation contracts remain the lifecycle-rule authority.

The Operator remains the final plan approval and review authority.

A plan packet is not an execution command.

A plan approval is not validation execution.

A completed validation review is not Champion promotion.

## Validation plan packet

Every future validation plan packet must preserve:

- validation_plan_id
- plan_version
- plan_status
- evaluation_mode
- research_scope
- baseline_id
- candidate_id
- comparison_id
- evaluation_window_id
- dataset_snapshot_id
- registered_input_manifest_id
- metric_registry_version
- metric_definition_versions
- primary_metrics
- blocking_guardrails
- required_segments
- sample_sufficiency_rules
- leakage_control_rules
- Config Snapshot identifiers
- Prompt versions when applicable
- model registrations when applicable
- decision_cutoff_utc
- observation_cutoff_utc
- outcome_maturity_utc
- evidence_references
- risk_flags
- contradiction_records
- correlation_id
- Operator review requirement
- immutable audit reference

Missing mandatory plan identity must produce INVALID or BLOCKED state.

## Evaluation modes

The plan must explicitly declare one evaluation mode:

- HISTORICAL_REPLAY
- FORWARD_OBSERVATION

A plan must not silently change evaluation mode.

Historical replay and forward observation require separate plan identifiers,
windows, evidence manifests, result packets, and review records.

## Lifecycle states

The validation plan lifecycle must distinguish:

- DRAFT
- ELIGIBILITY_CHECK
- BLOCKED
- DEGRADED
- INVALID
- READY_FOR_OPERATOR_REVIEW
- APPROVED_FOR_PAPER_VALIDATION
- APPROVED_FOR_FORWARD_OBSERVATION
- REJECTED
- RETURNED_FOR_REVISION
- HOLD
- CANCELLED
- EXPIRED
- CLOSED

These are governance and planning states only.

They are not runtime execution states.

No state transition may occur silently.

No AI model, coordinator, scheduler, or worker may approve a transition.

## Entry gates

A plan may reach READY_FOR_OPERATOR_REVIEW only when:

- all required artifacts are registered
- content hashes are valid
- correlation_id values are consistent
- evidence references resolve
- Schema versions are supported
- Config Snapshots are present
- required Prompt and model registrations are present
- evaluation windows are complete
- leakage-control checks pass
- metric definitions are registered
- blocking guardrails are defined
- required segments are defined
- sample sufficiency rules are defined
- risk flags remain visible
- contradictions remain visible
- no invalidating condition exists

An entry-gate failure must remain visible.

## Operator plan approval

Operator approval must preserve:

- operator_plan_review_id
- validation_plan_id
- reviewer_identity
- reviewer_role
- reviewed_at_utc
- reviewed_evidence_references
- reviewed_risk_flags
- reviewed_contradictions
- decision
- rationale
- conditions
- expiry
- correlation_id
- immutable audit reference

Permitted plan decisions are:

- APPROVE_PAPER_VALIDATION_PLAN
- APPROVE_FORWARD_OBSERVATION_PLAN
- REJECT_PLAN
- RETURN_PLAN_FOR_REVISION
- HOLD_PLAN
- INVALIDATE_PLAN

Plan approval does not start a runtime.

Plan approval does not invoke a model.

Plan approval does not start data collection.

Plan approval does not authorize real execution.

## Stop conditions

A future validation activity must stop or remain blocked when:

- correlation_id integrity fails
- a content hash mismatches
- a required artifact becomes unavailable
- evidence references break
- leakage risk is detected
- an unsupported Schema appears
- a Config Snapshot is missing
- a required model registration is missing
- a required Prompt version is missing
- a blocking guardrail fails
- sample sufficiency becomes invalid
- a mandatory segment is missing
- a blocking risk flag is unresolved
- a blocking contradiction is unresolved
- Operator approval expires
- Operator cancellation is recorded
- plan identity changes after approval

A stop condition must not be converted into successful completion.

## Cancellation and expiry

Cancellation must preserve:

- cancellation_id
- validation_plan_id
- cancellation_reason
- cancellation_scope
- requester_identity
- Operator decision
- cancelled_at_utc
- correlation_id
- immutable audit reference

Expired approval must not silently renew.

Cancelled plans must not silently resume.

CLOSED plans must not silently reopen.

## Revision and restart

A revised plan must receive:

- a new plan version
- updated content hashes
- updated evidence references
- updated risk and contradiction records
- a new eligibility check
- a new Operator review
- preserved prior audit history

A restart must not overwrite the earlier plan, review, or result packet.

A changed baseline, candidate, dataset, window, metric, Config Snapshot, Prompt,
model registration, or guardrail requires explicit compatibility review.

## Idempotency and duplicate prevention

The architecture must preserve:

- plan idempotency key
- packet content hash
- correlation_id
- version identity
- duplicate detection result
- duplicate disposition

The same plan packet must not create duplicate validation records.

A retry must not create duplicate approval, result, promotion, learning, or
archive actions.

## Controlled handoff

A future approved plan may be handed off only to separately approved,
registered, and bounded implementation components.

The handoff packet must preserve:

- handoff_id
- source_validation_plan_id
- source_plan_version
- approved_evaluation_mode
- approved_scope
- permitted_artifact_inputs
- prohibited_capabilities
- stop_conditions
- Operator approval reference
- correlation_id
- immutable audit reference

A handoff packet must not contain:

- broker credentials
- exchange credentials
- wallet credentials
- account identifiers
- balance data
- position data
- order instructions
- allocation instructions
- execution instructions
- automatic promotion instructions
- automatic learning instructions

## Runtime separation

D5 does not create:

- a scheduler
- a queue
- a worker
- a listener
- a daemon
- a web server
- an API endpoint
- a network port
- a data feed
- a model runtime
- a Prompt runtime
- an observation runtime
- a validation runtime
- an archive writer

Any future runtime requires a separate explicit phase and approval.

## Promotion and learning separation

Validation plan approval and validation review do not authorize:

- automatic Champion promotion
- automatic baseline replacement
- automatic model activation
- automatic Prompt activation
- automatic configuration activation
- automatic weight change
- automatic learning activation
- automatic archive
- automatic deployment
- real execution

Each such capability remains separately governed or permanently prohibited.

## Permanent prohibitions

D5 must not create:

- P1-P47 frozen Core mutation
- P48
- real trading
- real execution
- broker or exchange connectivity
- credential access
- wallet, account, balance, or position access
- order placement
- position sizing
- portfolio action
- model invocation
- Prompt execution
- automatic routing
- automatic state transition
- automatic approval
- automatic exception approval
- automatic Champion promotion
- automatic baseline replacement
- automatic learning activation
- automatic archive
- archive writing
- tag
- release
- deployment

## D5 acceptance boundaries

D5 passes only when:

- validation plan identity is explicit
- historical replay and forward observation remain separate
- lifecycle states are governed and non-automatic
- entry gates are deterministic and visible
- Operator approval remains mandatory
- stop conditions remain blocking
- cancelled and expired plans cannot silently resume
- revisions preserve prior audit evidence
- duplicate plan actions are prevented
- controlled handoff preserves scope and prohibitions
- no scheduler, queue, worker, listener, API, or runtime is created
- automatic Champion promotion remains prohibited
- automatic learning activation remains prohibited
- no real execution capability is created
- paper-only remains mandatory
- read-only remains mandatory
- sidecar-only remains mandatory
