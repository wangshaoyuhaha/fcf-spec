# AI-CONTEXT-EVIDENCE-CONTRACT-APP-1

## Purpose

Define AI evidence governance contract for FCF V2.

This sidecar extends AI explanation governance.
It does not modify core P1-P47.

## Safety Boundary

paper-only
local-only
read-only
sidecar-only
operator review required

Forbidden:
- real trading
- real execution
- broker connection
- exchange connection
- API key storage
- wallet private key access
- real account access
- real position access
- order generation
- automatic portfolio action

## Input Evidence Contract

Required fields:

research_run_id
correlation_id
source_artifact_ids
validation_baseline_id
source_trust_level
artifact_lifecycle_status

## Output Evidence Contract

Required fields:

explanation
reasoning_summary
uncertainty_statement
risk_flags
confidence_level

Forbidden output:

buy
sell
order
execute
position
allocation

## Governance Contract

AI output requires:

human_review_required = true

AI cannot bypass operator review.

