# P2-D1 - Phase 2 BTC Market Context 规划

## 1. 目的

Phase 1 已经完成 BTC 交易系统的最小事件骨架：

- FCFEvent
- EventBus
- EventStore
- ReplayEngine
- 8 个核心事件链
- JSONL 事件持久化
- JSONL 回放一致性测试
- 风控、执行、影子模式最小闭环

Phase 2 的目标不是立刻做复杂交易策略，也不是接真实账户自动下单。

Phase 2 的第一步是定义 BTC 交易系统需要的标准市场输入结构，使后续策略、风控、执行和回放都基于统一数据上下文。

## 2. 当前 Phase 1 事件链

当前最小事件链为：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

当前验证结果：

- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 8 passed

## 3. Phase 2 总目标

Phase 2 需要逐步引入：

- BTC 市场数据结构
- K线数据结构
- 成交量数据结构
- 订单簿快照结构
- spread / slippage 评估字段
- funding rate 字段
- volatility 字段
- market regime 判断字段
- risk context 字段
- position context 字段
- shadow trading 结果字段
- 可审计、可回放、可测试的交易上下文

## 4. Phase 2 暂不做的事情

Phase 2 初期暂不做：

- 不接真实交易所 API 密钥
- 不真实下单
- 不做高杠杆实盘
- 不做自动重仓策略
- 不做不可解释黑箱模型
- 不绕过 policy_engine
- 不绕过 risk_guardian
- 不绕过 EventStore
- 不破坏 Phase 1 已经稳定的 8 事件链

## 5. 新核心对象：BTCMarketContext

BTCMarketContext 用于描述一次交易决策前的市场上下文。

第一版字段规划如下。

### 5.1 基础市场信息

- symbol
- exchange
- market_type
- timestamp
- timeframe

示例：

- symbol: BTCUSDT
- exchange: binance
- market_type: perpetual
- timeframe: 1m / 5m / 15m / 1h

### 5.2 价格信息

- open
- high
- low
- close
- last_price
- mark_price
- index_price

### 5.3 成交量信息

- volume
- quote_volume
- taker_buy_volume
- taker_sell_volume
- volume_change_rate

### 5.4 订单簿信息

- best_bid
- best_ask
- spread
- bid_depth
- ask_depth
- orderbook_imbalance

### 5.5 衍生品信息

- funding_rate
- next_funding_time
- open_interest
- open_interest_change_rate
- long_short_ratio

### 5.6 波动率信息

- realized_volatility
- atr
- price_change_1m
- price_change_5m
- price_change_15m
- volatility_regime

### 5.7 市场状态信息

- trend_direction
- regime_label
- momentum_score
- mean_reversion_score
- liquidity_level
- abnormal_move_detected

### 5.8 风险信息

- data_quality_level
- market_liquidity_risk
- volatility_risk
- slippage_risk
- funding_risk
- position_risk
- max_loss_risk

## 6. Phase 2 事件链扩展方向

Phase 1 当前事件链暂时保持不变。

Phase 2 后续可能扩展为：

1. fcf.market.raw_received
2. fcf.market.normalized
3. fcf.market.context_built
4. fcf.regime.detected
5. fcf.decision.proposed
6. fcf.policy.reviewed
7. fcf.risk.reviewed
8. fcf.order.approved
9. fcf.order.executed
10. fcf.shadow.simulated
11. fcf.audit.persisted
12. fcf.audit.replay_verified

P2-D1 只做规划，不直接修改 main.py 事件链。

## 7. Phase 2 模块边界

### 7.1 market_data 模块

负责：

- 接收 BTC 原始行情
- 接收 K线
- 接收成交量
- 接收订单簿快照
- 输出原始 market event

### 7.2 market_context 模块

负责：

- 将原始行情标准化为 BTCMarketContext
- 计算 spread
- 计算 orderbook imbalance
- 计算 volatility 字段
- 输出标准市场上下文

### 7.3 regime_radar 模块

负责：

- 判断趋势 / 震荡 / 高波动 / 低流动性
- 输出 regime_label
- 不直接生成交易结论

### 7.4 strategy_proposer 模块

负责：

- 基于 BTCMarketContext 生成候选交易想法
- 输出 decision proposed
- 不直接下单

### 7.5 policy_engine 模块

负责：

- 检查策略是否符合规则
- 过滤过度交易
- 过滤不完整输入
- 过滤风险过高场景

### 7.6 risk_guardian 模块

负责：

- 检查仓位风险
- 检查滑点风险
- 检查流动性风险
- 检查最大亏损风险
- 决定是否批准订单

### 7.7 executor 模块

负责：

- 执行模拟订单
- 后续可扩展为真实交易所执行接口
- Phase 2 初期仍以模拟执行为主

### 7.8 shadow_simulator 模块

负责：

- 在不真实下单的情况下模拟交易结果
- 记录假设成交价格
- 记录影子收益 / 回撤
- 供 ReplayEngine 和审计系统验证

## 8. P2-D1 验收标准

P2-D1 完成需要满足：

- docs/12_phase2_btc_market_context.md 已创建
- 明确 BTCMarketContext 第一版字段
- 明确 Phase 2 暂不做真实下单
- 明确 Phase 2 事件链扩展方向
- 明确 BTC 交易系统模块边界
- 不破坏 Phase 1 代码
- python main.py 仍然输出 events_recorded: 8
- python -m pytest -q 仍然显示 8 passed

## 9. 下一步

P2-D1 完成后，进入 P2-D2：

创建 BTCMarketContext 契约文件：

- fcf/contracts/market_context.py

P2-D2 只定义数据结构和测试，不接真实交易所 API。
