# D11 - Phase 1 骨架验收与收尾

## 1. 目的

D11 的目标不是新增复杂功能，而是对 Phase 1 Build Spine 做一次稳定性验收。

本阶段确认 D1-D10 的最小系统骨架已经可以稳定运行、测试、回放，并作为后续 Phase 2 的基础。

## 2. 当前阶段

当前项目阶段：

- Phase 1 Build Spine
- D1-D10 已完成
- D11 正在进行 Phase 1 骨架验收与收尾

## 3. 已完成能力

当前系统已经具备：

- 事件契约 FCFEvent
- EventBus
- EventStore
- ReplayEngine
- 数据接入事件
- 数据标准化事件
- regime 检测事件
- decision proposed 事件
- policy reviewed 事件
- risk guardian 审核事件
- executor 执行事件
- shadow simulator 影子模拟事件
- JSONL 事件持久化
- JSONL 事件读取
- 从持久化事件进行回放验证

## 4. main.py 验收结果

当前运行：

python main.py

输出结果应包含：

- FCF minimal spine executed.
- events_recorded: 8

事件链顺序为：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

## 5. pytest 验收结果

当前运行：

python -m pytest -q

输出结果：

- 8 passed

## 6. D10 纠偏记录

D10 曾出现一次错误方向提交：

- a4bca33 add D10 event store persistence foundation

该提交已通过安全 revert 撤销：

- a8d4bd6 Revert "add D10 event store persistence foundation"

当前有效 D10 实现仍以以下提交为准：

- ef8f6ae add D10 audit persistence replay document
- 1cbb143 add D10 jsonl persistence and replay tests

## 7. Phase 1 验收标准

Phase 1 骨架验收需要满足：

- python main.py 稳定输出 events_recorded: 8
- python -m pytest -q 稳定显示 8 passed
- docs/01 到 docs/11 文档存在
- D1-D10 功能边界清晰
- D11 完成后 PROJECT_STATE.md 和 README.md 同步更新
- 所有变更提交并 push 到 GitHub

## 8. 下一步

D11 完成后，Phase 1 Build Spine 进入稳定收尾状态。

下一阶段进入 Phase 2 规划。

Phase 2 不应直接上复杂投注策略，而应先规划：

- 数据输入结构
- 真实比赛上下文
- 市场赔率接入边界
- 风控阈值
- 策略候选生成逻辑
- 回放审计标准
