# D6 - FCF 文件结构设计与最小可运行骨架

## 1. 目的

本文档定义 FCF 项目的运行骨架。

D6 的目标是把前面的文档契约，落到实际文件结构和 Python 包结构上。

D6 不追求完整功能。

D6 只要求系统具备最小可运行能力：

- 有清晰目录结构
- 有模块文件位置
- 有统一事件对象
- 有最小事件流
- 有 main.py 入口
- 可以跑通一次模拟流程

## 2. 当前仓库结构

当前仓库基础结构为：

- README.md
- PROJECT_STATE.md
- main.py
- docs/
- fcf/

文档目录 docs/ 当前包括：

- 01_vision.md
- 02_constitution.md
- 03_architecture.md
- 04_event_contracts.md
- 05_module_contracts.md
- 06_runtime_spine.md

## 3. 目标 Python 包结构

D6 目标结构如下：

fcf/
  __init__.py
  contracts/
    __init__.py
    event.py
  core/
    __init__.py
    event_bus.py
    event_store.py
  data/
    __init__.py
    ingestor.py
    normalizer.py
  intelligence/
    __init__.py
    regime_radar.py
    feature_engine.py
    model_engine.py
  decision/
    __init__.py
    strategy_proposer.py
  risk/
    __init__.py
    policy_engine.py
    risk_guardian.py
    capital_manager.py
  execution/
    __init__.py
    executor.py
  shadow/
    __init__.py
    simulator.py
  replay/
    __init__.py
    replay_engine.py

## 4. 最小运行链路

D6 的最小运行链路为：

1. main.py 启动系统
2. data_ingestor 生成 fcf.data.raw_received
3. normalizer 生成 fcf.data.normalized
4. event_bus 分发事件
5. regime_radar 生成 fcf.regime.detected
6. feature_engine 生成 fcf.feature.generated
7. model_engine 生成 fcf.model.evaluated
8. strategy_proposer 生成 fcf.decision.proposed
9. policy_engine 审核提案
10. risk_guardian 决定是否允许执行
11. executor 模拟执行
12. event_store 保存事件
13. replay_engine 可以读取事件并重建流程

## 5. D6 验收标准

D6 完成需要满足：

- Python 包结构已经创建
- 每个核心模块都有对应文件
- main.py 可以运行
- 系统可以生成一条最小事件链
- 事件可以被 event_store 保存
- replay_engine 可以读取事件
- 不接真实资金
- 不接真实外部 API
- 所有变更已提交并推送到 GitHub

## 6. 当前状态

本文档是 D6 的第一版草稿。

下一步将创建实际目录和空模块文件。
