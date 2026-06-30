# P3-D8 - Dify Workflow HTTP/API Node Mapping

## 1. 目的

本文档定义 Dify workflow 中各节点如何把用户输入传递给 FCF 受控 API wrapper。

P3-D8 只做 workflow 节点映射文档。
P3-D8 不接真实交易所 API。
P3-D8 不保存真实 API key。
P3-D8 不真实下单。
P3-D8 不把 Dify 当作底层交易内核。
P3-D8 不修改 executor。
P3-D8 不绕过 policy、risk、EventStore、ReplayEngine。

## 2. 当前边界

Dify 的定位：

- 上层 workflow
- 对话入口
- 字段收集器
- 字段校验器
- API wrapper 调用方
- summary 展示层

FCF 的定位：

- 事件驱动交易系统骨架
- 数据接入边界
- 受控 pipeline
- 事件持久化
- replay 校验
- 风控和执行边界所有者

Dify 不能直接做：

- 连接真实交易所
- 保存真实交易所 API key
- 读取钱包私钥
- 发送真实订单
- 绕过 FCF 事件链
- 绕过 FCF 风控边界

## 3. 推荐 Workflow 节点

推荐 Dify workflow 第一版节点如下：

1. Start Node
2. User Intent Node
3. Market Input Parser Node
4. Required Field Check Node
5. Market Type Normalization Node
6. Build FCF Request Node
7. FCF API Call Node
8. IF Response OK Node
9. Success Summary Node
10. Error Summary Node
11. End Node

## 4. Start Node

Start Node 负责接收用户原始输入。

示例用户输入：

我想分析 BTCUSDT 当前 1m 行情，价格 60050，成交量 120.5，盘口 bid 60049.5，ask 60050.5。

Start Node 输出字段：

- user_message
- conversation_id
- workflow_run_id
- user_id_optional

注意：

- user_id_optional 不进入交易执行
- conversation_id 只用于追踪
- workflow_run_id 可作为 correlation_id

## 5. User Intent Node

User Intent Node 只判断用户想做什么。

允许的 intent：

- analyze_market_input
- validate_market_input
- replay_market_input
- explain_error

禁止的 intent：

- place_real_order
- connect_exchange
- save_api_key
- bypass_risk
- force_execute_trade

如果用户要求真实下单，Dify 必须拒绝并说明当前系统不支持真实下单。

## 6. Market Input Parser Node

Market Input Parser Node 把自然语言整理成结构化字段。

输出字段：

- asset_class
- symbol
- venue
- market_type
- timestamp
- timeframe
- source
- source_type
- open
- high
- low
- close
- last_price
- volume
- quote_volume
- best_bid
- best_ask
- bid_depth
- ask_depth

字段说明：

- asset_class 表示资产类别
- symbol 表示交易标的
- venue 表示市场或交易场所
- market_type 表示 spot、perp、futures 等
- timestamp 建议使用 ISO 时间
- timeframe 表示时间周期
- source 表示输入来源
- source_type 当前建议使用 mock、manual、fixture
- 数字字段可以先作为字符串传递给 FCF，由 FCF 负责校验

## 7. Required Field Check Node

Required Field Check Node 检查必填字段。

当前必填字段建议：

- asset_class
- symbol
- venue
- market_type
- timestamp
- timeframe
- source
- source_type
- last_price

如果缺字段，进入 Error Summary Node。

缺字段错误示例：

{
  "ok": false,
  "stage": "dify_required_field_check",
  "error": {
    "type": "MissingField",
    "message": "last_price is required"
  }
}

注意：

该节点只是 Dify 层预检查。
最终合法性仍以 FCF wrapper / pipeline 返回为准。

## 8. Market Type Normalization Node

Dify 可以做轻量 market_type 归一化。

建议映射：

- perpetual -> perp
- PERP -> perp
- Perp -> perp
- spot -> spot
- SPOT -> spot
- futures -> futures
- FUTURES -> futures

Dify 不应做复杂交易规则判断。
复杂规则以后交给 FCF MarketContext / Policy / Risk 层。

## 9. Build FCF Request Node

Build FCF Request Node 负责组装传给 FCF wrapper 的 JSON。

Single input 请求结构：

{
  "handler": "handle_single_market_input",
  "correlation_id": "workflow_run_id",
  "output_path": "runtime/events/dify_single_market_input.jsonl",
  "raw": {
    "asset_class": "asset_class",
    "symbol": "symbol",
    "venue": "venue",
    "market_type": "market_type",
    "timestamp": "timestamp",
    "timeframe": "timeframe",
    "source": "dify_workflow",
    "source_type": "manual",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "last_price": "last_price",
    "volume": "volume",
    "quote_volume": "quote_volume",
    "best_bid": "best_bid",
    "best_ask": "best_ask",
    "bid_depth": "bid_depth",
    "ask_depth": "ask_depth"
  }
}

Batch input 请求结构：

{
  "handler": "handle_batch_market_input",
  "correlation_id": "workflow_run_id",
  "output_path": "runtime/events/dify_batch_market_input.jsonl",
  "rows": []
}

## 10. FCF API Call Node

当前 P3-D8 仍不实现真实 HTTP server。

但未来 HTTP/API 节点应只调用受控 wrapper 对应的服务端入口。

未来 HTTP 方法建议：

- POST

未来路径建议：

- /api/v1/market-input/single
- /api/v1/market-input/batch
- /api/v1/contract

请求头建议：

- Content-Type: application/json

禁止请求头：

- exchange-api-key
- exchange-secret
- wallet-private-key
- real-order-token

说明：

如果未来需要鉴权，也只能是 FCF 内部服务鉴权。
不能把真实交易所密钥放进 Dify。

## 11. IF Response OK Node

Dify 收到 FCF response 后必须检查：

- response.ok == true
- response.error == null
- response.data != null

如果 ok 为 true，进入 Success Summary Node。
如果 ok 为 false，进入 Error Summary Node。

禁止行为：

- 忽略 ok 字段
- ok=false 仍进入成功分支
- data=null 仍展示为成功
- error 存在时继续模拟交易完成

## 12. Success Summary Node

成功分支可以向用户展示：

- FCF 已接收市场输入
- pipeline 已完成
- event_count
- persisted
- output_path
- replay.status
- replay.event_count

成功分支必须说明：

- 当前没有连接真实交易所
- 当前没有真实下单
- 当前只是受控 pipeline / replay 处理

成功分支示例：

FCF 已接收本次市场输入，并通过受控 pipeline 完成处理。
事件数量：1
Replay 状态：completed
本次没有连接真实交易所，也没有真实下单。

## 13. Error Summary Node

错误分支可以展示：

- error.type
- error.message
- 建议用户修正哪个字段

错误分支必须说明：

- 本次没有进入真实交易
- 本次没有连接真实交易所
- 本次没有真实下单

错误分支示例：

这次输入没有通过校验。
错误类型：ValueError
错误信息：last_price must be a valid number
请修正 last_price 后重新提交。
本次没有连接真实交易所，也没有真实下单。

## 14. 字段映射总表

Dify 字段到 FCF 字段：

- workflow_run_id -> correlation_id
- asset_class -> raw.asset_class
- symbol -> raw.symbol
- venue -> raw.venue
- market_type -> raw.market_type
- timestamp -> raw.timestamp
- timeframe -> raw.timeframe
- source -> raw.source
- source_type -> raw.source_type
- open -> raw.open
- high -> raw.high
- low -> raw.low
- close -> raw.close
- last_price -> raw.last_price
- volume -> raw.volume
- quote_volume -> raw.quote_volume
- best_bid -> raw.best_bid
- best_ask -> raw.best_ask
- bid_depth -> raw.bid_depth
- ask_depth -> raw.ask_depth
- output_path -> output_path

## 15. 多资产扩展说明

FCF 当前不是 BTC-only。

asset_class 后续可扩展：

- crypto
- equities
- fx
- commodities
- rates
- index
- options
- futures

P3-D8 不实现这些市场的完整规则。
P3-D8 只保证 workflow 字段设计不把系统锁死在 BTC。

## 16. P3-D8 验收标准

P3-D8 完成需要满足：

- docs/18_dify_workflow_http_api_node_mapping.md 已新增
- 明确 Dify workflow 节点顺序
- 明确每个节点职责
- 明确字段映射
- 明确 FCF API Call Node 边界
- 明确 success 分支
- 明确 error 分支
- 明确安全禁止项
- 不接真实交易所 API
- 不真实下单
- python main.py 仍输出 events_recorded: 8
- python -m pytest -q 仍通过

