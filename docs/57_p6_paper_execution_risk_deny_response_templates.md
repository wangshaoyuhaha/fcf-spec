# P6-D9 - Paper Execution Risk Deny Response Templates

## 1. 目的

P6-D9 扩展 paper execution user-facing response templates。

P6-D8 已经把 paper execution risk guardian 接入 paper_execution_api。

P6-D9 的目标是：

- 当 paper execution 返回 RiskDeny 时，用户可见回复进入 risk_deny 分支
- 不把 risk deny 当作普通 schema error
- 不把 risk deny 说成交易所拒单
- 不把 risk deny 说成真实下单失败
- 明确没有连接真实交易所
- 明确没有真实下单
- 明确没有真实资金变化
- 明确没有真实仓位变化

## 2. 新增 response_type

新增：

- paper_risk_deny

已有：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_execution_error
- paper_safety_refusal

## 3. Risk Deny 用户可见要求

当 error.type = RiskDeny 时，Dify 必须告诉用户：

- paper / sandbox 风控拒绝了该模拟执行
- 这不是交易所真实拒单
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化
- 需要降低 quantity / notional 或补充 risk_context 后重新提交

## 4. Risk Deny 与其他失败的区别

RiskDeny：

- risk guardian 拒绝
- policy gate 已通过
- 不进入 sandbox execution engine
- 不产生 sandbox fill
- 不产生 sandbox reject
- 不是真实交易所拒单

PolicyDeny：

- policy gate 拒绝
- 常见原因是真实执行、保存 API key、读取私钥、绕过风控、强制执行

paper_execution_error：

- 输入校验失败或普通执行错误
- 例如 quantity <= 0
- 没有真实下单

paper_safety_refusal：

- Dify 或 UI 层直接拒绝危险 intent
- 通常不调用 adapter

## 5. 安全边界

P6-D9 不接真实交易所 API。
P6-D9 不保存真实 API key。
P6-D9 不读取钱包私钥。
P6-D9 不真实下单。
P6-D9 不把 risk deny 伪装成交易所真实拒单。
P6-D9 不把 paper execution 伪装成 real execution。

## 6. 验收标准

P6-D9 完成需要满足：

- 新增 docs/57_p6_paper_execution_risk_deny_response_templates.md
- 修改 fcf/api/paper_execution_response_templates.py
- 新增 tests/test_paper_execution_risk_deny_response_templates.py
- RiskDeny 渲染为 paper_risk_deny
- risk deny response 明确不是交易所真实拒单
- PolicyDeny 仍渲染为 paper_policy_deny
- ValueError 仍渲染为 paper_execution_error
- safety refusal 仍渲染为 paper_safety_refusal
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

