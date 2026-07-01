# P5-D4 - Sandbox Execution EventStore and Replay Integration

## 1. 目的

P5-D4 将 sandbox execution engine 接入 EventStore 和 ReplayEngine。

P5-D3 已经实现 sandbox execution engine skeleton：

- simulated_fill
- simulated_reject
- full fill
- partial fill
- stable response dict
- safe boundary fields

P5-D4 的目标是让 sandbox execution result 可以：

- 生成 sandbox execution event
- 写入 EventStore
- 可选择持久化 JSONL
- 被 ReplayEngine 回放
- 返回稳定 response dict

## 2. 当前新增能力

P5-D4 新增函数：

- execute_sandbox_order_with_eventstore

该函数会：

1. 调用 execute_sandbox_order
2. 如果模拟执行失败，直接返回 ok=false
3. 如果模拟执行成功，创建 sandbox execution event
4. 写入 EventStore
5. 可选保存 JSONL
6. 调用 ReplayEngine
7. 返回包含 replay summary 的 stable response dict

## 3. 当前事件名

当前支持事件：

- fcf.sandbox.execution.filled
- fcf.sandbox.execution.partial_filled
- fcf.sandbox.execution.rejected

## 4. Stable Response Dict

成功时：

{
  "ok": true,
  "engine": "sandbox_execution_engine",
  "engine_version": "0.1.0",
  "error": null,
  "data": {
    "status": "completed",
    "event_count": 1,
    "event_names": ["fcf.sandbox.execution.filled"],
    "persisted": false,
    "output_path": null,
    "replay": {}
  }
}

失败时：

{
  "ok": false,
  "engine": "sandbox_execution_engine",
  "engine_version": "0.1.0",
  "error": {
    "type": "ValueError",
    "message": "error detail"
  },
  "data": null
}

## 5. 安全边界

P5-D4 不接真实交易所 API。
P5-D4 不保存真实 API key。
P5-D4 不读取钱包私钥。
P5-D4 不真实下单。
P5-D4 不修改真实账户。
P5-D4 不修改真实仓位。
P5-D4 不把 sandbox execution 伪装成真实成交。

所有事件 payload 必须明确：

- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

## 6. 验收标准

P5-D4 完成需要满足：

- sandbox execution success 能写入 EventStore
- full fill event 可 Replay
- partial fill event 可 Replay
- reject event 可 Replay
- 可选 output_path 持久化 JSONL
- bad paper order 仍返回 ok=false
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

