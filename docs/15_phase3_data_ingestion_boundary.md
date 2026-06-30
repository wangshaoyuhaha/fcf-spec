# Phase 3 - 真实数据接入边界规划

## 1. 目的

Phase 3 的目标是规划真实市场数据如何安全进入 FCF 系统。

本阶段不直接接真实交易所 API 密钥。

本阶段不真实下单。

本阶段只定义：

- 数据源边界
- mock data adapter
- raw market data schema
- replayable input fixture
- 数据接入安全边界
- 真实 API 接入前的隔离层

## 2. 当前基础

当前已经完成：

- Phase 1 Build Spine
- Phase 2 多资产 MarketContext 基础层
- FCFEvent
- EventStore
- ReplayEngine
- BTCMarketContext
- BaseMarketContext
- market_constants
- market_context_builder
- market_context_adapter
- market context 事件化测试

当前验证结果：

- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 37 passed

## 3. Phase 3 边界原则

Phase 3 初期必须遵守：

- 不接真实交易所 API 密钥
- 不真实下单
- 不保存密钥
- 不读取本地敏感配置
- 不调用真实外部交易接口
- 不破坏当前 main.py 主事件链
- 不破坏当前 37 个测试

## 4. 数据源类型规划

未来可支持的数据源包括：

### 4.1 Crypto

- Binance
- OKX
- Coinbase
- Bybit
- Deribit

### 4.2 FX

- OANDA
- Interactive Brokers
- Dukascopy
- broker quote feed

### 4.3 Equities

- Polygon
- IEX
- Nasdaq data
- broker market data

### 4.4 Futures

- CME data
- broker futures feed
- historical futures data

### 4.5 Commodities

- commodity futures data
- spot commodity reference data
- inventory / supply-demand data

### 4.6 Rates / Bonds

- yield curve data
- treasury futures
- bond market data
- central bank event data

## 5. Phase 3 第一阶段只做 mock

Phase 3 第一阶段只允许使用：

- 本地 mock dict
- 本地 fixture JSON
- 本地 JSONL replay input
- 手写样本数据
- 测试内构造数据

不得使用：

- 真实 API key
- 真实下单接口
- 真实账户连接
- 自动交易权限

## 6. RawMarketDataSchema 初步规划

第一版 raw market data 可以包含：

- asset_class
- symbol
- venue
- exchange
- market_type
- timestamp
- timeframe
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
- source
- source_type
- received_at
- metadata

## 7. Mock Data Adapter 规划

mock data adapter 负责：

- 输入本地 raw market dict
- 校验必要字段
- 输出统一 raw market event payload
- 不调用外部 API
- 不保存密钥
- 不真实下单

建议后续新增：

- fcf/modules/mock_market_data_adapter.py
- tests/test_mock_market_data_adapter.py

## 8. Replayable Input Fixture 规划

后续需要支持：

- fixtures/raw_market_data_crypto.json
- fixtures/raw_market_data_fx.json
- fixtures/raw_market_data_equity.json
- fixtures/raw_market_data_futures.json

这些 fixture 只用于测试和回放。

## 9. Phase 3 初步事件方向

Phase 3 后续可能新增事件：

- fcf.market.raw_received
- fcf.market.raw_validated
- fcf.market.normalized
- fcf.market.context_built
- fcf.market.context_adapted
- fcf.audit.input_replayed

P3-D1 只做规划，不修改 main.py 主事件链。

## 10. P3-D1 验收标准

P3-D1 完成需要满足：

- docs/15_phase3_data_ingestion_boundary.md 已创建
- 明确 Phase 3 不接真实 API key
- 明确 Phase 3 不真实下单
- 明确 mock data adapter 方向
- 明确 raw market data schema 初稿
- 明确 replayable fixture 方向
- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 37 passed

## 11. 下一步

P3-D1 完成后，进入 P3-D2。

建议 P3-D2：

创建 mock market data adapter。

建议新增：

- fcf/modules/mock_market_data_adapter.py
- tests/test_mock_market_data_adapter.py

P3-D2 仍然不接真实交易所 API，不真实下单。
