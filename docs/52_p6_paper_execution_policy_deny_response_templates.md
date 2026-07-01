# P6-D4 - Paper Execution Policy Deny Response Templates

## 1. 目的

P6-D4 扩展 paper execution user-facing response templates。

P6-D3 已经把 paper execution policy gate 接入 paper_execution_api。

P6-D4 的目标是：

- 当 paper execution 返回 PolicyDeny 时，用户可见回复进入 policy_deny 分支
- 不把 policy deny 当作普通 schema error
- 不把 policy deny 说成交易所拒单
- 不把 policy deny 说成真实下单失败
- 明确没有连接真实交易所
- 明确没有真实下单
- 明确没有真实资金变化
- 明确没有真实仓位变化

## 2. 新增 response_type

新增：

- paper_policy_deny

已有：

- paper_fill_success
- paper_reject_success
- paper_execution_error
- paper_safety_refusal

## 3. Policy Deny 用户可见要求

当 error.type = PolicyDeny 时，Dify 必须告诉用户：

- 系统 policy gate 拒绝了该请求
- 这不是交易所真实拒单
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化
- 需要移除危险意图后重新提交 paper / sandbox 请求

## 4. Policy Deny 与其他失败的区别

PolicyDeny：

- policy gate 拒绝
- 不进入 sandbox execution engine
- 不产生 sandbox fill
- 不产生 sandbox reject
- 不是真实交易所拒单

paper_execution_error：

- 输入校验失败或普通执行错误
- 没有通过 paper execution wrapper
- 没有真实下单

paper_safety_refusal：

- Dify 或 UI 层直接拒绝危险 intent
- 通常不调用 adapter

## 5. 安全边界

P6-D4 不接真实交易所 API。
P6-D4 不保存真实 API key。
P6-D4 不读取钱包私钥。
P6-D4 不真实下单。
P6-D4 不把 policy deny 伪装成交易所真实拒单。
P6-D4 不把 paper execution 伪装成 real execution。

## 6. 验收标准

P6-D4 完成需要满足：

- 新增 docs/52_p6_paper_execution_policy_deny_response_templates.md
- 修改 fcf/api/paper_execution_response_templates.py
- 新增 tests/test_paper_execution_policy_deny_response_templates.py
- PolicyDeny 渲染为 paper_policy_deny
- policy deny response 明确不是交易所真实拒单
- 普通 ValueError 仍渲染为 paper_execution_error
- safety refusal 仍渲染为 paper_safety_refusal
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

