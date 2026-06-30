# P2-D5 - 多资产 MarketContext / AssetMarketContext 泛化层规划

## 1. 目的

当前 Phase 2 已经完成 BTCMarketContext 的第一版规划、契约、builder 和事件化测试。

但是项目目标不是 BTC-only。

FCF Spec 的长期目标是成为全金融市场 / 多资产交易系统的事件驱动骨架。

因此 P2-D5 的目标是规划通用 MarketContext / AssetMarketContext 泛化层，为后续支持 crypto、FX、equities、futures、commodities、rates / bonds 做准备。

本阶段只做规划，不急着重命名已经通过测试的 BTCMarketContext。

## 2. 当前已完成基础

当前已经具备：

- FCFEvent
- EventStore
- ReplayEngine
- risk_guardian
- executor
- shadow_simulator
- BTCMarketContext
- market_context_builder
- market context event flow tests

当前验证结果：

- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 18 passed

## 3. 核心定位

BTCMarketContext 是第一版 crypto/BTC 市场上下文实现。

它不是最终抽象层。

后续需要逐步形成：

- MarketContext
- AssetMarketContext
- CryptoMarketContext
- FXMarketContext
- EquityMarketContext
- FuturesMarketContext
- CommodityMarketContext
- RatesMarketContext

## 4. 通用字段规划

所有资产类别都应尽量共享一组通用字段。

### 4.1 标识字段

- asset_class
- symbol
- venue
- exchange
- market_type
- timestamp
- timeframe
- currency
- quote_currency

### 4.2 价格字段

- open
- high
- low
- close
- last_price
- reference_price
- settlement_price

### 4.3 流动性字段

- volume
- quote_volume
- best_bid
- best_ask
- spread
- bid_depth
- ask_depth
- liquidity_level

### 4.4 波动率字段

- realized_volatility
- implied_volatility
- atr
- price_change_1m
- price_change_5m
- price_change_15m
- price_change_1h
- volatility_regime

### 4.5 市场状态字段

- trend_direction
- regime_label
- momentum_score
- mean_reversion_score
- abnormal_move_detected

### 4.6 风险字段

- data_quality_level
- market_liquidity_risk
- volatility_risk
- slippage_risk
- position_risk
- max_loss_risk

## 5. 资产类别扩展边界

### 5.1 Crypto

crypto 需要额外支持：

- funding_rate
- next_funding_time
- open_interest
- open_interest_change_rate
- long_short_ratio
- liquidation_risk
- perpetual_basis

当前 BTCMarketContext 已经覆盖 crypto 第一版核心字段。

### 5.2 FX

FX 需要额外支持：

- base_currency
- quote_currency
- pip_size
- session
- central_bank_event_risk
- carry_context
- macro_event_risk

### 5.3 Equities

股票需要额外支持：

- ticker
- exchange
- sector
- industry
- market_cap
- earnings_event_risk
- dividend_event_risk
- premarket_price
- afterhours_price

### 5.4 Futures

期货需要额外支持：

- contract_code
- expiry_date
- roll_date
- front_month
- basis
- term_structure
- margin_requirement
- delivery_risk

### 5.5 Commodities

大宗商品需要额外支持：

- commodity_type
- inventory_data
- supply_demand_context
- seasonality_context
- storage_cost
- geopolitical_risk

### 5.6 Rates / Bonds

利率和债券需要额外支持：

- yield
- duration
- convexity
- curve_point
- curve_spread
- central_bank_policy_risk
- auction_risk

## 6. 建议的抽象方向

后续可以逐步引入：

- BaseMarketContext
- AssetMarketContext
- CryptoMarketContext
- EquityMarketContext
- FuturesMarketContext
- FXMarketContext

但当前不立刻修改已通过的 BTCMarketContext。

原因：

- 当前 18 个测试稳定通过
- BTCMarketContext 已经是可运行样板
- 过早重命名容易破坏现有骨架
- 更好的方式是先增加泛化规划，再小步抽象

## 7. 建议事件命名方向

当前已验证事件：

- fcf.market.context_built

后续可以扩展：

- fcf.market.raw_received
- fcf.market.normalized
- fcf.market.context_built
- fcf.asset.context_built
- fcf.crypto.context_built
- fcf.fx.context_built
- fcf.equity.context_built
- fcf.futures.context_built
- fcf.risk.context_built
- fcf.audit.replay_verified

## 8. P2-D5 暂不做的事情

P2-D5 暂不做：

- 不重命名 BTCMarketContext
- 不删除当前 BTC 测试
- 不接真实交易所 API
- 不真实下单
- 不做复杂策略
- 不修改 main.py 主事件链
- 不破坏当前 18 个测试

## 9. P2-D5 验收标准

P2-D5 完成需要满足：

- docs/13_multi_asset_market_context.md 已创建
- 明确项目是全金融市场 / 多资产系统
- 明确 BTCMarketContext 是第一实现，不是终点
- 明确通用 MarketContext 字段
- 明确不同资产类别的扩展边界
- python main.py 仍然输出 events_recorded: 8
- python -m pytest -q 仍然显示 18 passed

## 10. 下一步

P2-D5 完成后，进入 P2-D6。

建议 P2-D6：

创建通用 MarketContext 最小契约。

建议新增：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

P2-D6 只做最小通用契约，不迁移、不删除、不破坏 BTCMarketContext。
