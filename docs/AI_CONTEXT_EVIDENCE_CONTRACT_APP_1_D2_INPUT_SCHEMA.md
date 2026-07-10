# AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 D2

## AI Input Evidence Schema

Purpose:

Define read-only evidence inputs consumed by AI context layer.

## Input Sources

Allowed sources:

- DATA_APP_OUTPUT
- STOCK_APP_OUTPUT
- MARKET_SCENARIO_OUTPUT
- BACKTEST_REVIEW_OUTPUT
- MODEL_GOVERNANCE_OUTPUT
- OPERATOR_REVIEW_OUTPUT
- REPORT_ARCHIVE_OUTPUT

## Required Fields

research_run_id

correlation_id

source_artifact_ids

validation_baseline_id

source_trust_level

artifact_lifecycle_status

input_hash

source_timestamp

source_version

quality_state

## Evidence Rules

AI input must preserve:

- source identity
- validation state
- artifact lineage
- lifecycle state

AI cannot:

- modify source data
- remove risk flags
- downgrade validation state
- overwrite artifacts

## Multi Asset Support

Supported asset categories:

- STOCK
- BTC
- FUTURES
- OTHER_FINANCIAL_ASSET

Schema must remain asset-neutral.

## Safety

paper-only

local-only

read-only

sidecar-only

operator review required

