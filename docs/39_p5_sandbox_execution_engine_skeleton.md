# P5-D3 - Sandbox Execution Engine Skeleton

## 1. 目的

P5-D3 新增 sandbox execution engine skeleton。

该 engine 只接收 paper order，并生成本地模拟执行 summary。

P5-D3 不接真实交易所 API。
P5-D3 不保存真实 API key。
P5-D3 不读取钱包私钥。
P5-D3 不真实下单。
P5-D3 不修改真实账户。
P5-D3 不修改真实仓位。

## 2. 当前支持模式

当前支持：

- simulated_fill
- simulated_reject

## 3. simulated_fill

simulated_fill 用于模拟成交。

允许：

- full fill
- partial fill

必须保持：

- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

## 4. simulated_reject

simulated_reject 用于模拟拒单。

拒单只产生 sandbox summary。
拒单不触达真实交易所。
拒单不产生真实账户影响。

## 5. 当前输出 summary

execute_sandbox_order 返回稳定 dict：

{
  "ok": true,
  "engine": "sandbox_execution_engine",
  "engine_version": "0.1.0",
  "error": null,
  "data": {}
}

错误时：

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

## 6. 安全边界

P5-D3 不接真实交易所 API。
P5-D3 不保存真实 API key。
P5-D3 不读取钱包私钥。
P5-D3 不真实下单。
P5-D3 不把 sandbox execution 伪装成真实成交。

## 7. 下一步建议

下一步进入 P5-D4：sandbox execution event integration。

建议目标：

- 将 sandbox execution summary 写入 EventStore
- 生成 fcf.sandbox.execution.filled / rejected 事件
- ReplayEngine 可回放 sandbox execution event
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

