# P10-D7 - Phase 10 Acceptance Smoke

P10-D7 新增 Phase 10 acceptance smoke。

新增文件：

- docs/96_p10_acceptance_smoke.md
- scripts/run_p10_acceptance_smoke.py
- tests/test_p10_acceptance_smoke.py

## 1. 目的

P10-D7 汇总验证 Phase 10 第一轮已完成能力：

- P9 global regression summary
- Dify global regression adapter
- operator review response templates
- paper-only operator runbook
- failure triage guide
- Dify workflow node contract

## 2. 覆盖阶段

P10-D7 覆盖：

- P10-D1：Dify-safe paper operations plan
- P10-D2：global regression Dify adapter contract
- P10-D3：operator review response templates
- P10-D4：paper-only operator runbook
- P10-D5：failure triage guide
- P10-D6：Dify workflow node contract document
- P10-D7：Phase 10 acceptance smoke

## 3. 新增命令

新增命令：

- python scripts/run_p10_acceptance_smoke.py

## 4. 输出字段

输出字段：

- status
- runner
- runner_version
- acceptance_summary
- components
- safe_boundary

## 5. 验收目标

P10-D7 验收目标：

- P9 global regression summary status completed
- Dify global regression adapter ok true
- operator review response type global_regression_passed
- operator review required true
- ready_for_operator_review true
- P10 docs readiness true
- safe_boundary ok true
- ready_for_p10_d8_closeout true

## 6. 安全边界

P10-D7 不接真实交易所 API。
P10-D7 不保存真实 API key。
P10-D7 不读取钱包私钥。
P10-D7 不真实下单。
P10-D7 不读取真实账户余额。
P10-D7 不读取真实仓位。
P10-D7 不声明真实成交。
P10-D7 不声明真实资金影响。
P10-D7 不配置 CI secret。
P10-D7 不做 production deployment。
P10-D7 不自动实盘交易。
P10-D7 不自动绕过人工复核。
P10-D7 不绕过 policy / risk / safe_boundary。

下一步：

P10-D8：Phase 10 closeout。
