# P5-D6 - Dify Paper Execution Contract and Local Adapter Planning

## 1. 目的

P5-D6 定义 Dify 调用 paper execution API wrapper 的契约。

当前已完成：

- paper order schema
- sandbox execution engine
- sandbox execution EventStore / Replay integration
- paper execution API wrapper

P5-D6 只做 Dify paper execution contract 文档和本地 adapter 规划。

P5-D6 不接真实交易所 API。
P5-D6 不保存真实 API key。
P5-D6 不读取钱包私钥。
P5-D6 不真实下单。
P5-D6 不让 Dify 触达真实执行器。

## 2. 当前可调用 Wrapper

当前 wrapper：

- fcf/api/paper_execution_api.py

当前函数：

- describe_paper_execution_api
- handle_paper_execution

当前底层调用：

- fcf.paper.sandbox_execution_engine.execute_sandbox_order_with_eventstore

## 3. Stable Response Dict

成功响应：

{
  "ok": true,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {}
}

失败响应：

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

## 4. Dify 输入 JSON：simulated_fill

Dify paper execution simulated_fill 请求示例：

{
  "handler": "handle_paper_execution",
  "simulation_mode": "simulated_fill",
  "fill_price": "60050.5",
  "filled_quantity": "0.25",
  "output_path": "runtime/events/dify_paper_execution.jsonl",
  "raw_order": {
    "asset_class": "crypto",
    "symbol": "BTCUSDT",
    "venue": "binance",
    "market_type": "perp",
    "side": "buy",
    "order_type": "limit",
    "quantity": "0.25",
    "price": "60050.5",
    "time_in_force": "gtc",
    "source": "dify_paper_execution",
    "correlation_id": "dify-paper-execution-001",
    "metadata": {
      "note": "paper only"
    }
  }
}

## 5. Dify 输入 JSON：simulated_reject

Dify paper execution simulated_reject 请求示例：

{
  "handler": "handle_paper_execution",
  "simulation_mode": "simulated_reject",
  "reject_reason": "policy denied in paper sandbox",
  "output_path": "runtime/events/dify_paper_reject.jsonl",
  "raw_order": {
    "asset_class": "crypto",
    "symbol": "BTCUSDT",
    "venue": "binance",
    "market_type": "perp",
    "side": "buy",
    "order_type": "limit",
    "quantity": "0.25",
    "price": "60050.5",
    "time_in_force": "gtc",
    "source": "dify_paper_execution",
    "correlation_id": "dify-paper-reject-001",
    "metadata": {
      "note": "paper only"
    }
  }
}

## 6. 成功输出 JSON：simulated_fill

成功输出示例：

{
  "ok": true,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {
    "status": "completed",
    "engine": "sandbox_execution_engine",
    "engine_version": "0.1.0",
    "simulation_mode": "simulated_fill",
    "execution_status": "filled",
    "event_name": "fcf.sandbox.execution.filled",
    "event_count": 1,
    "event_names": [
      "fcf.sandbox.execution.filled"
    ],
    "execution_mode": "paper",
    "real_order": false,
    "real_execution": false,
    "real_exchange_api": false,
    "real_money_impact": false,
    "replay": {
      "status": "completed",
      "event_count": 1
    }
  }
}

## 7. 成功输出 JSON：simulated_reject

成功输出示例：

{
  "ok": true,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {
    "status": "completed",
    "engine": "sandbox_execution_engine",
    "engine_version": "0.1.0",
    "simulation_mode": "simulated_reject",
    "execution_status": "rejected",
    "event_name": "fcf.sandbox.execution.rejected",
    "event_count": 1,
    "event_names": [
      "fcf.sandbox.execution.rejected"
    ],
    "execution_mode": "paper",
    "real_order": false,
    "real_execution": false,
    "real_exchange_api": false,
    "real_money_impact": false,
    "replay": {
      "status": "completed",
      "event_count": 1
    }
  }
}

## 8. 错误输出 JSON

错误输出示例：

{
  "ok": false,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": {
    "type": "ValueError",
    "message": "quantity must be greater than 0"
  },
  "data": null
}

Dify 收到 ok=false 时必须进入 error branch。

## 9. Dify Workflow 推荐节点

推荐节点：

1. Start
2. User Intent Parser
3. Paper Order Field Parser
4. Required Field Check
5. Safety Boundary Check
6. Build Paper Execution Request
7. Paper Execution API Call
8. IF response.ok
9. Paper Success Summary
10. Paper Error Summary
11. Safety Refusal Summary
12. End

## 10. Dify 字段映射

字段映射：

- workflow_run_id -> raw_order.correlation_id
- asset_class -> raw_order.asset_class
- symbol -> raw_order.symbol
- venue -> raw_order.venue
- market_type -> raw_order.market_type
- side -> raw_order.side
- order_type -> raw_order.order_type
- quantity -> raw_order.quantity
- price -> raw_order.price
- time_in_force -> raw_order.time_in_force
- source -> raw_order.source
- metadata -> raw_order.metadata
- simulation_mode -> simulation_mode
- fill_price -> fill_price
- filled_quantity -> filled_quantity
- reject_reason -> reject_reason
- output_path -> output_path

## 11. Dify 必须拒绝的 intent

Dify 必须拒绝：

- place_real_order
- connect_exchange
- save_api_key
- read_wallet_private_key
- real_execution
- bypass_risk
- force_execute_trade
- convert_paper_to_real_order

拒绝原因：

当前只支持 paper / sandbox execution。
当前不接真实交易所 API。
当前不保存真实 API key。
当前不真实下单。

## 12. 用户可见 success 文案要求

Dify 展示 paper success 时必须说明：

- 这是 paper / sandbox execution
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化
- 结果只用于测试、审计和 replay

禁止说法：

- 已真实买入
- 已真实卖出
- 已真实成交
- 已产生真实收益
- 已修改真实仓位

## 13. 本地 Adapter 规划

P5-D6 只做规划，不实现 Dify paper HTTP adapter。

后续 P5-D7 可以新增：

- fcf/api/dify_paper_execution_adapter.py
- tests/test_dify_paper_execution_adapter.py

建议 route：

- GET /api/v1/paper-execution/contract
- POST /api/v1/paper-execution/execute

该 adapter 只能调用：

- fcf.api.paper_execution_api.handle_paper_execution

禁止：

- 调用真实交易所
- 调用真实执行器
- 保存真实 API key
- 真实下单

## 14. 安全边界

P5-D6 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交

## 15. 验收标准

P5-D6 完成需要满足：

- 新增 docs/42_p5_dify_paper_execution_contract.md
- README 更新 P5-D6 状态
- PROJECT_STATE 更新 P5-D6 状态
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

