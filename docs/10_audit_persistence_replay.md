# D10 - 审计日志、事件持久化与回放一致性加强

## 1. 目的

本文档定义 D10 的目标。

D10 的目标是把当前只存在内存里的事件，增强为可以保存、读取、回放和校验的一套最小审计系统。

D10 不接数据库。

D10 不接真实外部服务。

D10 第一版只使用本地 JSONL 文件保存事件。

## 2. 当前基础

当前已经具备：

- FCFEvent
- EventBus
- EventStore
- ReplayEngine
- main.py 最小运行链路
- D9 风控、执行、影子模式最小闭环
- pytest 测试

当前 main.py 可以生成 8 个事件：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

## 3. D10 目标

D10 第一版需要完成：

- EventStore 可以把事件保存到本地 JSONL 文件
- EventStore 可以从本地 JSONL 文件读取事件
- ReplayEngine 可以回放从文件读取的事件
- 回放结果可以检查事件数量
- 回放结果可以检查事件顺序
- 回放结果可以检查事件名称
- pytest 可以验证持久化和回放一致性

## 4. JSONL 文件说明

D10 使用 JSONL 作为第一版事件持久化格式。

JSONL 的规则是：

- 一行一个事件
- 每一行都是一个 JSON 对象
- 文件可以追加写入
- 文件可以逐行读取
- 方便调试和审计

## 5. D10 验收标准

D10 第一版完成需要满足：

- docs/10_audit_persistence_replay.md 已创建
- EventStore 支持 save_jsonl
- EventStore 支持 load_jsonl
- ReplayEngine 可以回放读取后的事件
- tests 增加持久化测试
- python -m pytest -q 通过
- 所有变更提交并推送到 GitHub

## 6. 当前状态

本文档是 D10 第一版草稿。

下一步修改 EventStore 和 ReplayEngine，并增加持久化测试。
