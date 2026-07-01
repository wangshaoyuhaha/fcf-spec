# P5-D1 - Paper-only Sandbox Execution Boundary Plan

## 1. 目的

P5-D1 开始进入 Phase 5。

Phase 5 的第一目标是定义 paper-only sandbox execution boundary。

当前系统已经具备：

- raw market input schema
- schema error catalog
- market input pipeline schema integration
- local_market_input_api
- dify_http_adapter
- dify_response_templates
- Dify smoke runners
- multi-asset fixture
- multi-asset success smoke
- multi-asset error smoke

下一步需要明确：

- paper order 是什么
- real order 是什么
- sandbox execution 允许做什么
- sandbox execution 禁止做什么
- Dify 是否能触达执行边界
- sandbox execution 如何进入 EventStore
- sandbox execution 如何 Replay

## 2. 当前安全原则

P5-D1 继续保持以下安全原则：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核
- 不让 Dify 直接触达真实执行器
- 不把模拟执行伪装成真实成交
- 所有 sandbox execution 必须进入 EventStore
- 所有 sandbox execution 必须可 Replay

## 3. Paper Order 定义

Paper order 是模拟订单。

Paper order 可以包含：

- order_id
- correlation_id
- asset_class
- symbol
- venue
- market_type
- side
- order_type
- quantity
- price
- time_in_force
- source
- created_at
- risk_context
- metadata

Paper order 只能用于：

- sandbox execution
- replay
- audit
- strategy dry-run
- Dify workflow 演示
- risk / policy 测试

Paper order 不能用于：

- 真实交易所下单
- 真实账户资金变动
- 真实仓位变动
- 真实成交确认
- 真实收益展示

## 4. Real Order 定义

Real order 是会进入真实交易所或真实经纪商系统的订单。

Real order 可能导致：

- 真实下单
- 真实成交
- 真实资金变化
- 真实仓位变化
- 真实风险暴露
- 真实法律和合规责任

当前 FCF Spec 阶段不支持 real order。

当前禁止：

- 生成 real order
- 发送 real order
- 保存真实交易所 API key
- 调用真实交易所 API
- 调用真实经纪商 API
- 用 Dify 发起真实交易
- 把 paper execution 说成 real execution

## 5. Sandbox Execution 定义

Sandbox execution 是本地模拟执行。

Sandbox execution 可以做：

- 接收 paper order
- 模拟 fill
- 模拟 reject
- 模拟 partial fill
- 生成 sandbox execution event
- 写入 EventStore
- 被 ReplayEngine 回放
- 生成稳定 summary dict

Sandbox execution 不可以做：

- 调用真实交易所 API
- 调用真实经纪商 API
- 使用真实 API key
- 读取钱包私钥
- 真实下单
- 修改真实账户余额
- 修改真实仓位
- 生成真实成交回报

## 6. Dify 与执行边界

Dify 在 Phase 5 中只能做：

- 收集用户输入
- 构造 paper intent
- 调用受控 wrapper
- 展示 sandbox summary
- 展示安全边界说明
- 展示错误信息

Dify 禁止做：

- 直接调用真实执行器
- 直接生成 real order
- 直接接真实交易所 API
- 保存真实 API key
- 读取钱包私钥
- 真实下单
- 绕过 policy / risk
- 绕过 EventStore
- 绕过 ReplayEngine
- 把 sandbox execution 说成真实成交

## 7. 建议事件类型

Phase 5 后续可以新增以下事件：

- fcf.paper.order.proposed
- fcf.paper.order.validated
- fcf.paper.order.rejected
- fcf.sandbox.execution.simulated
- fcf.sandbox.execution.filled
- fcf.sandbox.execution.partial_filled
- fcf.sandbox.execution.rejected
- fcf.sandbox.execution.replayed

P5-D1 只定义规划，不实现这些事件。

## 8. 建议模块边界

后续可以新增：

- fcf/paper/
- fcf/paper/paper_order_schema.py
- fcf/paper/sandbox_execution_engine.py
- fcf/api/paper_execution_api.py
- tests/test_paper_order_schema.py
- tests/test_sandbox_execution_engine.py
- tests/test_paper_execution_api.py

当前 P5-D1 不创建这些代码模块。

## 9. Stable Response Dict 要求

未来 paper / sandbox wrapper 仍然必须返回稳定 response dict：

{
  "ok": true,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {}
}

错误时：

{
  "ok": false,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": {
    "type": "ValueError",
    "message": "error detail"
  },
  "data": null
}

## 10. Replay 要求

未来 sandbox execution 必须满足：

- 所有 paper order 进入 EventStore
- 所有 sandbox execution result 进入 EventStore
- ReplayEngine 可以回放 sandbox execution events
- replay summary 可校验 event_count
- replay summary 可校验 event_names
- replay summary 可校验 sequence order

## 11. 审计要求

Sandbox execution 必须可审计。

最小审计字段：

- event_id
- event_name
- event_time
- sequence_id
- source_module
- correlation_id
- causation_id
- payload
- metadata

审计中必须明确：

- execution_mode = paper
- real_order = false
- real_exchange_api = false
- real_money_impact = false

## 12. 用户可见说明

Dify 或任何用户界面展示 sandbox execution 时，必须说明：

- 这是模拟执行
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化
- 结果只用于测试、回放和审计

禁止说法：

- 已经真实买入
- 已经真实卖出
- 已经在交易所成交
- 已经产生真实收益
- 已经修改真实仓位

## 13. P5-D1 验收标准

P5-D1 完成需要满足：

- 新增 docs/37_p5_paper_sandbox_execution_boundary_plan.md
- README 更新 P5-D1 状态
- PROJECT_STATE 更新 P5-D1 状态
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 通过
- 不接真实交易所 API
- 不真实下单

## 14. 下一步建议

下一步进入 P5-D2：paper order schema module。

建议新增：

- fcf/paper/__init__.py
- fcf/paper/paper_order_schema.py
- tests/test_paper_order_schema.py

P5-D2 目标：

- 定义 paper order required fields
- 定义 side normalization
- 定义 order_type normalization
- 定义 quantity positive check
- 定义 price optional positive check
- 明确 real_order false
- 明确 execution_mode paper
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

