# D7 - 最小测试与回放验证

## 1. 目的

本文档定义 FCF 第一版最小测试与回放验证。

D7 的目标是确认 D6 的最小事件运行时不是只能打印结果，而是可以被测试、验证和回放。

## 2. 当前基础

D6 已经完成：

- FCFEvent 事件对象
- create_event 事件创建函数
- EventBus 事件总线
- EventStore 事件存储
- main.py 最小运行入口
- python main.py 可以跑通 4 个事件

当前最小事件链包括：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed

## 3. D7 测试目标

D7 第一版需要验证：

- main.py 可以正常运行
- 最小事件链可以生成
- EventStore 可以保存事件
- 事件数量正确
- 事件顺序正确
- sequence_id 单调递增
- correlation_id 保持一致
- causation_id 可以连接上下游事件
- replay_engine 可以读取事件并返回回放结果

## 4. 测试范围

D7 暂时不测试真实外部 API。

D7 暂时不测试真实交易执行。

D7 暂时不测试真实模型预测。

D7 只验证系统骨架是否能稳定产生、保存和回放事件。

## 5. 计划新增文件

D7 计划新增：

- tests/
- tests/test_minimal_spine.py

D7 计划补充：

- fcf/replay/replay_engine.py

## 6. 验收标准

D7 完成需要满足：

- tests/ 目录已创建
- 最小测试文件已创建
- pytest 可以运行
- 事件数量测试通过
- 事件顺序测试通过
- correlation_id 测试通过
- replay_engine 测试通过
- 所有变更已提交并推送到 GitHub

## 7. 当前状态

本文档是 D7 第一版测试与回放验证草稿。

下一步创建 tests/ 目录，并添加最小测试。
