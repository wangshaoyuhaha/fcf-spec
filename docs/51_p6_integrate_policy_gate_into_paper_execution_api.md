# P6-D3 - Integrate Paper Execution Policy Gate Into Paper Execution API

## 1. 目的

P6-D3 将 P6-D2 的 paper execution policy gate 接入 paper_execution_api。

目标：

- paper execution API 不能绕过 policy gate
- Dify paper execution adapter 不能绕过 policy gate
- policy denied 时不进入 sandbox execution engine
- policy denied 时不写入 sandbox execution event
- policy denied 时返回 stable response dict

P6-D3 不接真实交易所 API。
P6-D3 不保存真实 API key。
P6-D3 不读取钱包私钥。
P6-D3 不真实下单。

## 2. 接入位置

修改文件：

- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py

新增测试：

- tests/test_paper_execution_api_policy_integration.py

## 3. 当前调用链

Dify style request
-> route_dify_paper_execution_request
-> handle_paper_execution
-> evaluate_paper_execution_policy
-> if denied: return ok=false
-> if allowed: execute_sandbox_order_with_eventstore
-> EventStore
-> ReplayEngine

## 4. Policy Deny 行为

当 policy gate 返回 denied：

paper_execution_api 返回：

{
  "ok": false,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": {
    "type": "PolicyDeny",
    "message": "..."
  },
  "data": null
}

该情况下：

- 不进入 sandbox execution engine
- 不生成 sandbox fill
- 不生成 sandbox reject
- 不写入 sandbox execution event
- 不真实下单

## 5. 当前 policy_context

handle_paper_execution 新增可选参数：

- policy_context

Dify paper execution adapter 会把 body 作为 policy_context 传入。

因此 policy gate 可以检查：

- body 顶层字段
- body.metadata
- body.raw_order
- body.raw_order.metadata

## 6. 兼容性说明

P6-D3 会清理旧 safe sample 中的危险字段：

- real_order: true
- real_exchange_api: true
- real_money_impact: true

原因：

P6-D2 后这些字段已经成为 policy deny 信号。
safe sample 不应再带这些字段。
paper_order_schema 仍然会强制输出：

- real_order = false
- real_exchange_api = false
- real_money_impact = false

## 7. 安全边界

P6-D3 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不允许 Dify 绕过 policy gate
- 不把 paper execution 伪装成 real execution

## 8. 验收标准

P6-D3 完成需要满足：

- paper_execution_api 调用 evaluate_paper_execution_policy
- Dify adapter 传入 policy_context
- safe paper execution 仍返回 200 / ok true
- raw_order.real_order=true 返回 PolicyDeny
- policy_context.save_api_key_requested=true 返回 PolicyDeny
- Dify adapter top-level bypass_risk_requested=true 返回 422 / PolicyDeny
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

