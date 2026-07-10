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

---

当前最新主控状态：CONTROL-CENTER-V2-AI-INTELLIGENCE-LAYER-SPEC-APP-1

继续 FCF / BTC finance platform 金融市场模型项目。只做 FCF，不要切到足球项目。
最新主控已确认：FCF V2 = 确定性金融计算引擎 + 可控 AI 智能认知层。
AI 是高级金融研究员，不是交易员、执行器、下单系统、仓位管理器或收益保证器。
下一阶段不要直接做 Dashboard Scanner。
下一阶段应先讨论并批准 AI-CONTEXT-EVIDENCE-CONTRACT-APP-1。
后续顺序：AI evidence contract -> contrarian challenge -> dashboard contradiction scanner -> market narrative context -> scenario simulation -> orchestration roadmap。
保持 core frozen、sidecar-only、paper-only、local-only、read-only、operator review required。
禁止真实交易、真实执行、broker/exchange API、API key、wallet private key、real account、real position、buy/sell/order、自动仓位、自动组合动作、收益保证、tag、release、deploy。

---

当前最新主控状态：CONTROL-CENTER-V2-AI-HARDENING-GAPS-APP-1

继续 FCF / BTC finance platform 金融市场模型项目。
最新主控补充：进入 AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 前，必须保留 V2 AI 规划硬化缺口。
必须覆盖：AI 输入来源分级、AI 输出质量评价、prompt / model version governance、Challenge AI 有效性质检、Human Review 状态机、UI 风险暴露规则、AI 失败模式、多资产 AI schema 分层。
不允许只写空文档。V2 sidecar 必须有 contract、可运行产物、测试、artifact、handoff、final current state。
保持 core frozen、sidecar-only、paper-only、local-only、read-only、operator review required。

---

当前最新主控状态：CONTROL-CENTER-V2-AI-DELIVERY-FOUNDATION-APP-1

继续 FCF / BTC finance platform 金融市场模型项目。
最新主控补充：进入 AI-CONTEXT-EVIDENCE-CONTRACT-APP-1 前，必须保留 6 个 V2 AI 交付基础点。
必须覆盖：ADR 架构决策记录、AI 评估样例库、Research Artifact Package 标准、Human Override Ledger、AI 降级模式、资产类型隔离。
不允许只写空文档。V2 sidecar 必须有 contract、可运行产物、测试样例、研究包输出、artifact、handoff、final current state。
保持 core frozen、sidecar-only、paper-only、local-only、read-only、operator review required。

---

当前最新主控状态：CONTROL-CENTER-V2-AI-RUNTIME-OPERATIONS-GUARD-APP-1

继续 FCF / BTC finance platform 金融市场模型项目。
最新主控补充：CONTROL-CENTER-V2-AI-RUNTIME-OPERATIONS-GUARD-APP-1 是进入 V2 AI 开发前的最后一个纯规划补丁。
必须保留：Source Trust Level、research_run_id、AI 超时/重试/降级策略、本地隐私边界、Golden Path Demo、Stop Rule / Freeze Rule。
下一阶段必须进入 AI-CONTEXT-EVIDENCE-CONTRACT-APP-1，不再继续无限补规划。
保持 core frozen、sidecar-only、paper-only、local-only、read-only、operator review required。

<!-- BEGIN AI-EVALUATION-SAMPLE-LIBRARY-APP-1 FINAL SYNC -->
## Current handoff

Project:
FCF / Financial Cognitive Framework

Repository:
wangshaoyuhaha/fcf-spec

Local path:
C:\Users\Admin\Desktop\btc_finance_platform

Current verified state:
- branch: main
- HEAD and origin/main: 59f8b85
- latest completed phase: AI-EVALUATION-SAMPLE-LIBRARY-APP-1
- D1-D6 completed
- final current state completed
- merged and pushed
- run_all_checks passed
- pytest 2273 passed
- git status clean
- no tag / no release / no deploy

Mandatory boundaries:
paper-only / local-only / read-only / sidecar-only /
operator review required.

P1-P47 core is frozen.
Do not create P48 or mutate core.
Do not build a complete AI Orchestrator.
Do not connect news feeds.
Do not add real trading, execution, broker or exchange APIs,
credentials, wallet keys, real accounts, real positions,
automatic position sizing or automatic portfolio actions.

Next action:
Perform architecture review first.
No next development phase is currently approved.
<!-- END AI-EVALUATION-SAMPLE-LIBRARY-APP-1 FINAL SYNC -->

<!-- AI-EVALUATION-DRIFT-REVIEW-APP-1-PROMPT -->

## ACTIVE PHASE OVERRIDE

You are continuing the FCF project on:

AI-EVALUATION-DRIFT-REVIEW-APP-1

Repository:
wangshaoyuhaha/fcf-spec

Local path:
C:\Users\Admin\Desktop\btc_finance_platform

Approved branch:
sidecar-ai-evaluation-drift-review-app-1

Main baseline before branch creation:
f5d0b94

Execution requirements:
- Chinese chat replies
- complete copyable PowerShell commands
- ASCII English for code, tests, and documents
- execute D1-D6 sequentially
- validate, commit, and push every stage
- report commit, push, validation, and git status
- keep the working tree clean
- write logs to Desktop
- do not use exit

Permanent safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- P1-P47 core frozen
- no P48
- no core mutation
- no live model invocation
- no prompt execution
- no AI orchestrator
- no automatic evaluation acceptance
- no automatic model or prompt selection
- no automatic winner selection
- no trade action
- no real execution
- no broker or exchange connection
- no API keys or wallet keys
- no tag, release, or deploy without explicit approval

Next action:
Start AI-EVALUATION-DRIFT-REVIEW-APP-1 D1 boundary contract.
<!-- AI-EVALUATION-DRIFT-REVIEW-APP-1-FINAL-PROMPT -->

## FINAL CURRENT STATE OVERRIDE

This section overrides all earlier active-phase instructions.

You are continuing the FCF / Financial Cognitive Framework project.

Repository:
wangshaoyuhaha/fcf-spec

Local path:
C:\Users\Admin\Desktop\btc_finance_platform

Current branch:
main

Current HEAD:
7eef90a

Current origin/main:
7eef90a

Latest completed phase:
AI-EVALUATION-DRIFT-REVIEW-APP-1

Latest phase state:
COMPLETED / MERGED / VALIDATED / PUSHED / CLEAN

Final Current State commit:
8ddd692

Main merge commit:
7eef90a

Validation:
- python scripts/run_all_checks.py = ALL CHECKS PASSED
- python -m pytest -q = 2545 passed
- git status = clean
- origin/main = synchronized

Current active development phase:
NONE

Next phase:
NOT SELECTED

The next window must first:
1. Verify main, origin/main, and clean status.
2. Read docs/FCF_PROJECT_CONTROL_CENTER.md.
3. Perform architecture review.
4. Wait for explicit operator approval before creating a branch or
   starting a new D1-D6 phase.

Do not automatically resume the earlier Drift active-phase instruction.

Permanent safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- deterministic-only
- operator review required
- P1-P47 core frozen
- no P48
- no core mutation
- no live model invocation
- no prompt execution
- no AI orchestrator execution
- no automatic drift approval or rejection
- no automatic rollback
- no automatic model or prompt switching
- no operator review bypass
- no trade action
- no real execution
- no broker or exchange connection
- no API keys or wallet keys
- no tag, release, or deploy without explicit approval