# FCF_CURRENT_STATE_RESEARCH_WORKFLOW_APP_1_FINAL

Continue BTC finance platform / FCF financial market model project only.
Do not switch to football project.

## Project identity

Project: FCF / Financial Cognitive Framework
Repository: wangshaoyuhaha/fcf-spec
Local path: C:\Users\Admin\Desktop\btc_finance_platform

Important note:
btc_finance_platform is the local folder name.
The platform is a multi-asset financial market paper-only system, not BTC-only.
Main future application direction remains financial market research across stocks, BTC, futures, and other market assets.

## Current latest main state

Branch:
main

Latest main merge commit:
merge RESEARCH-WORKFLOW-APP-1 into main

RESEARCH-WORKFLOW-APP-1 sidecar commit:
add RESEARCH-WORKFLOW-APP-1 sidecar

Previous completed app:
DECISION-AUDIT-APP-1

Previous DECISION-AUDIT final current-state file:
FCF_CURRENT_STATE_DECISION_AUDIT_APP_1_FINAL.md

Validation:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 1489 passed

git status: clean
origin/main: synced
Tag: none
Release: none
Deploy: none

Generated at UTC:
2026-07-06

## Completed project scope

P1-P47 core is frozen.

Completed sidecar app layers merged into main:
- DATA-APP-1
- STOCK-APP-1
- AI-CONTEXT-1
- UI-APP-1
- OPERATOR-REVIEW-APP-1
- REPORT-ARCHIVE-APP-1
- DATA-QUALITY-OPS-APP-1
- MARKET-SCENARIO-APP-1
- BACKTEST-REVIEW-APP-1
- SIGNAL-VALIDATION-APP-1
- MODEL-GOVERNANCE-APP-1
- WATCHLIST-LIFECYCLE-APP-1
- PORTFOLIO-REVIEW-APP-1
- RISK-EXPOSURE-APP-1
- DECISION-AUDIT-APP-1
- RESEARCH-WORKFLOW-APP-1

## RESEARCH-WORKFLOW-APP-1 completed branch

Branch:
sidecar-research-workflow-app-1

Completed stages:
- RESEARCH-WORKFLOW-D1 boundary contract
- RESEARCH-WORKFLOW-D2 read-only source loader
- RESEARCH-WORKFLOW-D3 workflow state schema
- RESEARCH-WORKFLOW-D4 workflow review model
- RESEARCH-WORKFLOW-D5 workflow packet
- RESEARCH-WORKFLOW-D6 final workflow handoff

## Purpose

RESEARCH-WORKFLOW-APP-1 is a paper-only local research workflow orchestration and review layer.

It reads existing local outputs from:
- DECISION-AUDIT-APP-1
- RISK-EXPOSURE-APP-1
- PORTFOLIO-REVIEW-APP-1
- WATCHLIST-LIFECYCLE-APP-1
- MODEL-GOVERNANCE-APP-1
- SIGNAL-VALIDATION-APP-1
- BACKTEST-REVIEW-APP-1
- MARKET-SCENARIO-APP-1
- DATA-QUALITY-OPS-APP-1
- REPORT-ARCHIVE-APP-1
- OPERATOR-REVIEW-APP-1
- UI-APP-1
- AI-CONTEXT-1
- STOCK-APP-1
- DATA-APP-1

It can generate:
- research workflow contract
- research workflow source manifest
- research workflow state schema
- research workflow review model
- research workflow packet
- final workflow handoff

It is not:
- a workflow execution engine
- a decision engine
- an auto approval engine
- a trade instruction engine
- a real trading system
- an execution system
- a broker or exchange connector
- an order ticket generator
- a buy or sell instruction generator
- a position sizing engine
- a portfolio action engine
- a future return prediction engine
- a guaranteed performance claim engine

## Safety boundary

Required:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

Forbidden:
- no P48 core expansion
- no P1-P47 core mutation
- no source content mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no workflow auto approval
- no workflow execution
- no decision auto approval
- no decision override
- no operator review bypass
- no real trading
- no real execution
- no broker connection
- no exchange connection
- no API key storage
- no wallet private key access
- no real account access
- no real position access
- no buy button
- no sell button
- no order button
- no position management
- no automatic position sizing
- no automatic portfolio action
- no future return prediction
- no guaranteed performance claim
- no tag
- no release
- no deploy

Research-workflow-specific forbidden scope:
- workflow_state must not become a trade instruction
- research_workflow_packet must not become an order ticket
- workflow review must not become auto approval
- workflow review must not execute real actions
- workflow review must not bypass operator review
- workflow review must not mutate upstream scores, reasons, or risk flags

## Final status

RESEARCH-WORKFLOW-APP-1 is completed, merged into main, validated, pushed, and clean.

Current final baseline:
branch = main
latest merge commit includes merge RESEARCH-WORKFLOW-APP-1 into main
origin/main = synced
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 1489 passed
git status --short = blank

## Next recommended sidecar sequence

1. DASHBOARD-STATUS-APP-1

## Next workflow rule

Start the next sidecar phase only after a read-only state check.

Do not tag, release, deploy, or start real trading integrations.
