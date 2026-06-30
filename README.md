# FCF Spec

FCF Spec 是一个全金融市场 / 多资产交易系统的最小事件骨架项目。

## 当前定位

本项目不是足球系统。

本项目也不是只做 BTC。

当前目标是构建一个可以逐步适配全金融市场的事件驱动交易系统骨架。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

BaseMarketContext 是通用多资产上下文契约。

market_constants 是多资产 asset_class / market_type 标准常量与验证工具。

Phase 2 多资产市场上下文基础层已经完成阶段验收。

## 当前阶段

- Phase 1 Build Spine 已完成稳定收尾
- D1-D11 已完成
- Phase 2 多资产市场上下文基础层已完成阶段验收
- P2-D1 到 P2-D10 已完成

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
- Market context 事件化测试
- 多资产 MarketContext 泛化层规划
- BaseMarketContext 通用契约
- BTCMarketContext 到 BaseMarketContext 兼容桥
- 多资产 asset_class / market_type 标准常量与验证工具
- BaseMarketContext 使用 market_constants 标准化
- Phase 2 多资产市场上下文阶段验收

## 当前验证方式

运行最小主流程：

python main.py

预期输出包含：

- FCF minimal spine executed.
- events_recorded: 8

运行测试：

python -m pytest -q

预期输出：

- 37 passed

## 当前关键文件

Phase 2 关键代码：

- fcf/contracts/market_context.py
- fcf/contracts/base_market_context.py
- fcf/contracts/market_constants.py
- fcf/modules/market_context_builder.py
- fcf/modules/market_context_adapter.py

Phase 2 关键测试：

- tests/test_market_context.py
- tests/test_market_context_builder.py
- tests/test_market_context_event_flow.py
- tests/test_base_market_context.py
- tests/test_market_context_adapter.py
- tests/test_market_constants.py

Phase 2 关键文档：

- docs/12_phase2_btc_market_context.md
- docs/13_multi_asset_market_context.md
- docs/14_phase2_market_context_acceptance.md

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

## 下一步

进入 Phase 3：

真实数据接入边界规划。

Phase 3 初期不接真实交易所 API 密钥，不真实下单。

建议先创建：

- docs/15_phase3_data_ingestion_boundary.md

Phase 3 第一阶段目标：

- 创建数据源边界文档
- 规划 mock data adapter
- 规划 raw market data schema
- 规划 replayable input fixture
- 定义数据接入安全边界
- 定义真实 API 接入前的隔离层
- 保持当前 37 个测试通过
