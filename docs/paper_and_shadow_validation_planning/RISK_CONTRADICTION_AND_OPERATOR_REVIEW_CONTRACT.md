# Risk, Contradiction, and Operator Review Contract

## Phase

PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1

## Delivery

D4 - Validation Result Packet, Risk, Contradiction, and Operator Review

## Status

PLANNING_ONLY

NO_RUNTIME_IMPLEMENTATION

NO_AUTOMATIC_DECISION

NO_AUTOMATIC_PROMOTION

## Purpose

This contract defines the future validation result packet, preserved risk and
contradiction evidence, review states, and Operator decision boundary.

It does not execute validation, invoke a model, approve a candidate, promote a
Champion, replace a baseline, activate learning, write an archive, or create a
trading action.

## Authority

The deterministic FCF engine remains the calculation and hard-policy
authority.

Registered evidence remains the factual support authority.

Registered risk flags and contradiction records remain mandatory evidence.

The Operator remains the final review and acceptance authority.

A validation coordinator may assemble a packet.

It may not approve, reject, promote, activate, archive, or execute on behalf of
the Operator.

## Validation result packet identity

Every future validation result packet must preserve:

- validation_packet_id
- validation_plan_id
- comparison_id
- baseline_id
- candidate_id
- evaluation_mode
- evaluation_window_id
- dataset_snapshot_id
- metric_registry_version
- Config Snapshot identifiers
- Prompt versions when applicable
- model registrations when applicable
- decision_cutoff_utc
- observation_cutoff_utc
- outcome_maturity_utc
- content_hashes
- correlation_id
- evidence_references
- metric_results
- guardrail_results
- segment_results
- sample_sufficiency_state
- data_quality_state
- risk_flags
- contradiction_records
- eligibility_state
- comparison_state
- review_state
- Operator decision state

Missing mandatory packet identity must fail visibly.

## Metric result preservation

Every metric result must preserve:

- metric_id
- metric_version
- observed_value
- baseline_value
- candidate_value
- comparison_delta
- direction_of_improvement
- tolerance
- guardrail_threshold
- blocking_threshold
- sample_count
- uncertainty_value
- segment_scope
- result_state
- evidence_references
- calculation_reference

A displayed summary must not replace the registered metric result.

An AI explanation must not modify a calculated value.

## Risk flag preservation

Every risk flag must preserve:

- risk_flag_id
- risk_code
- risk_category
- severity
- source_artifact_id
- detection_rule_id
- detected_at_utc
- affected_scope
- evidence_references
- blocking_effect
- acknowledgement_required
- resolution_state
- Operator disposition
- correlation_id

Risk flags must remain first-class packet content.

Risk flags must not be hidden inside prose-only summaries.

A candidate improvement must not delete, suppress, downgrade, or relabel a
mandatory risk flag.

A blocking risk flag must prevent ACCEPTED presentation until governed review
and disposition are complete.

## Contradiction preservation

Every contradiction record must preserve:

- contradiction_id
- contradiction_type
- source_a
- source_b
- conflicting_claims
- conflicting_values when applicable
- severity
- affected_metrics
- affected_segments
- evidence_references
- resolution_state
- Operator disposition
- correlation_id

Contradictions must remain visible even when aggregate metrics improve.

An unresolved blocking contradiction must prevent ACCEPTED status.

An AI synthesis must not erase disagreement between models, evidence sources,
deterministic results, or Operator policy.

## Failure and degradation classification

The packet must distinguish:

- INFORMATIONAL
- WARNING
- DEGRADED
- BLOCKING
- INVALIDATING

The packet state must distinguish:

- DRAFT
- ELIGIBILITY_CHECK
- READY_FOR_REVIEW
- REVIEW_REQUIRED
- ACCEPTED
- REJECTED
- RETURNED_FOR_REVISION
- BLOCKED
- DEGRADED
- INVALID
- CANCELLED

BLOCKED, DEGRADED, and INVALID must remain separate.

DEGRADED must not silently become ACCEPTED.

BLOCKED must not be presented as incomplete success.

INVALID must not enter promotion review.

## Operator review record

Every Operator review record must preserve:

- operator_review_id
- validation_packet_id
- reviewer_identity
- reviewer_role
- review_started_at_utc
- review_completed_at_utc
- reviewed_evidence_references
- reviewed_risk_flags
- reviewed_contradictions
- acknowledgement_records
- exception_records
- decision
- rationale
- conditions
- expiry or re-review requirement
- correlation_id
- immutable audit reference

Permitted Operator decisions are:

- ACCEPT
- REJECT
- RETURN_FOR_REVISION
- HOLD
- INVALIDATE

These decisions apply only to governed paper and shadow validation review.

They are not trading, allocation, order, portfolio, or execution instructions.

## Separation of review and promotion

Validation acceptance and Champion promotion remain separate governed actions.

An ACCEPT decision does not automatically:

- promote a Champion
- replace a baseline
- activate a model
- activate a Prompt
- activate a configuration
- change deterministic weights
- activate learning
- archive a packet
- authorize execution

Promotion requires a separately registered governance packet and explicit
Operator decision.

## Exception handling

Every exception must preserve:

- exception_id
- exception_type
- requested_scope
- requested_duration
- affected_guardrails
- affected_risk_flags
- affected_contradictions
- justification
- compensating_controls
- requester_identity
- Operator decision
- expiry
- immutable audit reference

An exception must not waive:

- P1-P47 frozen Core protection
- no P48
- paper-only
- read-only
- sidecar-only
- Operator review
- no real execution
- no broker or exchange connection
- no credential access
- no order placement

Exceptions must expire or require explicit re-review.

## AI explanation boundary

AI may:

- summarize registered metric results
- explain registered risk flags
- explain contradiction records
- compare registered evidence
- identify unresolved review questions

AI may not:

- calculate authoritative metrics
- alter a result
- remove a risk flag
- downgrade a severity
- resolve a contradiction automatically
- approve an exception
- approve a packet
- promote a candidate
- replace a baseline
- activate learning
- authorize execution

AI confidence is not Operator approval.

## Audit and traceability

The packet, evidence, risk flags, contradictions, review record, and final
decision must preserve the same correlation_id scope.

Broken correlation must produce CORRELATION_BROKEN or INVALID state.

Every review decision must point to immutable registered evidence.

Later evidence must not silently rewrite an earlier review record.

## Permanent prohibitions

D4 must not create:

- P1-P47 frozen Core mutation
- P48
- runtime validation execution
- model invocation
- Prompt execution
- automatic routing
- automatic approval
- automatic exception approval
- automatic Champion promotion
- automatic baseline replacement
- automatic configuration activation
- automatic learning activation
- automatic archive
- archive writing
- real trading
- real execution
- broker or exchange connectivity
- credential access
- wallet, balance, account, or position access
- order placement
- position sizing
- portfolio action
- tag
- release
- deployment

## D4 acceptance boundaries

D4 passes only when:

- validation packet identity is explicit
- metric results remain registered and immutable
- risk flags remain first-class evidence
- contradictions remain visible
- BLOCKED, DEGRADED, and INVALID remain distinct
- Operator review identity and rationale are mandatory
- exceptions are registered, limited, and expiring
- validation acceptance remains separate from promotion
- AI cannot approve, alter, suppress, promote, or activate
- correlation_id traceability remains mandatory
- automatic Champion promotion remains prohibited
- automatic learning activation remains prohibited
- no runtime implementation is created
- paper-only remains mandatory
- read-only remains mandatory
- sidecar-only remains mandatory
