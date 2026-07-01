# P11-D6 - Regression Stability Gate

P11-D6 新增 regression stability gate。

新增文件：

- docs/105_p11_regression_stability_gate.md
- fcf/regression/regression_stability_gate.py
- tests/test_p11_regression_stability_gate.py

## 1. 目的

regression stability gate 用于判断当前 paper-only / non-production regression package 是否稳定到可以进入 P11-D7 acceptance smoke。

gate_version = 0.1.0
phase = P11
day = P11-D6
status = active

该 gate 用于：

- release readiness
- regression stability review
- operator handoff validation
- long-term maintainability
- paper-only safety review

该 gate 不用于：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 钱包私钥读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. 新增入口

新增入口：

- evaluate_regression_stability_gate

输入：

- python scripts/run_p10_dify_safe_package_summary.py 的输出 dict

输出：

- status
- gate
- gate_version
- ok
- checks
- violations
- ready_for_p11_d7_acceptance_smoke
- safe_boundary

## 3. 稳定性检查项

必须通过：

- package summary status completed
- package_summary.ready_for_p10_d10_bridge_plan true
- package_summary.p10_acceptance_completed true
- package_summary.dify_global_regression_ok true
- package_summary.operator_response_passed true
- package_summary.operator_review_required true
- package_summary.ready_for_operator_review true
- package_summary.deliverables_all_present true
- package_summary.safe_boundary_ok true
- deliverables.all_present true
- deliverables.present_count equals deliverables.deliverable_count
- Dify adapter ok true
- operator review response type global_regression_passed
- safe_boundary.paper_only true
- safe_boundary.real_order false
- safe_boundary.real_execution false
- safe_boundary.real_exchange_api false
- safe_boundary.real_money_impact false
- safe_boundary.operator_review_required true
- safe_boundary.auto_live_trading false
- safe_boundary.bypass_operator_review false
- safe_boundary.bypass_policy_risk_safe_boundary false

## 4. 失败规则

如果任何检查 failed：

- status = failed
- ok = false
- ready_for_p11_d7_acceptance_smoke = false
- 必须停止继续操作
- 不进入 P11-D7
- 不解释为交易信号
- 不连接真实交易所
- 不配置 API key
- 不读取钱包私钥
- 不尝试真实下单
- 回到 docs/94_p10_failure_triage_guide.md

## 5. 安全边界

P11-D6 不接真实交易所 API。
P11-D6 不保存真实 API key。
P11-D6 不读取钱包私钥。
P11-D6 不真实下单。
P11-D6 不读取真实账户余额。
P11-D6 不读取真实仓位。
P11-D6 不声明真实成交。
P11-D6 不声明真实资金影响。
P11-D6 不配置 CI secret。
P11-D6 不做 production deployment。
P11-D6 不自动实盘交易。
P11-D6 不自动绕过人工复核。
P11-D6 不绕过 policy / risk / safe_boundary。
P11-D6 不把 paper-only passed 解释成真实交易信号。
P11-D6 不把 paper-only passed 解释成真实成交。

## 6. P11-D6 验收标准

P11-D6 完成需要满足：

- 新增 docs/105_p11_regression_stability_gate.md
- 新增 fcf/regression/regression_stability_gate.py
- 新增 tests/test_p11_regression_stability_gate.py
- gate 能通过当前 P10 package summary
- gate 能识别 failed summary
- gate 能识别 safe_boundary violation
- gate 输出 ready_for_p11_d7_acceptance_smoke=true
- python main.py 输出 events_recorded: 8
- python scripts/run_p10_dify_safe_package_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P11-D7：Phase 11 acceptance smoke。
