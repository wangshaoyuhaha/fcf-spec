# AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 D4

## AI Runtime Governance Record

Purpose:

Define controlled AI runtime metadata for FCF V2.

This record tracks AI execution context.
It does not execute actions.

## Runtime Identity

Required:

research_run_id

correlation_id

contract_version

prompt_version

model_version

## Runtime Status

Required:

runtime_status

allowed values:

- COMPLETED
- DEGRADED
- FAILED
- WAITING_FOR_OPERATOR_REVIEW

## Runtime Control

Required:

timeout_status

retry_status

fallback_mode

degradation_reason

## Quality Governance

Required:

input_validation_passed

output_validation_passed

forbidden_action_check

human_review_required

archive_required

## AI Failure Handling

When AI fails:

- preserve input evidence
- preserve artifact lineage
- record failure reason
- require operator review

AI fallback cannot:

- create trade instruction
- bypass review
- modify source data
- change risk flags

## Forbidden Runtime Capability

Not allowed:

real trading

real execution

broker connection

exchange connection

API key usage

wallet access

real account access

real position access

automatic portfolio action

## Safety Boundary

paper-only

local-only

read-only

sidecar-only

operator review required

