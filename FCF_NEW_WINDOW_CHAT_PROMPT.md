Continue BTC finance platform / FCF financial market model project only.
Do not switch to football project.

First read these backend source files:
- FCF_CURRENT_STATE_MASTER_FINAL.md
- FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md

Current final state:
- branch: main
- latest known main audit commit: 3123704 add final architecture gap audit report
- master final current-state commit: 414fee9 add master final current state
- validation: python scripts/run_all_checks.py = ALL CHECKS PASSED
- pytest: 1505 passed
- git status: clean
- origin/main: synced
- no tag
- no release
- no deploy

P1-P47 core is frozen.
All current sidecar apps through FINAL-COMPLETION-REVIEW-APP-1 are completed, merged into main, final current-state files committed, and audit passed.

Safety boundary:
paper-only, local-only, read-only, sidecar-only, operator review required.
No real trading, no real execution, no broker connection, no exchange connection, no API key storage, no wallet private key access, no real account access, no real position access, no buy/sell/order button, no position management, no automatic position sizing, no automatic portfolio action, no future return prediction, no guaranteed performance claim, no tag, no release, no deploy.

Task for new window:
Do architecture planning / gap review first.
Do not write code unless explicitly instructed.
