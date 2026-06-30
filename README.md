# FCF Spec

FCF Spec 是一个全金融市场 / 多资产交易系统的最小事件骨架项目。

## 当前定位

本项目不是足球系统。

本项目也不是只做 BTC。

当前目标是构建一个可以逐步适配全金融市场的事件驱动交易系统骨架。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

BaseMarketContext 是当前新增的通用多资产上下文契约。

market_constants 是多资产 asset_class / market_type 标准常量与验证工具。

## 当前阶段

- Phase 1 Build Spine 已完成稳定收尾
- D1-D11 已完成
- Phase 2 已启动
- P2-D1：BTC Market Context 规划已完成
- P2-D2：BTCMarketContext 契约已完成
- P2-D3：BTCMarketContext 最小标准化模块已完成
- P2-D4：market context 事件化测试已完成
- P2-D5：多资产 MarketContext / AssetMarketContext 泛化层规划已完成
- P2-D6：通用 BaseMarketContext 最小契约已完成
- P2-D7：BTCMarketContext 到 BaseMarketContext 轻量兼容桥已完成
- P2-D8：多资产 asset_class / market_type 标准常量与验证工具已完成
- P2-D9：BaseMarketContext 使用 market_constants 标准化已完成

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

## 当前新增代码与文档

P2-D6 新增：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

P2-D7 新增：

- fcf/modules/market_context_adapter.py
- tests/test_market_context_adapter.py

P2-D8 新增：

- fcf/contracts/market_constants.py
- tests/test_market_constants.py

P2-D9 修改：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

## P2-D9 能力

BaseMarketContext 当前支持：

- 使用 market_constants.normalize_asset_class
- 使用 market_constants.normalize_market_type
- normalized_asset_class
- normalized_market_type
- to_dict 输出标准化 asset_class
- to_dict 输出标准化 market_type
- base_market_context_from_dict 标准化 asset_class
- base_market_context_from_dict 标准化 market_type

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

进入 P2-D10：

Phase 2 多资产市场上下文阶段验收与收尾。

建议新增：

- docs/14_phase2_market_context_acceptance.md

P2-D10 目标：

- 不继续无限加功能
- 总结 P2-D1 到 P2-D9 已完成内容
- 固化当前多资产 MarketContext 基础层
- 确认 main.py 仍稳定输出 events_recorded: 8
- 确认 python -m pytest -q 仍稳定通过
- 更新 README.md
- 更新 PROJECT_STATE.md
- 生成新的续聊话术
