# FCF 项目状态

## 仓库信息

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 46a58fe

## 当前状态

FCF Phase 1：Build Spine 正在推进。

当前已经完成：

- docs/01_vision.md
- docs/02_constitution.md
- docs/03_architecture.md
- docs/04_event_contracts.md
- docs/05_module_contracts.md
- docs/06_runtime_spine.md
- docs/07_tests_and_replay.md
- docs/08_module_runtime.md

D6 已完成：

- Python 包目录骨架已创建
- 最小事件对象已实现
- EventBus 已实现
- EventStore 已实现
- main.py 最小运行入口已实现
- python main.py 已成功跑通

D7 已完成：

- ReplayEngine 已实现
- tests/test_minimal_spine.py 已创建
- python -m pytest -q 已通过
- 当前测试结果：5 passed

D8 已完成第一版：

- DataIngestor 已实现
- Normalizer 已实现
- RegimeRadar 已实现
- StrategyProposer 已实现
- main.py 已改为调用模块生成事件
- python main.py 可运行
- python -m pytest -q 已通过
- 当前测试结果：5 passed

## 当前阶段

D1：项目愿景，已完成。

D2：系统宪法，已完成。

D3：总体架构图与数据流，已完成。

D4：标准事件契约与数据结构，已完成。

D5：模块契约定义，已完成。

D6：文件结构设计与最小可运行骨架，已完成。

D7：最小测试与回放验证，已完成。

D8：模块代码最小落地，已完成第一版。

下一步进入 D9：风控、执行、影子模式最小闭环。

## D9 下一步任务

创建 docs/09_risk_execution_shadow.md。

D9 需要完成：

- policy_engine 最小审核逻辑
- risk_guardian 最小风控逻辑
- executor 最小模拟执行逻辑
- shadow_simulator 最小影子执行逻辑
- main.py 增加风控和执行链路
- tests 增加风控、执行、影子相关测试
- python -m pytest -q 通过

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 46a58fe
current_stage: Phase 1 Build Spine；D1-D5 已完成；D6 最小运行时已跑通；D7 测试与回放已通过；D8 第一批模块代码已落地，main.py 已调用 DataIngestor、Normalizer、RegimeRadar、StrategyProposer，python -m pytest -q 显示 5 passed。
next_action: 读取 PROJECT_STATE.md、main.py、fcf/data/ingestor.py、fcf/data/normalizer.py、fcf/intelligence/regime_radar.py、fcf/decision/strategy_proposer.py、tests/test_minimal_spine.py，然后进入 D9：风控、执行、影子模式最小闭环。
