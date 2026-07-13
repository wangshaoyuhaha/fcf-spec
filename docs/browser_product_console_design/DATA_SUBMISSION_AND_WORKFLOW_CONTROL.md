# Browser Product Console Data Submission and Workflow Control

## Phase

BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1

## Delivery

D3 - Data Submission, Task Lifecycle, and Workflow Control

## Status

DESIGN_ONLY

NO_RUNTIME_IMPLEMENTATION

## Submission boundary

The future console may prepare a governed paper-data submission.

A submission must contain:

- submission identifier
- source identity
- source type
- file name
- content hash
- privacy classification
- licensing status
- Schema version
- workspace identifier
- submitting user identity
- submission timestamp
- correlation identifier
- Config Snapshot reference

The browser must not directly browse unrestricted local filesystem paths.

The browser must not transmit sensitive data before eligibility is confirmed.

## Upload preparation states

Allowed preparation states are:

- EMPTY
- FILE_SELECTED
- HASHING
- CLASSIFYING
- VALIDATING
- READY_TO_SUBMIT
- SUBMISSION_BLOCKED
- SUBMITTED

Selecting a file does not start a research workflow.

Uploading a file does not approve its use.

A failed validation must remain visible.

## Validation gates

A submission must be blocked when any required condition fails:

- source identity is missing
- privacy classification is missing
- licensing status is unknown
- Schema version is unsupported
- content hash is missing
- required metadata is incomplete
- Policy Eligibility rejects the submission
- duplicate submission protection is triggered

A blocked submission must not be silently downgraded to a warning.

## Idempotency

Every submission action requires an idempotency key.

Every workflow-start action requires an idempotency key.

A browser refresh must not repeat a submission.

A browser refresh must not repeat a workflow start.

A retry with the same idempotency key must return the existing result.

A retry must not create a duplicate run.

## Workflow lifecycle

Allowed workflow states are:

- DRAFT
- QUEUED
- VALIDATING
- RUNNING_DETERMINISTIC_STAGE
- WAITING_FOR_CONTROLLED_AI
- CONTROLLED_AI_COMPLETE
- REVIEW_REQUIRED
- RETURNED_FOR_REVISION
- APPROVED
- REJECTED
- BLOCKED
- FAILED
- CANCEL_REQUESTED
- CANCELLED
- ARCHIVE_ELIGIBLE
- ARCHIVED

The console must display the authoritative state returned by FCF.

The console must not invent a successful state.

## Start control

Starting a workflow requires:

- an eligible submission
- an explicit Research Analyst action
- a confirmation screen
- an idempotency key
- a stable workflow identifier
- a correlation identifier
- an immutable start audit record

No workflow starts from page load, route change, tab change, or browser refresh.

## Pause and resume

Pause and resume are future governed commands only.

The design must distinguish:

- user-requested pause
- policy pause
- dependency pause
- provider-unavailable pause
- Operator-required pause

A resume action must not bypass failed validation.

A resume action must continue from an approved checkpoint.

A resume action must not repeat completed deterministic stages.

## Cancellation

Cancellation is a request, not an immediate assumption.

The console must show:

- cancellation requested
- cancellation accepted
- cancellation rejected
- cancellation completed

Cancelling a workflow must not delete evidence or audit history.

Cancellation must not convert a failed run into a successful run.

## Retry control

A retry must identify:

- failed stage
- failure classification
- retry eligibility
- prior attempt identifier
- new attempt identifier
- preserved correlation identifier
- preserved evidence references

Retry must be stage-scoped.

Retry must not restart the entire workflow unless explicitly approved.

Retry must not repeat a completed Operator decision.

## Controlled AI boundary

The workflow may wait for controlled AI assistance.

The browser must not:

- select a model automatically
- switch models automatically
- route to a provider automatically
- invoke an unregistered model
- execute a Prompt automatically
- hide provider unavailability
- treat AI completion as Operator approval

Controlled AI remains subordinate to deterministic authority and Operator review.

## Operator handoff

A workflow enters REVIEW_REQUIRED only after required artifacts exist.

The review packet must reference:

- deterministic results
- controlled AI outputs
- risk flags
- contradictions
- evidence references
- provenance
- Config Snapshot
- Schema version
- Prompt version
- model registration
- correlation identifier

Missing required artifacts must block review completion.

## Audit requirements

Every governed action must record:

- actor identity
- actor role
- action name
- prior state
- resulting state
- timestamp
- correlation identifier
- idempotency key when applicable
- reason or rationale
- success or failure result

The browser must not edit immutable audit records.

## Forbidden controls

The console must not provide:

- real order controls
- live-trading controls
- broker or exchange controls
- wallet controls
- balance or position controls
- automatic approval controls
- automatic archive controls
- arbitrary shell execution
- arbitrary Python execution
- arbitrary PowerShell execution
- direct Git mutation
- runtime activation during this design phase
- web server startup during this design phase
- HTTP port binding during this design phase

## D3 acceptance contract

D3 is accepted only when:

- submission metadata is explicit
- validation gates are explicit
- idempotency is mandatory
- workflow states are explicit
- start, pause, resume, cancel, and retry semantics are explicit
- refresh cannot duplicate actions
- controlled AI cannot become authority
- Operator review remains mandatory
- evidence and audit history are preserved
- no runtime implementation is created
