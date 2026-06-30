# FCF Spec

FCF Spec 是一个全金融市场 / 多资产交易系统的最小事件骨架项目。

## 当前定位

本项目不是足球系统。

本项目也不是只做 BTC。

当前目标是构建一个可以逐步适配全金融市场的事件驱动交易系统骨架。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

未来需要逐步适配：

- crypto: BTC, ETH, SOL 等
- FX: EURUSD, USDJPY 等
- equities: AAPL, TSLA, SPY 等
- futures: ES, NQ, CL, GC 等
- commodities: oil, gold 等
- rates / bonds: 利率、国债、收益率相关市场

## 当前阶段

- Phase 1 Build Spine 已完成稳定收尾
- D1-D11 已完成
- Phase 2 已启动
- P2-D1：BTC Market Context 规划已完成
- P2-D2：BTCMarketContext 契约已完成
- P2-D3：BTCMarketContext 最小标准化模块已完成

## 当前能力

当前系统已经具备一条最小交易事件链：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

当前已经完成：

- FCFEvent 事件契约
- EventBus
- EventStore
- ReplayEngine
- 数据标准化模块
- regime 检测模块
- decision proposer
- policy engine
- risk guardian
- executor
- shadow simulator
- JSONL 事件持久化
- JSONL 事件读取
- ReplayEngine 回放一致性测试
- Phase 1 骨架验收
- BTCMarketContext 第一版规划
- BTCMarketContext 契约文件
- BTCMarketContext 单元测试
- BTCMarketContext 最小标准化 builder

## 当前验证方式

运行最小主流程：

python main.py

预期输出包含：

- FCF minimal spine executed.
- events_recorded: 8

运行测试：

python -m pytest -q

预期输出：

- 15 passed

## 当前新增代码

P2-D2 新增：

- fcf/contracts/market_context.py
- tests/test_market_context.py

P2-D3 新增：

- fcf/modules/market_context_builder.py
- tests/test_market_context_builder.py

当前 BTCMarketContext 支持：

- BTC 市场基础信息
- 价格信息
- 成交量信息
- 订单簿信息
- 衍生品信息
- 波动率信息
- 市场状态信息
- 风险信息
- to_dict
- market_context_from_dict

当前 market_context_builder 支持：

- 输入原始 BTC market dict
- 输出 BTCMarketContext
- 自动计算 spread
- 自动计算 orderbook_imbalance
- 自动标记 data_quality_level
- 字符串数值转 float
- 必填数字字段校验

## 架构方向

底层架构保持事件驱动：

全金融市场原始数据
-> market_data / data_ingestor
-> normalizer
-> MarketContext / AssetMarketContext
-> regime_radar
-> strategy_proposer
-> policy_engine
-> risk_guardian
-> executor
-> shadow_simulator
-> EventStore
-> ReplayEngine
-> Audit / Replay / Test

## Phase 2 边界

Phase 2 不直接接真实交易所 API，不真实下单，不做复杂黑箱策略。

Phase 2 当前目标是先建立市场上下文结构，后续逐步支持：

- 多资产 MarketContext
- crypto market context
- FX market context
- equity market context
- futures market context
- spread / slippage
- volatility
- market regime
- risk context
- position context
- shadow trading 审计
- replay 验证

## 下一步

进入 P2-D4：

market context 事件化。

P2-D4 目标：

- 把 BTCMarketContext 放进 FCFEvent payload
- 增加最小事件测试
- 验证 BTCMarketContext 可以被 FCFEvent 记录
- 验证 EventStore 可以保存包含 MarketContext 的事件
- 验证 ReplayEngine 可以回放相关事件
- 为后续多资产 MarketContext 泛化做准备
- 不接真实交易所 API
- 不真实下单
- 不破坏 main.py
