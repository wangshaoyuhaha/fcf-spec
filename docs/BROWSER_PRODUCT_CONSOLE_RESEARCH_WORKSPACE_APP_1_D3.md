# BROWSER-PRODUCT-CONSOLE-RESEARCH-WORKSPACE-APP-1 D3

## Status

COMPLETED_ON_SIDECAR

## Scope

D3 implements the governed Research Runs and AI Comparison workspaces.

## Delivered

- Research Runs route at /runs
- registered research_run artifact support
- registered workflow_status artifact support
- deterministic run ID and workflow state presentation
- explicit AVAILABLE, INCOMPLETE, and NO_REGISTERED_RUNS states
- AI Comparison route at /ai-comparison
- registered ai_explanation artifact presentation
- registered ai_evaluation artifact support
- deterministic model, prompt version, and evaluation state labels
- explicit COMPARISON_READY, INCOMPLETE, and
  NO_REGISTERED_AI_ARTIFACTS states
- payload HTML escaping
- GET and HEAD only presentation
- Overview route availability updated
- existing Browser Product Console routes preserved

## Permanent boundary

- P1-P47 frozen
- no P48
- paper-only
- local-only
- loopback-only
- sidecar-only
- registered-artifact-only
- Operator review mandatory
- Deterministic Engine authority preserved
- AI advisory only
- no external data fetching
- no workflow dispatch or mutation
- no public network exposure
- no broker, exchange, credentials, account, balance, position, wallet,
  order, or real execution path
- no automatic approval, promotion, baseline replacement, learning, or archive
- no tag, release, or deployment

D3 does not implement Governance or Audit History. Those surfaces start in D4.
