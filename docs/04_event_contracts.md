# D4 - FCF 标准事件契约与数据结构

## 1. 目的

本文档定义 FCF 系统的标准事件格式。

D4 的目标是让所有模块都通过统一事件通信。

所有事件都必须可以被记录、审计、回放和测试。

## 2. 事件命名规则

事件名称采用：

模块域.对象.动作

示例：

- fcf.data.raw_received
- fcf.data.normalized
- fcf.decision.proposed
- fcf.policy.reviewed
- fcf.order.executed
- fcf.shadow.simulated
- fcf.replay.completed

命名规则：

- 全部小写
- 单词之间使用下划线
- 事件名表示已经发生的事实
- 不在事件名里写具体策略名称
- 不在事件名里写临时实验名称

## 3. 事件基础字段

所有事件必须包含：

- event_id
- event_name
- event_version
- event_time
- sequence_id
- source_module
- correlation_id
- causation_id
- payload
- metadata

## 4. 最小可回放要求

为了保证系统可以回放，每个事件必须记录：

- 事件发生时间
- 事件顺序编号
- 事件来源模块
- 上游触发事件
- 同一决策链路编号
- 事件主体数据
- 审计元数据

其中 sequence_id 必须单调递增。

如果没有 sequence_id，就不能保证严格回放顺序。

## 5. D4 第一版事件列表

D4 第一版先定义以下事件：

- fcf.data.raw_received
- fcf.data.normalized
- fcf.market.snapshot_created
- fcf.regime.detected
- fcf.feature.generated
- fcf.model.evaluated
- fcf.decision.proposed
- fcf.policy.reviewed
- fcf.risk.rejected
- fcf.order.approved
- fcf.order.executed
- fcf.shadow.simulated
- fcf.circuit_breaker.triggered
- fcf.replay.started
- fcf.replay.completed

## 6. 当前状态

这是 D4 的第一版短草稿。

后续继续补充：

- 每类事件的字段表
- JSON 示例
- 决策提案结构
- 风控审核结构
- 执行结果结构
- 影子模拟结构
- 回放结构

