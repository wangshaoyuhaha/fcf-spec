# AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 D6

## Final Workflow Handoff

Purpose:

Define final handoff contract for AI evidence governance layer.

This sidecar provides evidence traceability.
It does not provide execution capability.

## Handoff Targets

Supported:

- UI-APP
- OPERATOR-REVIEW-APP
- REPORT-ARCHIVE-APP
- MODEL-GOVERNANCE-APP
- DASHBOARD-STATUS-APP

## Handoff Payload

Required:

research_run_id

correlation_id

artifact_package_id

source_artifact_ids

validation_baseline_id

ai_runtime_record

ai_output_evidence

human_review_required

archive_required

## UI Consumption Rules

UI may display:

- explanation
- reasoning_summary
- uncertainty_statement
- risk_flags
- confidence_level
- runtime_status
- review_status

UI cannot create:

- trade instruction
- execution action
- order action

## Operator Review Rules

Operator Review receives:

- evidence package
- AI runtime record
- uncertainty statement
- risk flags
- archive reference

Operator review remains mandatory.

AI cannot bypass review.

## Archive Rules

Archive stores:

- input evidence
- output evidence
- runtime metadata
- version metadata
- review linkage

Archive does not execute actions.

## Final Safety Contract

paper-only

local-only

read-only

sidecar-only

operator review required

Forbidden:

real trading

real execution

broker connection

exchange connection

API key storage

wallet private key access

real account access

real position access

automatic portfolio action

automatic decision approval

## Completion State

AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 completed.

Next work requires architecture review before new sidecars.

