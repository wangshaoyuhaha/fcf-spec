# Registered Input and Evaluation Window Contract

## Phase

PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1

## Delivery

D2 - Registered Inputs, Evaluation Windows, and Leakage Control

## Status

PLANNING_ONLY

NO_RUNTIME_IMPLEMENTATION

NO_DATA_FETCHING

NO_FORWARD_OBSERVATION_RUNTIME

## Purpose

This contract defines which registered artifacts may enter future paper and
shadow validation and how evaluation time boundaries must be represented.

It does not fetch data, subscribe to data, run validation, invoke a model,
schedule observation, or write an archive.

## Authority

The deterministic FCF engine remains the calculation and policy authority.

Registered artifacts remain the evidence authority.

The Operator remains the final review authority.

A source being available does not make it eligible.

An eligible source does not make a validation result accepted.

## Permitted registered input classes

A future validation packet may reference:

- registered historical dataset snapshots
- registered deterministic result artifacts
- registered controlled AI result artifacts
- registered risk and contradiction artifacts
- registered evaluation-baseline artifacts
- registered configuration snapshots
- registered Prompt and model-version records
- registered subsequent-outcome artifacts
- registered Operator review artifacts

Every input remains read-only.

No source artifact may be silently modified, overwritten, repaired, replaced,
or deleted during validation.

## Required source manifest fields

Every validation input manifest must preserve:

- source_artifact_id
- source_artifact_kind
- source_registration_id
- source_schema_version
- dataset_version
- Config Snapshot identifier
- Prompt version when applicable
- model registration when applicable
- content_hash
- source_created_at_utc
- source_registered_at_utc
- source_as_of_utc
- effective_from_utc
- effective_to_utc
- observation_cutoff_utc
- freshness_state
- privacy_classification
- license_classification
- correlation_id
- evidence_references
- Operator review requirement

A missing mandatory field must not be silently inferred.

## Evaluation window identity

Every historical replay or forward observation plan must define:

- evaluation_window_id
- evaluation_mode
- reference_window_start_utc
- reference_window_end_utc
- decision_cutoff_utc
- observation_window_start_utc
- observation_window_end_utc
- outcome_maturity_utc
- embargo_duration
- timezone
- calendar_version
- dataset_snapshot_id
- metric_definition_version
- baseline_id
- candidate_id
- correlation_id

Evaluation modes must remain explicit:

- HISTORICAL_REPLAY
- FORWARD_OBSERVATION

The two modes must not share an ambiguous status label.

## Historical replay contract

Historical replay must use a frozen dataset snapshot.

All features, evidence, configurations, Prompts, models, and deterministic
results must be eligible as of the decision_cutoff_utc.

Subsequent outcomes may be used only after the simulated decision cutoff and
must remain separately identified as outcome evidence.

Historical replay must not include future-known revisions, later disclosures,
reconstructed values, or post-event labels unless explicitly registered and
labelled.

## Forward observation contract

Forward observation must register the research or prediction artifact before
the observation outcome becomes available.

The original artifact, content hash, decision cutoff, Config Snapshot,
correlation_id, risk flags, and contradictions must remain immutable.

Subsequent outcomes must be registered as separate artifacts.

Forward observation must not rewrite the original research artifact after an
outcome is known.

This phase does not implement a scheduler, observer, feed, listener, or data
subscription.

## Leakage-control rules

The future validation architecture must block or invalidate:

- future-known features
- outcome labels visible before decision_cutoff_utc
- post-event revisions presented as contemporaneous data
- silent historical backfill
- mutable dataset snapshots
- missing observation cutoffs
- overlapping reference and outcome windows without explicit authorization
- unregistered source replacement
- correlation_id mismatch
- broken evidence references
- unsupported Schema versions
- missing Config Snapshots
- missing content hashes

No AI explanation may override a leakage-control failure.

## Freshness and compatibility states

Input eligibility must distinguish:

- ELIGIBLE
- STALE
- INCOMPATIBLE
- UNREGISTERED
- HASH_MISMATCH
- CORRELATION_BROKEN
- LEAKAGE_RISK
- BLOCKED
- DEGRADED
- INVALID

STALE must not silently become ELIGIBLE.

DEGRADED must not silently become ACCEPTED.

LEAKAGE_RISK must block complete-status presentation until explicitly
resolved through governed Operator review.

INVALID inputs must not enter metric calculation.

## Baseline and candidate comparability

A baseline and candidate comparison is valid only when compatible values exist
for:

- dataset snapshot
- evaluation window
- observation cutoff
- outcome maturity
- metric definition
- Schema version
- market calendar
- Config Snapshot
- required evidence
- correlation scope

A comparison with incompatible windows must not be represented as a valid
performance difference.

## Failure behavior

Missing, stale, incompatible, corrupted, unregistered, leakage-risk, or
correlation-broken inputs must fail visibly.

The system must not:

- invent missing timestamps
- infer missing hashes
- repair evidence silently
- substitute a newer dataset silently
- remove risk flags
- suppress contradictions
- continue as successful after a blocking eligibility failure

## Permanent prohibitions

D2 must not create:

- P1-P47 frozen Core mutation
- P48
- runtime data ingestion
- external data fetching
- web scraping
- broker or exchange connectivity
- credential access
- account, balance, position, or wallet access
- order placement
- model invocation
- Prompt execution
- automatic provider routing
- automatic approval
- automatic Champion promotion
- automatic learning activation
- automatic archive
- archive writing
- tag
- release
- deployment

## D2 acceptance boundaries

D2 passes only when:

- only registered inputs are permitted
- required source identity fields are explicit
- historical replay and forward observation remain separate
- decision and observation cutoffs are explicit
- subsequent outcomes remain separate artifacts
- future-data leakage is explicitly blocked
- stale and incompatible inputs remain visible
- correlation_id and evidence integrity are mandatory
- baseline and candidate comparability is deterministic
- Operator review remains mandatory
- no runtime implementation is created
- paper-only remains mandatory
- read-only remains mandatory
- sidecar-only remains mandatory
