# P5-D2 - Paper Order Schema Module

## 1. 目的

P5-D2 新增 paper order schema module。

该模块只定义 paper / sandbox order 的输入边界。

P5-D2 不接真实交易所 API。
P5-D2 不保存真实 API key。
P5-D2 不读取钱包私钥。
P5-D2 不真实下单。

## 2. Paper Order 定位

Paper order 是模拟订单。

Paper order 只能用于：

- sandbox execution
- replay
- audit
- strategy dry-run
- Dify workflow 演示
- risk / policy 测试

Paper order 不能用于：

- 真实交易所下单
- 真实账户资金变化
- 真实仓位变化
- 真实成交确认

## 3. 必填字段

当前 paper order 必填字段：

- asset_class
- symbol
- venue
- market_type
- side
- order_type
- quantity
- source
- correlation_id

## 4. 可选字段

当前 paper order 可选字段：

- price
- time_in_force
- metadata

## 5. 归一化规则

side 支持：

- buy -> buy
- long -> buy
- sell -> sell
- short -> sell

order_type 支持：

- market -> market
- limit -> limit
- stop -> stop
- stop_limit -> stop_limit

time_in_force 支持：

- gtc -> GTC
- ioc -> IOC
- fok -> FOK
- day -> DAY

## 6. 数字规则

quantity：

- 必须能转换为 float
- 必须大于 0

price：

- 可选
- 如果存在，必须能转换为 float
- 如果存在，必须大于 0

## 7. 强制安全字段

normalize 后必须强制写入：

- execution_mode = paper
- real_order = false
- real_exchange_api = false
- real_money_impact = false

这些字段不能由用户输入覆盖为 true。

## 8. Stable Response Dict

validate_paper_order 返回：

{
  "ok": true,
  "schema": "paper_order_schema",
  "schema_version": "0.1.0",
  "error": null,
  "data": {}
}

P5-D2 当前只做 schema，不做 API wrapper。

## 9. 安全边界

P5-D2 不接真实交易所 API。
P5-D2 不保存真实 API key。
P5-D2 不读取钱包私钥。
P5-D2 不真实下单。
P5-D2 不让 Dify 触达真实执行器。
P5-D2 不把 paper order 伪装成 real order。

## 10. 下一步建议

下一步进入 P5-D3：sandbox execution engine skeleton。

建议目标：

- 新增 fcf/paper/sandbox_execution_engine.py
- 接收 normalized paper order
- 生成 sandbox execution summary
- 不接真实交易所 API
- 不真实下单
- 后续再接 EventStore / Replay

