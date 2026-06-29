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


## 7. 通用事件结构

所有 FCF 事件都必须遵守统一外壳结构。

事件外壳用于保证事件可以被追踪、审计、排序和回放。

| 字段 | 是否必填 | 说明 |
|---|---|---|
| event_id | 必填 | 当前事件的唯一编号 |
| event_name | 必填 | 标准事件名称 |
| event_version | 必填 | 事件契约版本 |
| event_time | 必填 | 事件发生时间 |
| sequence_id | 必填 | 单调递增事件序号 |
| source_module | 必填 | 产生事件的模块 |
| correlation_id | 必填 | 同一决策链路的编号 |
| causation_id | 必填 | 触发当前事件的上游事件编号 |
| payload | 必填 | 事件主体内容 |
| metadata | 必填 | 审计、环境、追踪信息 |

## 8. 字段解释

event_id 用来唯一标识一个事件。

event_name 用来说明事件类型。

event_version 用来保证以后事件格式升级时仍然可以兼容旧事件。

event_time 记录事件发生时间。

sequence_id 用来保证回放顺序。

source_module 记录事件来源模块。

correlation_id 用来把同一次决策链路中的多个事件串起来。

causation_id 用来记录当前事件由哪个上游事件触发。

payload 保存业务数据。

metadata 保存审计信息、运行环境和追踪信息。


## 9. payload 设计原则

payload 是事件的业务主体数据。

不同事件可以有不同 payload，但必须遵守以下原则：

- payload 只保存当前事件真正需要的数据
- payload 不能保存无法解释的临时对象
- payload 不能依赖某个模块的私有内部结构
- payload 必须可以被序列化保存
- payload 必须可以被回放系统重新读取
- payload 中的关键字段必须有明确含义

## 10. payload 类型分类

D4 第一版把 payload 分为以下几类：

| 类型 | 说明 |
|---|---|
| data_payload | 数据接入和标准化事件使用 |
| market_payload | 市场快照和盘口状态事件使用 |
| model_payload | 特征和模型评估事件使用 |
| decision_payload | 决策提案事件使用 |
| policy_payload | 风控审核事件使用 |
| order_payload | 订单批准和执行事件使用 |
| shadow_payload | 影子模拟事件使用 |
| replay_payload | 回放事件使用 |

## 11. payload 最低要求

每个 payload 至少要满足：

- 能说明当前事件发生了什么
- 能支持后续模块继续处理
- 能支持审计人员理解事件
- 能支持回放系统重建过程
- 不能只保存一句自然语言解释

