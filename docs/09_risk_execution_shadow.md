# D9 - 风控、执行、影子模式最小闭环

## 1. 目的

本文档定义 D9 的目标。

D9 的目标是把 D8 已经跑通的最小事件链，继续扩展到风控、执行和影子模式。

D9 不接真实资金。

D9 不接真实交易接口。

D9 只实现最小闭环：

- 决策提案进入风控审核
- 风控决定是否通过
- 通过后生成批准订单
- 执行器模拟执行
- 影子模拟器可以模拟影子结果
- 测试验证事件链完整

## 2. 当前基础

当前已经具备：

- DataIngestor
- Normalizer
- RegimeRadar
- StrategyProposer
- FCFEvent
- EventBus
- EventStore
- ReplayEngine
- pytest 测试

## 3. D9 第一批模块

D9 第一版落地以下模块：

- policy_engine
- risk_guardian
- executor
- shadow_simulator

## 4. D9 最小事件链

D9 完成后，最小事件链应扩展为：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

## 5. D9 验收标准

D9 第一版完成需要满足：

- policy_engine 可以审核提案
- risk_guardian 可以批准低风险提案
- executor 可以模拟执行批准订单
- shadow_simulator 可以生成影子模拟事件
- main.py 可以跑通完整最小链路
- python -m pytest -q 可以通过
- 所有变更已提交并推送到 GitHub

## 6. 当前状态

本文档是 D9 第一版草稿。

下一步写入 D9 第一批模块代码。
