# Metric and Comparison Contract

## Phase

PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1

## Delivery

D3 - Deterministic Metric Registry and Baseline Candidate Comparison

## Status

PLANNING_ONLY

NO_RUNTIME_IMPLEMENTATION

NO_AUTOMATIC_PROMOTION

NO_AUTOMATIC_LEARNING

## Purpose

This contract defines how future paper and shadow validation metrics,
comparison packets, sample sufficiency, and result states must be registered.

It does not calculate live metrics, execute a workflow, invoke a model,
promote a candidate, replace a baseline, or activate learning.

## Authority

The deterministic FCF engine remains the metric calculation authority.

Registered metric definitions remain the comparison-rule authority.

Registered artifacts remain the evidence authority.

The Operator remains the final acceptance authority.

An AI explanation may describe a result.

An AI explanation may not calculate, modify, suppress, override, approve, or
promote a result.

## Metric registry

Every metric must be registered before use.

A metric registration must preserve:

- metric_id
- metric_name
- metric_version
- metric_family
- metric_definition
- calculation_method
- input_field_requirements
- missing_value_policy
- denominator_policy
- aggregation_method
- direction_of_improvement
- minimum_sample_size
- evaluation_window_requirement
- segment_scope
- tolerance
- guardrail_threshold
- blocking_threshold
- confidence_method
- deterministic_implementation_reference
- Schema version
- content_hash
- registered_at_utc
- correlation_id
- Operator review requirement

An unregistered metric must not enter an accepted comparison packet.

A metric name alone is not a complete metric definition.

## Metric families

The architecture may register metric families such as:

- coverage
- eligibility
- data quality
- classification quality
- ranking quality
- calibration
- stability
- contradiction rate
- risk-flag preservation
- evidence completeness
- abstention quality
- latency planning
- cost planning
- Operator review agreement

Financial return, profit, or simulated performance metrics must remain
paper-only research evidence.

They must not become an order, position, allocation, or execution instruction.

## Primary metrics and guardrails

Every comparison plan must distinguish:

- primary metrics
- secondary metrics
- blocking guardrails
- non-blocking diagnostics
- segment metrics
- data-quality metrics
- evidence-integrity metrics
- risk-preservation metrics

A candidate must not be declared superior only because one selected metric
improves.

A primary-metric improvement must not override a blocking guardrail failure.

Risk-flag deletion, contradiction suppression, evidence loss, leakage risk, or
Operator-review bypass must remain blocking failures.

## Comparison identity

Every baseline and candidate comparison must preserve:

- comparison_id
- baseline_id
- candidate_id
- baseline_registration_id
- candidate_registration_id
- evaluation_window_id
- dataset_snapshot_id
- metric_registry_version
- metric_definition_versions
- Config Snapshot identifiers
- Prompt versions when applicable
- model registrations when applicable
- market calendar version
- decision_cutoff_utc
- observation_cutoff_utc
- outcome_maturity_utc
- sample_count
- eligible_sample_count
- excluded_sample_count
- exclusion_reason_codes
- segment_definitions
- correlation_id
- evidence_references
- risk_flags
- contradictions
- Operator review requirement

The baseline and candidate must be evaluated using compatible definitions.

A comparison must not silently mix different windows, datasets, metrics,
calendars, Schemas, Config Snapshots, or outcome maturities.

## Sample sufficiency

Every metric result must preserve:

- observed_sample_count
- minimum_required_sample_count
- eligible_sample_count
- excluded_sample_count
- missing_sample_count
- segment_sample_count
- sample_sufficiency_state
- uncertainty_method
- uncertainty_value
- result_reliability_state

Sample sufficiency states must include:

- SUFFICIENT
- INSUFFICIENT
- PARTIAL
- NOT_APPLICABLE
- INVALID

INSUFFICIENT must not silently become SUFFICIENT.

A small sample must not be represented as conclusive evidence.

A missing uncertainty estimate must remain visible when one is required by the
registered metric definition.

## Exclusions and abstentions

Every excluded observation must preserve a reason code.

Permitted exclusion reasons must be registered.

The comparison packet must separately report:

- eligible observations
- excluded observations
- abstained observations
- invalid observations
- missing outcomes
- unresolved observations

Excluding a difficult segment to improve a result is prohibited.

Abstention must not be counted as a correct prediction unless the registered
metric explicitly defines that treatment.

## Segment analysis

Required segments may include:

- market family
- instrument class
- region
- data-quality state
- risk state
- confidence band
- scenario class
- time window
- model slot
- deterministic policy outcome

Aggregate improvement must not hide a blocking failure in a required segment.

Missing required segment coverage must remain visible.

## Comparison result states

Comparison result states must include:

- DRAFT
- ELIGIBILITY_CHECK
- NOT_COMPARABLE
- INSUFFICIENT_SAMPLE
- READY_FOR_REVIEW
- REVIEW_REQUIRED
- ACCEPTED
- REJECTED
- BLOCKED
- DEGRADED
- INVALID
- CANCELLED

No metric result may silently become ACCEPTED.

NOT_COMPARABLE must not be represented as a tie.

INSUFFICIENT_SAMPLE must not be represented as evidence of equivalence.

BLOCKED, DEGRADED, and INVALID must remain distinct.

## Candidate outcome classifications

A future comparison review may classify a candidate as:

- IMPROVED
- EQUIVALENT_WITHIN_TOLERANCE
- REGRESSED
- MIXED
- NOT_COMPARABLE
- INSUFFICIENT_EVIDENCE
- BLOCKED
- INVALID

These classifications are research-review labels only.

They are not promotion, activation, execution, allocation, or trading
instructions.

## Champion and baseline governance

A candidate outcome classification does not authorize:

- automatic Champion promotion
- automatic baseline replacement
- automatic configuration activation
- automatic Prompt activation
- automatic model activation
- automatic weight change
- automatic learning activation
- automatic archive
- automatic approval

Champion promotion and baseline replacement require separate governed
Operator decisions and immutable audit evidence.

## Failure behavior

The comparison must fail visibly when:

- a metric is unregistered
- metric versions differ without authorization
- required inputs are missing
- samples are insufficient
- required segments are missing
- evidence references are broken
- content hashes mismatch
- correlation_id values conflict
- leakage risk exists
- blocking guardrails fail
- risk flags are missing
- contradictions are suppressed
- Operator review is incomplete

A failed comparison must not be presented as complete.

## Permanent prohibitions

D3 must not create:

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
- automatic Champion promotion
- automatic baseline replacement
- automatic configuration activation
- automatic learning activation
- automatic approval
- automatic archive
- archive writing
- tag
- release
- deployment

## D3 acceptance boundaries

D3 passes only when:

- metric definitions must be registered and versioned
- deterministic calculation authority is preserved
- primary metrics and blocking guardrails remain separate
- baseline and candidate identity is complete
- sample sufficiency remains explicit
- exclusions and abstentions remain visible
- required segment failures cannot be hidden
- NOT_COMPARABLE and INSUFFICIENT_SAMPLE remain explicit
- risk flags and contradictions remain preserved
- automatic Champion promotion remains prohibited
- automatic learning activation remains prohibited
- Operator review remains mandatory
- no runtime implementation is created
- paper-only remains mandatory
- read-only remains mandatory
- sidecar-only remains mandatory
