# P6-D10 - Dify Paper Execution Response Smoke Includes Risk Deny

## 1. 目的

P6-D10 更新 Dify paper execution response integration smoke。

P6-D9 已经新增 paper_risk_deny 用户可见模板。

P6-D10 的目标是让 smoke runner 明确覆盖：

- fill success
- reject success
- policy deny
- risk deny
- execution error
- safety refusal

并明确区分：

- policy_deny：policy gate 拒绝，不是交易所拒单
- risk_deny：risk guardian 拒绝，不是交易所拒单
- execution_error：输入校验失败或普通执行错误
- safety_refusal：Dify / UI 层直接拒绝危险 intent

## 2. 修改文件

修改：

- scripts/run_dify_paper_execution_response_smoke.py
- tests/test_dify_paper_execution_response_smoke.py

新增：

- docs/58_p6_dify_paper_execution_response_smoke_risk_deny.md

## 3. 新增 smoke case

新增 case：

- risk_deny_to_user_paper_risk_deny

该 case 使用：

- risk_context.max_quantity = 0.1
- raw_order.quantity = 0.25

预期 adapter 返回：

- http_status = 422
- ok = false
- api = paper_execution_api
- error.type = RiskDeny

预期 user response 返回：

- response_type = paper_risk_deny
- title = 纸面模拟执行被风控规则拒绝

## 4. 与其他失败的区别

policy_deny：

- policy gate 拒绝
- 不进入 risk guardian
- 不是交易所真实拒单

risk_deny：

- policy gate 已通过
- risk guardian 拒绝
- 不进入 sandbox execution engine
- 不是交易所真实拒单

execution_error：

- 输入校验失败
- 例如 quantity = -1
- 没有真实下单

safety_refusal：

- Dify / UI 层直接拒绝真实执行 intent
- 通常不调用 adapter

## 5. 安全边界

P6-D10 不接真实交易所 API。
P6-D10 不保存真实 API key。
P6-D10 不读取钱包私钥。
P6-D10 不真实下单。
P6-D10 不把 policy deny / risk deny 伪装成交易所真实拒单。
P6-D10 不把 paper execution 伪装成 real execution。

## 6. 验收标准

P6-D10 完成需要满足：

- smoke runner case_count 从 5 变为 6
- 覆盖 risk_deny_to_user_paper_risk_deny
- fill 仍为 paper_fill_success
- reject 仍为 paper_reject_success
- policy deny 仍为 paper_policy_deny
- bad order 仍为 paper_execution_error
- real execution intent 仍为 paper_safety_refusal
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

