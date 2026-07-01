# P4-D9 - Multi-asset Fixture Expansion Plan

## 1. 目的

P4-D9 开始扩展多资产 fixture。

当前项目不是 BTC-only。
当前项目目标是全金融市场 / 多资产交易事件系统。

P4-D9 的目标是新增一份最小多资产 fixture，用于验证 raw market input schema 对不同 asset_class 的兼容性。

## 2. 当前覆盖资产

P4-D9 覆盖四类资产：

- crypto
- equities
- fx
- commodities

## 3. 新增 fixture

新增文件：

- fixtures/raw_market_data_multi_asset.json

该 fixture 包含：

- BTCUSDT / crypto / perpetual
- AAPL / equities / spot
- EURUSD / fx / spot
- XAUUSD / commodities / futures

## 4. 字段策略

所有资产暂时共享 raw market input 的最小 schema：

必填字段：

- asset_class
- symbol
- venue
- market_type
- timestamp
- timeframe
- source
- source_type
- last_price

可选数字字段：

- open
- high
- low
- close
- volume
- quote_volume
- best_bid
- best_ask
- bid_depth
- ask_depth

## 5. 当前限制

P4-D9 不实现真实交易所数据接入。
P4-D9 不实现股票行情源。
P4-D9 不实现外汇行情源。
P4-D9 不实现商品行情源。
P4-D9 不真实下单。

当前 fixture 全部是 mock / fixture 数据。

## 6. 验证目标

P4-D9 验证：

- 多资产 fixture 可以被 JSON 加载
- 每一行都可以通过 normalize_raw_market_input
- process_raw_market_batch 可以处理多资产 rows
- Dify HTTP batch adapter 可以处理多资产 rows
- Dify batch response 保持稳定 response dict

## 7. 安全边界

P4-D9 不接真实交易所 API。
P4-D9 不保存真实 API key。
P4-D9 不读取钱包私钥。
P4-D9 不真实下单。
P4-D9 不让 Dify 成为底层交易内核。
P4-D9 不把 pipeline 成功伪装成真实交易成功。

## 8. 下一步建议

下一步进入 P4-D10：multi-asset fixture Dify response smoke。

建议目标：

- 增加本地 smoke runner
- 用 Dify batch route 调用 multi-asset fixture
- 把 adapter response 接入 user-facing response template
- 输出稳定 summary
- 不接真实交易所 API
- 不真实下单

