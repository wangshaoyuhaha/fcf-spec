# FCF Spec

FCF Spec 是一个 BTC / 加密货币交易系统的最小事件骨架项目。

## 当前阶段

- Phase 1 Build Spine 已完成稳定收尾
- D1-D11 已完成
- Phase 2 已启动
- P2-D1：BTC Market Context 规划已完成
- P2-D2：BTCMarketContext 契约已完成

## 当前能力

当前系统已经具备一条最小 BTC 交易事件链：

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

## 当前验证方式

运行最小主流程：

python main.py

预期输出包含：

- FCF minimal spine executed.
- events_recorded: 8

运行测试：

python -m pytest -q

预期输出：

- 11 passed

## 文档进度

当前 docs 已包含：

- docs/01_constitution.md
- docs/01_vision.md
- docs/02_constitution.md
- docs/03_architecture.md
- docs/04_event_contracts.md
- docs/05_module_contracts.md
- docs/06_runtime_spine.md
- docs/07_tests_and_replay.md
- docs/08_module_runtime.md
- docs/09_risk_execution_shadow.md
- docs/10_audit_persistence_replay.md
- docs/11_phase1_acceptance.md
- docs/12_phase2_btc_market_context.md

## 当前新增代码

P2-D2 新增：

- fcf/contracts/market_context.py
- tests/test_market_context.py

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

## Phase 2 方向

Phase 2 不直接接真实交易所 API，不真实下单，不做复杂黑箱策略。

Phase 2 当前目标是先建立 BTC 市场上下文结构，后续逐步支持：

- BTC K线数据
- 成交量数据
- 订单簿快照
- spread / slippage
- funding rate
- volatility
- market regime
- risk context
- position context
- shadow trading 审计
- replay 验证

## 下一步

进入 P2-D3：

创建 BTCMarketContext 最小标准化模块：

- fcf/modules/market_context_builder.py
- tests/test_market_context_builder.py

P2-D3 目标：

- 输入原始 BTC market dict
- 输出 BTCMarketContext
- 自动计算 spread
- 自动计算 orderbook_imbalance
- 自动标记 data_quality_level
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py 事件链
