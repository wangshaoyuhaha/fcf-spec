# D8 - 模块代码最小落地

## 1. 目的

本文档定义 D8 的目标。

D8 的目标是把 D5 中定义的部分模块，从空文件变成可以运行的最小代码。

D8 不追求完整策略能力。

D8 只要求核心模块可以接收输入、生成标准事件，并串成最小运行链路。

## 2. 当前基础

当前已经具备：

- FCFEvent
- create_event
- EventBus
- EventStore
- ReplayEngine
- main.py 最小运行入口
- pytest 最小测试

## 3. D8 第一批模块

D8 第一批落地以下模块：

- data_ingestor
- normalizer
- regime_radar
- strategy_proposer

## 4. D8 目标

D8 完成后，main.py 不再手动创建全部事件。

main.py 应该调用模块，让模块自己生成事件。

目标链路：

1. data_ingestor 生成 fcf.data.raw_received
2. normalizer 接收 raw 事件，生成 fcf.data.normalized
3. regime_radar 接收 normalized 事件，生成 fcf.regime.detected
4. strategy_proposer 接收 regime 事件，生成 fcf.decision.proposed
5. EventStore 保存全部事件
6. pytest 测试通过

## 5. D8 验收标准

D8 第一版完成需要满足：

- 相关模块文件已写入最小代码
- main.py 可以调用模块运行
- python main.py 可以运行
- python -m pytest -q 可以通过
- 所有变更已提交并推送到 GitHub

## 6. 当前状态

本文档是 D8 第一版草稿。

下一步写入第一批模块代码。
