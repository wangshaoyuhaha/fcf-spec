# AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 D3

## AI Output Evidence Schema

Purpose:

Define governed AI output structure for FCF V2.

AI output is explanation only.
AI output is not execution.

## Output Fields

Required:

explanation

reasoning_summary

uncertainty_statement

risk_flags

confidence_level

human_review_required

archive_required

## Evidence Trace Fields

Required:

research_run_id

correlation_id

source_artifact_ids

validation_baseline_id

prompt_version

model_version

contract_version

output_hash

## Risk Preservation Rules

AI output must preserve:

- original risk_flags
- original validation state
- original source lineage

AI cannot:

- remove risk_flags
- downgrade risk severity
- create unsupported facts
- modify source artifacts

## Forbidden Output Actions

Forbidden:

buy

sell

order

execute

position

allocation

portfolio_action

trade_instruction

## Multi Asset Output Support

Supported:

STOCK

BTC

FUTURES

OTHER_FINANCIAL_ASSET

Output schema remains asset-neutral.

## Safety Boundary

paper-only

local-only

read-only

sidecar-only

operator review required

