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
You are continuing the FCF / Financial Cognitive Framework project.

Project:
FCF / Financial Cognitive Framework
Repository: wangshaoyuhaha/fcf-spec
Local path: C:\Users\Admin\Desktop\btc_finance_platform
Branch: main

Language:
Reply in Chinese.
Keep responses short and direct.
For PowerShell, provide complete copyable commands.
Do not ask the user to manually open files.
Prefer PowerShell for file writes.
At each phase end, report commit, push, validation, and git status.
Do not tag, release, or deploy without explicit approval.

Current latest true state:
ARCHIVE-CORRELATION-ROLLUP-APP-1 is completed, merged into main, validated, pushed, and clean.

Latest main merge commit:
59ba8e7 merge ARCHIVE-CORRELATION-ROLLUP-APP-1 into main

Final sidecar commit:
fb05e00 fix ARCHIVE-CORRELATION-D6 final handoff tests

Validation:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 2002 passed

git status:
clean

origin/main:
synced

no tag / no release / no deploy

Project positioning:
FCF is a local multi-asset financial research governance platform.
It is not BTC-only.
It is not a trading execution system.

Core architecture:
P1-P47 core is frozen.
No P48.
New capability must use sidecar extension.
Preserve core frozen + sidecar extension.
Preserve one-way dependency.
No core mutation.

Latest completed sidecar purpose:
ARCHIVE-CORRELATION-ROLLUP-APP-1 upgrades correlation_id from passive field preservation into a read-only full-chain evidence index.

It indexes existing chain links:
data_snapshot, candidate, ai_explanation, ui_packet, review_packet, archive_packet, handoff, final_state.

It only marks:
COMPLETE, INCOMPLETE, STALE, UNRESOLVED.

It must not:
auto-pass, auto-fill correlation_id, backfill evidence, generate placeholder review, create UI dashboard panel, touch core, create P48.

Safety boundary:
paper-only / local-only / read-only / sidecar-only / operator review required.

Strictly forbidden:
real trading
real execution
broker/exchange API
API key
wallet private key
real account
real position
buy/sell/order
automatic position sizing
automatic portfolio action
profit guarantee
tag
release
deploy

Next step:
Return to control center planning and approve the next sidecar only after read-only verification.

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
