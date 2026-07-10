# FCF CURRENT HANDOFF TRUTH - STALE MARKER CLEANUP APPLIED

This file contains current handoff truth.

CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed.

Current truth commits:
- main merge commit: ad16c03
- D6 final closeout commit: 42ffeef
- final handoff sync commit: 8c18573
- validation: 1884 passed

Stale marker rule:
Any old next-phase approval, old validation count, old approved-but-not-started marker, or old begin-with-D1 instruction is historical unless explicitly re-approved by the operator.

Current latest completed phase:
ARCHIVE-CORRELATION-ROLLUP-APP-1 is completed, merged into main, validated, pushed, and clean.

Current latest commits:
- final current state sync commit: 8089b75
- main merge commit: 59ba8e7
- final sidecar commit: fb05e00

Current validation:
- python scripts/run_all_checks.py = pending after this repair
- python -m pytest -q = pending after this repair

---
# FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW

Continue FCF / Financial Cognitive Framework only.
Do not switch to football project.

## Project identity

Project: FCF / Financial Cognitive Framework
Repository: wangshaoyuhaha/fcf-spec
Local path: C:\Users\Admin\Desktop\btc_finance_platform
Branch: main

The local folder name btc_finance_platform is retained for convenience.
The platform is a multi-asset financial market paper-only research governance system, not BTC-only.

## Current latest main state

Latest main merge commit:
59ba8e7 merge ARCHIVE-CORRELATION-ROLLUP-APP-1 into main

Latest completed sidecar:
ARCHIVE-CORRELATION-ROLLUP-APP-1

Final sidecar commit:
fb05e00 fix ARCHIVE-CORRELATION-D6 final handoff tests

Validation baseline:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 2002 passed

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

## Latest completed phase

ARCHIVE-CORRELATION-ROLLUP-APP-1 completed and merged into main.

Purpose:
Upgrade correlation_id from passive field preservation into a read-only full-chain evidence index.

Completed stages:

- D1 sidecar boundary and correlation rollup contract
- D2 read-only source artifact reference model
- D3 correlation chain coverage matrix
- D4 trace summary
- D5 read-only rollup packet
- D6 final handoff closeout

Evidence chain indexed:

- data_snapshot
- candidate
- ai_explanation
- ui_packet
- review_packet
- archive_packet
- handoff
- final_state

Allowed rollup statuses:

- COMPLETE
- INCOMPLETE
- STALE
- UNRESOLVED

## Safety boundary

Required:

- paper-only
- local-only
- read-only
- sidecar-only
- index-only
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
- no automatic position sizing
- no automatic portfolio action
- no workflow execution
- no decision auto approval
- no operator review bypass
- no evidence backfill
- no correlation_id auto-fill
- no placeholder review generation
- no UI dashboard panel creation
- no tag
- no release
- no deploy

## Next-window instruction

Start from main.

First run read-only verification:

cd C:\Users\Admin\Desktop\btc_finance_platform
git branch --show-current
git status --short
git log -10 --oneline
python scripts/run_all_checks.py
python -m pytest -q

Expected:
branch = main
latest main includes 59ba8e7 merge ARCHIVE-CORRELATION-ROLLUP-APP-1 into main
ALL CHECKS PASSED
2002 passed
git status --short blank

Then return to control center planning before approving the next sidecar phase.
Do not tag, release, deploy, or start real trading integrations.

git status: clean

Architecture gap review or explicitly approved next phase only
origin/main: synced


## Approved Next Phase

ARTIFACT-LIFECYCLE-REGISTRY-APP-1 is approved as the next sidecar phase.

Start from main only after read-only verification.

Expected baseline before branch creation:
- branch = main
- latest HEAD includes approval commit for ARTIFACT-LIFECYCLE-REGISTRY-APP-1
- previous stable HEAD = ab96a86 fix stale marker cleanup handoff sync marker
- validation = ALL CHECKS PASSED
- pytest = 2002 passed
- git status = clean
- origin/main = synced

Next branch:
sidecar-artifact-lifecycle-registry-app-1

First stage:
ARTIFACT-LIFECYCLE-D1 sidecar boundary and lifecycle registry contract

Boundary:
read-only / index-only / sidecar-only / operator review required.
No P48. No core mutation. No tag. No release. No deploy.

---

## Completed Phase: ARTIFACT-LIFECYCLE-REGISTRY-APP-1

Status:
completed, merged into main, validated, pushed, and clean.

Main merge commit:
0601415 merge ARTIFACT-LIFECYCLE-REGISTRY-APP-1 into main

Final sidecar commit:
d7f008b add ARTIFACT-LIFECYCLE-D6 final handoff closeout

Validation:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 2040 passed

git status:
clean

origin/main:
synced

Purpose:
Create a global artifact lifecycle registry sidecar.

Completed stages:
- D1 sidecar boundary and lifecycle registry contract
- D2 lifecycle transition policy
- D3 artifact state snapshot index
- D4 registry summary
- D5 registry packet
- D6 final handoff closeout

Boundary:
paper-only / local-only / read-only / sidecar-only / index-only / operator review required.

Strictly forbidden:
no P48, no core mutation, no source artifact mutation, no artifact status auto-repair, no evidence backfill, no auto-pass, no tag, no release, no deploy.

## Approved Next Phase

VALIDATION-BASELINE-REGISTRY-APP-1 is approved as the next sidecar phase.

Start from main only after read-only verification.

Expected baseline before branch creation:
- branch = main
- latest HEAD includes approval commit for VALIDATION-BASELINE-REGISTRY-APP-1
- previous stable HEAD = bbffce5 add ARTIFACT-LIFECYCLE-REGISTRY-APP-1 final current state
- validation = ALL CHECKS PASSED
- pytest = 2040 passed
- git status: clean
- origin/main: synced

Next branch:
sidecar-validation-baseline-registry-app-1

First stage:
VALIDATION-BASELINE-D1 sidecar boundary and validation baseline registry contract

Boundary:
read-only / index-only / sidecar-only / operator review required.
No validation result fabrication. No pass count fabrication. No P48. No core mutation. No tag. No release. No deploy.
Architecture gap review or explicitly approved next phase only.

---

## Completed Phase: VALIDATION-BASELINE-REGISTRY-APP-1

Status:
completed, merged into main, validated, pushed, and clean.

Main merge commit:
b6c8525 merge VALIDATION-BASELINE-REGISTRY-APP-1 into main

Final sidecar commit:
e98c3d2 add VALIDATION-BASELINE-D6 final handoff closeout

Validation:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 2082 passed

git status:
clean

origin/main:
synced

Purpose:
Create a validation baseline registry sidecar.

Completed stages:
- D1 sidecar boundary and validation baseline registry contract
- D2 validation run record model
- D3 validation baseline snapshot index
- D4 validation baseline summary
- D5 validation baseline packet
- D6 final handoff closeout

Boundary:
paper-only / local-only / read-only / sidecar-only / index-only / operator review required.

Strictly forbidden:
no validation result fabrication, no pass count fabrication, no P48, no core mutation, no source artifact mutation, no evidence backfill, no auto-pass, no tag, no release, no deploy.

Architecture gap review or explicitly approved next phase only.

---

## Latest Control Center V2 AI Update

Latest main before this handoff sync:
- 9d9b859 record FCF V2 AI intelligence layer in control center

V2 direction:
- FCF V2 is not an automatic trading system.
- FCF V2 is a local paper-only research dossier system.
- AI is a controlled research fellow, not a trader.
- AI must be traceable, challengeable, reviewable, and archivable.

Approved next route:
1. AI-CONTEXT-EVIDENCE-CONTRACT-APP-1
2. AI-CONTRARIAN-CHALLENGE-APP-1
3. DASHBOARD-CONTRADICTION-SCANNER-APP-1
4. MARKET-NARRATIVE-CONTEXT-APP-1
5. AI-SCENARIO-SIMULATION-APP-1
6. AI-ORCHESTRATION-ROADMAP-APP-1

Do not start Dashboard Scanner before AI input/output evidence contract and Challenge AI are stable.
Do not start full AI orchestration before previous V2 stages are stable.
