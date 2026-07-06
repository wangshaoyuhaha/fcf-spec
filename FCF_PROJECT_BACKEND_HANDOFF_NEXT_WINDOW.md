# FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW

This file is the backend project handoff source for the next ChatGPT window.

## Project identity

Project: FCF / Financial Cognitive Framework
Repository: wangshaoyuhaha/fcf-spec
Local path: C:\Users\Admin\Desktop\btc_finance_platform
Branch: main

Latest main commit:
3123704 add final architecture gap audit report

Validation baseline:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 1505 passed

Git status:
clean

origin/main:
synced

Tag:
none

Release:
none

Deploy:
none

Generated at UTC:
2026-07-06T16:17:10Z

## Scope rule

Continue BTC finance platform / FCF financial market model project only.
Do not switch to football project.

btc_finance_platform is the local folder name.
The platform is a multi-asset financial market paper-only system, not BTC-only.
Target market research scope includes stocks, BTC, futures, and other financial market assets.

## Core status

P1-P47 core is frozen.

Core rules:
- no P48 core expansion
- no P1-P47 core mutation
- no core bypass
- no source content mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade

## Completed core phase

P1-P47:
completed and frozen

Current validation:
1505 passed

## Completed sidecar apps and stages

### DATA-APP-1

Status:
completed and merged into main

Purpose:
paper-only local data app layer

Completed stages:
- DATA-APP-1 D1 sidecar boundary
- DATA-APP-1 D2 A-share schema
- DATA-APP-1 D3 local CSV/JSON adapter
- DATA-APP-1 D4 manifest and checksum
- DATA-APP-1 D5 health check and clean universe/watchlist/quarantine report
- DATA-APP-1 D6 final closeout

### STOCK-APP-1

Status:
completed and merged into main

Purpose:
paper-only local stock candidate and watchlist analysis sidecar

Completed stages:
- STOCK-APP-1 D1 base candidate filter
- STOCK-APP-1 D2 sector/theme linkage
- STOCK-APP-1 D3 volume-price anomaly rules
- STOCK-APP-1 D4 public fund-flow proxy
- STOCK-APP-1 D5 limit-up potential scoring
- STOCK-APP-1 D6 ranked watchlist and candidate report handoff

### AI-CONTEXT-1

Status:
completed and merged into main

Purpose:
paper-only explanation and operator context sidecar

Completed stages:
- AI-CONTEXT-1 D1 sidecar boundary and explanation contract
- AI-CONTEXT-1 D2 read STOCK-APP ranked watchlist contract
- AI-CONTEXT-1 D3 reason code and risk flag dictionary
- AI-CONTEXT-1 D4 structured JSON explanation output
- AI-CONTEXT-1 D5 operator review summary report
- AI-CONTEXT-1 D6 final closeout

### UI-APP-1

Status:
completed and merged into main

Purpose:
paper-only local UI context sidecar

Completed stages:
- UI-APP-1 D1 sidecar boundary
- UI-APP-1 D2 local UI schema
- UI-APP-1 D3 review layout contract
- UI-APP-1 D4 status display contract
- UI-APP-1 D5 operator-safe UI handoff
- UI-APP-1 D6 final handoff closeout

### OPERATOR-REVIEW-APP-1

Status:
completed and merged into main

Purpose:
paper-only operator review and signoff sidecar

Completed stages:
- OPERATOR-REVIEW-APP-1 D1 boundary
- OPERATOR-REVIEW-APP-1 D2 source contract
- OPERATOR-REVIEW-APP-1 D3 review schema
- OPERATOR-REVIEW-APP-1 D4 review model
- OPERATOR-REVIEW-APP-1 D5 review packet
- OPERATOR-REVIEW-APP-1 D6 final closeout

### REPORT-ARCHIVE-APP-1

Status:
completed and merged into main

Purpose:
paper-only local report archive sidecar

Completed stages:
- REPORT-ARCHIVE-APP-1 D1 boundary
- REPORT-ARCHIVE-APP-1 D2 source loader
- REPORT-ARCHIVE-APP-1 D3 archive schema
- REPORT-ARCHIVE-APP-1 D4 archive model
- REPORT-ARCHIVE-APP-1 D5 archive packet
- REPORT-ARCHIVE-APP-1 D6 final closeout

### DATA-QUALITY-OPS-APP-1

Status:
completed and merged into main

Purpose:
paper-only data quality operations sidecar

Completed stages:
- DATA-QUALITY-OPS-APP-1 D1 boundary
- DATA-QUALITY-OPS-APP-1 D2 source loader
- DATA-QUALITY-OPS-APP-1 D3 quality schema
- DATA-QUALITY-OPS-APP-1 D4 quality review model
- DATA-QUALITY-OPS-APP-1 D5 quality packet
- DATA-QUALITY-OPS-APP-1 D6 final closeout

### MARKET-SCENARIO-APP-1

Status:
completed and merged into main

Purpose:
paper-only market scenario review sidecar

Completed stages:
- MARKET-SCENARIO-APP-1 D1 boundary
- MARKET-SCENARIO-APP-1 D2 source loader
- MARKET-SCENARIO-APP-1 D3 scenario schema
- MARKET-SCENARIO-APP-1 D4 scenario review model
- MARKET-SCENARIO-APP-1 D5 scenario packet
- MARKET-SCENARIO-APP-1 D6 final closeout

### BACKTEST-REVIEW-APP-1

Status:
completed and merged into main

Purpose:
paper-only backtest review sidecar

Completed stages:
- BACKTEST-REVIEW-APP-1 D1 boundary
- BACKTEST-REVIEW-APP-1 D2 source loader
- BACKTEST-REVIEW-APP-1 D3 backtest review schema
- BACKTEST-REVIEW-APP-1 D4 review model
- BACKTEST-REVIEW-APP-1 D5 review packet
- BACKTEST-REVIEW-APP-1 D6 final closeout

### SIGNAL-VALIDATION-APP-1

Status:
completed and merged into main

Purpose:
paper-only signal validation sidecar

Completed stages:
- SIGNAL-VALIDATION-APP-1 D1 boundary
- SIGNAL-VALIDATION-APP-1 D2 source loader
- SIGNAL-VALIDATION-APP-1 D3 validation schema
- SIGNAL-VALIDATION-APP-1 D4 validation model
- SIGNAL-VALIDATION-APP-1 D5 validation packet
- SIGNAL-VALIDATION-APP-1 D6 final closeout

### MODEL-GOVERNANCE-APP-1

Status:
completed and merged into main

Purpose:
paper-only model governance sidecar

Known commits:
- merge commit: 5da3c3b merge MODEL-GOVERNANCE-APP-1 into main
- final branch commit: 82eea43 add MODEL-GOVERNANCE-D6 final handoff closeout
- final current-state commit: 5bc8fb3 add MODEL-GOVERNANCE-APP-1 final current state

Validation:
1429 passed at completion

Completed stages:
- MODEL-GOVERNANCE-D1 boundary contract
- MODEL-GOVERNANCE-D2 source loader
- MODEL-GOVERNANCE-D3 governance schema
- MODEL-GOVERNANCE-D4 governance review model
- MODEL-GOVERNANCE-D5 governance packet
- MODEL-GOVERNANCE-D6 final handoff closeout

### WATCHLIST-LIFECYCLE-APP-1

Status:
completed and merged into main

Known commits:
- D1: e83085d add WATCHLIST-LIFECYCLE-D1 boundary contract
- D2: 052a140 add WATCHLIST-LIFECYCLE-D2 source loader
- D3: b7e424d add WATCHLIST-LIFECYCLE-D3 lifecycle schema
- D4: e3c6740 add WATCHLIST-LIFECYCLE-D4 decision model
- D5: c359417 add WATCHLIST-LIFECYCLE-D5 lifecycle packet
- D4 repair: 65fa54e fix WATCHLIST-LIFECYCLE-D4 transition-safe stale handling
- D6: 973b74a add WATCHLIST-LIFECYCLE-D6 final handoff closeout
- merge: 64d9849 merge WATCHLIST-LIFECYCLE-APP-1 into main

Validation:
1457 passed at completion

Completed stages:
- WATCHLIST-LIFECYCLE-D1 boundary contract
- WATCHLIST-LIFECYCLE-D2 source loader
- WATCHLIST-LIFECYCLE-D3 lifecycle schema
- WATCHLIST-LIFECYCLE-D4 decision model
- WATCHLIST-LIFECYCLE-D4 repair transition-safe stale handling
- WATCHLIST-LIFECYCLE-D5 lifecycle packet
- WATCHLIST-LIFECYCLE-D6 final handoff closeout

### PORTFOLIO-REVIEW-APP-1

Status:
completed and merged into main

Validation:
1465 passed at completion

Completed stages:
- PORTFOLIO-REVIEW-D1 boundary contract
- PORTFOLIO-REVIEW-D2 read-only source loader
- PORTFOLIO-REVIEW-D3 paper exposure review schema
- PORTFOLIO-REVIEW-D4 paper portfolio review model
- PORTFOLIO-REVIEW-D5 paper portfolio review packet
- PORTFOLIO-REVIEW-D6 final workflow handoff

### RISK-EXPOSURE-APP-1

Status:
completed, merged into main, repaired, final current-state committed

Known commits:
- sidecar: d6d04c1 add RISK-EXPOSURE-APP-1 sidecar
- merge: 09175d7 merge RISK-EXPOSURE-APP-1 into main
- repair: a2af41f fix RISK-EXPOSURE contract trade action boundary flag
- final current state: 561653b add RISK-EXPOSURE-APP-1 final current state

Validation:
1473 passed at completion

Completed stages:
- RISK-EXPOSURE-D1 boundary contract
- RISK-EXPOSURE-D2 read-only source loader
- RISK-EXPOSURE-D3 paper risk exposure schema
- RISK-EXPOSURE-D4 paper risk exposure review model
- RISK-EXPOSURE-D5 paper risk exposure packet
- RISK-EXPOSURE-D6 final workflow handoff
- Repair: missing trade_action_allowed boundary flag fixed

### DECISION-AUDIT-APP-1

Status:
completed and merged into main

Known commits:
- sidecar: 8d60588 add DECISION-AUDIT-APP-1 sidecar
- merge: 80c0a81 merge DECISION-AUDIT-APP-1 into main
- final current state: 2e923ca add DECISION-AUDIT-APP-1 final current state

Validation:
1481 passed at completion

Completed stages:
- DECISION-AUDIT-D1 boundary contract
- DECISION-AUDIT-D2 read-only source loader
- DECISION-AUDIT-D3 decision audit event schema
- DECISION-AUDIT-D4 audit review model
- DECISION-AUDIT-D5 audit packet
- DECISION-AUDIT-D6 final workflow handoff

### RESEARCH-WORKFLOW-APP-1

Status:
completed and merged into main

Known commits:
- sidecar: a2899d0 add RESEARCH-WORKFLOW-APP-1 sidecar
- merge: 7a96b96 merge RESEARCH-WORKFLOW-APP-1 into main
- final current state: 27eb356 add RESEARCH-WORKFLOW-APP-1 final current state

Validation:
1489 passed at completion

Completed stages:
- RESEARCH-WORKFLOW-D1 boundary contract
- RESEARCH-WORKFLOW-D2 read-only source loader
- RESEARCH-WORKFLOW-D3 workflow state schema
- RESEARCH-WORKFLOW-D4 workflow review model
- RESEARCH-WORKFLOW-D5 workflow packet
- RESEARCH-WORKFLOW-D6 final workflow handoff

### DASHBOARD-STATUS-APP-1

Status:
completed and merged into main

Known commits:
- sidecar: 328b579 add DASHBOARD-STATUS-APP-1 sidecar
- merge: 7f53d10 merge DASHBOARD-STATUS-APP-1 into main
- final current state: 7a90616 add DASHBOARD-STATUS-APP-1 final current state

Validation:
1497 passed at completion

Completed stages:
- DASHBOARD-STATUS-D1 boundary contract
- DASHBOARD-STATUS-D2 read-only source loader
- DASHBOARD-STATUS-D3 dashboard status schema
- DASHBOARD-STATUS-D4 dashboard status review model
- DASHBOARD-STATUS-D5 dashboard status packet
- DASHBOARD-STATUS-D6 final workflow handoff

### FINAL-COMPLETION-REVIEW-APP-1

Status:
completed and merged into main

Known commits:
- sidecar: 88fc376 add FINAL-COMPLETION-REVIEW-APP-1 sidecar
- merge: e1582d8 merge FINAL-COMPLETION-REVIEW-APP-1 into main
- final current state: 5bf295c add FINAL-COMPLETION-REVIEW-APP-1 final current state

Validation:
1505 passed at completion

Completed stages:
- FINAL-COMPLETION-REVIEW-D1 boundary contract
- FINAL-COMPLETION-REVIEW-D2 read-only source loader
- FINAL-COMPLETION-REVIEW-D3 completion review schema
- FINAL-COMPLETION-REVIEW-D4 completion review model
- FINAL-COMPLETION-REVIEW-D5 completion review packet
- FINAL-COMPLETION-REVIEW-D6 final workflow handoff

## Final audit files

Final master file:
FCF_CURRENT_STATE_MASTER_FINAL.md

Final architecture audit report:
FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md

Known audit commit:
3123704 add final architecture gap audit report

Known master commit:
414fee9 add master final current state

Final audit result:
PASS final architecture gap audit passed
PASS current repo remains paper-only/local-only/read-only/sidecar-only
PASS no tag/release/deploy action detected
1505 passed

## Safety boundary

Required:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

Forbidden:
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
- no workflow execution
- no decision auto approval
- no operator review bypass
- no future return prediction
- no guaranteed performance claim
- no tag
- no release
- no deploy

## Next window instruction

In a new ChatGPT window, start by reading:
- FCF_CURRENT_STATE_MASTER_FINAL.md
- FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md

Then do architecture planning only unless the user explicitly asks for a new code phase.
