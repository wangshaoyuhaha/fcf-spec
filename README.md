# FCF Spec

FCF Spec 是一个全金融市场 / 多资产交易系统的最小事件骨架项目。

## 当前定位

本项目不是足球系统。

本项目也不是只做 BTC。

当前目标是构建一个可以逐步适配全金融市场的事件驱动交易系统骨架。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

Phase 2 多资产市场上下文基础层已完成阶段验收。

Phase 3 已启动，当前重点是数据接入边界、mock 数据接入和可回放输入。

Dify 后续会作为上层工作流 / 对话入口 / 编排层接入，不作为底层交易内核。

## 当前阶段

- Phase 1 Build Spine 已完成稳定收尾
- D1-D11 已完成
- Phase 2 多资产市场上下文基础层已完成阶段验收
- P2-D1 到 P2-D10 已完成
- Phase 3 已启动
- P3-D1：真实数据接入边界规划已完成
- P3-D2：mock market data adapter 已完成
- P3-D3：replayable raw market fixture 已完成

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
- Phase 2 多资产市场上下文基础层
- Phase 3 数据接入边界规划
- mock market data adapter
- replayable raw market fixture

## 当前验证方式

运行最小主流程：

python main.py

预期输出包含：

- FCF minimal spine executed.
- events_recorded: 8

运行测试：

python -m pytest -q

预期输出：

- 48 passed

## 当前关键代码

- fcf/modules/mock_market_data_adapter.py
- tests/test_mock_market_data_adapter.py
- tests/test_raw_market_fixture_replay.py

## 当前关键数据

- fixtures/raw_market_data_crypto.json

## 当前关键文档

- docs/14_phase2_market_context_acceptance.md
- docs/15_phase3_data_ingestion_boundary.md

## Phase 3 边界

Phase 3 初期不接真实交易所 API 密钥。

Phase 3 初期不真实下单。

Phase 3 初期只做：

- 数据源边界文档
- mock data adapter
- raw market data schema
- replayable input fixture
- 数据接入安全边界
- 真实 API 接入前的隔离层

## Dify 接入路线

Dify 预计在 P3-D5 开始正式规划。

建议路线：

- P3-D4：本地 system input pipeline / 外部调用边界
- P3-D5：Dify workflow 接入规划

## 下一步

进入 P3-D4：

本地 system input pipeline / 外部调用边界。

建议新增：

- fcf/pipelines/market_input_pipeline.py
- tests/test_market_input_pipeline.py

P3-D4 目标：

- 输入 raw market dict
- 调用 mock_market_data_adapter
- 生成 raw market event
- 保存到 EventStore
- 调用 ReplayEngine 回放
- 输出可给外部系统调用的 summary dict
- 为后续 Dify workflow 接入做准备
- 不接真实交易所 API
- 不真实下单
- 保持当前测试通过
