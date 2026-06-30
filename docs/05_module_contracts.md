# D5 - FCF 模块契约定义

## 1. 目的

本文档定义 FCF 系统中各个核心模块的职责、输入、输出和边界。

D5 的目标是让每个模块都能独立开发、替换、测试和回放。

模块之间不能依赖彼此的内部实现。

模块之间只能通过标准事件和标准契约通信。

## 2. 模块契约原则

FCF 的模块契约遵守以下原则：

- 每个模块必须职责单一
- 每个模块必须有明确输入
- 每个模块必须有明确输出
- 每个模块不能直接读取其他模块内部状态
- 每个模块必须通过事件总线通信
- 每个模块必须可以被替换
- 每个模块的输出必须可以被审计
- 关键模块失败时必须触发降级或熔断

## 3. 第一版核心模块列表

D5 第一版先定义以下核心模块：

| 模块 | 中文名称 | 所属层级 |
|---|---|---|
| data_ingestor | 数据接入器 | 数据接入层 |
| normalizer | 数据标准化器 | 数据标准化层 |
| event_bus | 事件总线 | 事件总线层 |
| regime_radar | 状态雷达 | 智能分析层 |
| feature_engine | 特征引擎 | 智能分析层 |
| model_engine | 模型引擎 | 智能分析层 |
| strategy_proposer | 策略提案器 | 决策提案层 |
| policy_engine | 治理规则引擎 | 风控治理层 |
| risk_guardian | 风险守卫 | 风控治理层 |
| capital_manager | 资金管理器 | 风控治理层 |
| executor | 执行器 | 执行层 |
| event_store | 事件存储 | 审计与回放层 |
| replay_engine | 回放引擎 | 审计与回放层 |
| shadow_simulator | 影子模拟器 | 审计与回放层 |

## 4. 当前状态

这是 D5 的第一版短草稿。

后续继续补充每个模块的：

- 职责
- 输入事件
- 输出事件
- 禁止行为
- 失败处理方式
- 可替换条件


## 5. data_ingestor 数据接入器

### 职责

data_ingestor 负责接收外部原始数据。

它只负责接入，不负责判断，不负责预测，不负责决策。

可接入的数据包括：

- 盘口数据
- 赔率数据
- 比赛数据
- 新闻数据
- 伤病数据
- 天气数据
- 赛程数据
- 流动性数据

### 输入

data_ingestor 的输入来自外部系统，不直接依赖 FCF 内部模块。

输入可以包括：

- 外部 API
- 手动导入文件
- 网页抓取结果
- 第三方数据源

### 输出事件

data_ingestor 输出：

- fcf.data.raw_received

### 禁止行为

data_ingestor 禁止：

- 判断是否下注
- 修改策略参数
- 生成决策提案
- 调用执行器
- 直接写入风控结果

### 失败处理

如果 data_ingestor 失败，系统应记录数据接入失败事件。

如果连续失败达到阈值，应触发降级或硬熔断。

## 6. normalizer 数据标准化器

### 职责

normalizer 负责把外部原始数据转换成 FCF 内部统一格式。

它负责处理字段命名、时间格式、数据单位、缺失值和基础质量评分。

### 输入事件

normalizer 输入：

- fcf.data.raw_received

### 输出事件

normalizer 输出：

- fcf.data.normalized
- fcf.market.snapshot_created

### 禁止行为

normalizer 禁止：

- 判断交易方向
- 生成决策提案
- 修改资金参数
- 调用执行器
- 绕过事件总线直接调用智能分析模块

### 失败处理

如果 normalizer 无法解析数据，应输出错误记录。

如果数据质量低于阈值，应降低 quality_score，并允许风控层后续处理。

## 7. event_bus 事件总线

### 职责

event_bus 负责在系统模块之间传递标准事件。

event_bus 不理解策略含义，只负责传递、排序和分发事件。

### 输入

event_bus 接收所有标准事件。

### 输出

event_bus 将事件分发给订阅模块。

### 禁止行为

event_bus 禁止：

- 修改事件 payload
- 判断事件业务含义
- 生成交易信号
- 过滤风控事件
- 私自丢弃关键事件

### 失败处理

如果 event_bus 不可用，系统必须进入 DEGRADED 或 SHADOW。

如果事件顺序无法保证，系统不能进入 LIVE。


## 8. regime_radar 状态雷达

### 职责

regime_radar 负责识别当前系统、市场或比赛所处的状态。

它的任务是先判断环境，再决定后续是否允许预测或提案。

### 输入事件

regime_radar 输入：

- fcf.data.normalized
- fcf.market.snapshot_created

### 输出事件

regime_radar 输出：

- fcf.regime.detected

### 禁止行为

regime_radar 禁止：

- 直接生成订单
- 直接调用执行器
- 修改资金参数
- 绕过风控治理层
- 把状态识别结果当成最终决策

### 失败处理

如果状态无法识别，系统应降低置信度。

如果状态识别模块不可用，系统不能进入激进执行状态。

## 9. feature_engine 特征引擎

### 职责

feature_engine 负责把标准化数据转换成模型和策略可使用的特征。

特征必须可以追踪来源，不能只生成无法解释的黑箱结果。

### 输入事件

feature_engine 输入：

- fcf.data.normalized
- fcf.market.snapshot_created
- fcf.regime.detected

### 输出事件

feature_engine 输出：

- fcf.feature.generated

### 禁止行为

feature_engine 禁止：

- 直接生成决策提案
- 直接判断下注方向
- 调用执行器
- 修改风控规则
- 使用不可回放的临时数据

### 失败处理

如果特征生成失败，应记录失败原因。

如果关键特征缺失，后续模型必须降低置信度或停止提案。

## 10. model_engine 模型引擎

### 职责

model_engine 负责运行统计模型、预测模型或评分模型。

它输出模型评估结果，但不直接产生真实订单。

### 输入事件

model_engine 输入：

- fcf.feature.generated
- fcf.regime.detected

### 输出事件

model_engine 输出：

- fcf.model.evaluated

### 禁止行为

model_engine 禁止：

- 直接执行交易
- 绕过策略提案层
- 绕过风控治理层
- 私自修改训练数据
- 把模型分数直接当成订单

### 失败处理

如果模型不可用，系统应进入降级模式。

如果模型输出异常，必须记录异常并阻止自动提案。

## 11. strategy_proposer 策略提案器

### 职责

strategy_proposer 负责把状态、特征和模型结果组合成标准决策提案。

决策提案不是订单。

提案必须经过风控治理层审核后，才能变成可执行订单。

### 输入事件

strategy_proposer 输入：

- fcf.regime.detected
- fcf.feature.generated
- fcf.model.evaluated

### 输出事件

strategy_proposer 输出：

- fcf.decision.proposed

### 禁止行为

strategy_proposer 禁止：

- 直接调用 executor
- 直接影响真实资金
- 绕过 policy_engine
- 绕过 risk_guardian
- 修改已生成的历史提案

### 失败处理

如果提案生成失败，应记录失败原因。

如果输入信息不足，应拒绝生成提案，而不是强行输出低质量提案。


## 12. policy_engine 治理规则引擎

### 职责

policy_engine 负责根据系统规则审核决策提案。

它判断提案是否违反系统宪法、事件契约、资金规则和风险限制。

policy_engine 不负责预测，也不负责执行。

### 输入事件

policy_engine 输入：

- fcf.decision.proposed
- fcf.regime.detected
- fcf.model.evaluated

### 输出事件

policy_engine 输出：

- fcf.policy.reviewed

### 禁止行为

policy_engine 禁止：

- 直接调用执行器
- 修改模型输出
- 修改历史提案
- 忽略硬熔断规则
- 因收益理由绕过风险规则

### 失败处理

如果 policy_engine 不可用，系统不能进入 LIVE。

如果规则判断不确定，默认进入 shadow_only 或 rejected。

## 13. risk_guardian 风险守卫

### 职责

risk_guardian 负责识别系统级风险、冲突风险、熔断风险和异常执行风险。

risk_guardian 拥有触发硬熔断的权力。

### 输入事件

risk_guardian 输入：

- fcf.decision.proposed
- fcf.policy.reviewed
- fcf.order.approved
- fcf.order.executed
- fcf.data.normalized
- fcf.market.snapshot_created

### 输出事件

risk_guardian 输出：

- fcf.risk.rejected
- fcf.circuit_breaker.triggered
- fcf.order.approved

### 禁止行为

risk_guardian 禁止：

- 因模型置信度高而忽略风险
- 因短期收益绕过熔断
- 私自提高仓位
- 删除风险事件
- 隐藏冲突信息

### 失败处理

如果 risk_guardian 不可用，系统必须停止真实执行。

如果发现同场冲突、滑点异常、数据质量崩溃或连续执行异常，必须进入 SHADOW 或 STOPPED。

## 14. capital_manager 资金管理器

### 职责

capital_manager 负责控制仓位、限额、资金暴露和单次执行规模。

它不判断方向，只判断资金是否允许。

### 输入事件

capital_manager 输入：

- fcf.decision.proposed
- fcf.policy.reviewed
- fcf.risk.rejected

### 输出事件

capital_manager 输出：

- fcf.policy.reviewed
- fcf.risk.rejected

### 禁止行为

capital_manager 禁止：

- 判断比赛结果
- 生成策略提案
- 直接调用执行器
- 超过系统限额
- 绕过 risk_guardian

### 失败处理

如果 capital_manager 不可用，系统不能执行真实订单。

如果资金暴露超过阈值，必须拒绝新提案或降低仓位。

