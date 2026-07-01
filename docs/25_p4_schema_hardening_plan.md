# P4-D1 - Schema Hardening Plan

## 1. 目的

P4-D1 开始进入 Phase 4。

Phase 4 第一目标是强化 raw market input 的 schema 边界，让系统对市场输入的字段、类型、必填项、可选项、多资产兼容规则有更明确的约束。

P4-D1 只做规划文档。
P4-D1 不接真实交易所 API。
P4-D1 不保存真实 API key。
P4-D1 不读取钱包私钥。
P4-D1 不真实下单。
P4-D1 不破坏现有测试。

## 2. 当前背景

Phase 3 已完成数据接入与 Dify integration 的阶段收尾。

当前已经具备：

- mock market data adapter
- replayable raw market fixture
- market input pipeline
- local_market_input_api
- dify_http_adapter
- dify_response_templates
- smoke runner
- integration smoke

当前 wrapper 已能返回稳定 response dict：

- ok
- api
- api_version
- error
- data

下一步需要把 raw market input 的 schema 变硬，减少模糊输入、字段缺失、类型混乱、多资产扩展失控等问题。

## 3. Schema Hardening 总原则

P4 schema hardening 遵守以下原则：

- Contract First
- Event Driven
- Every Decision Replayable
- Policy Above Intelligence
- Dify is not trading core
- No real exchange API
- No real order placement
- No secret storage

schema 层只负责输入边界。
schema 层不负责收益判断。
schema 层不负责真实下单。
schema 层不负责连接真实交易所。

## 4. Raw Market Input 必填字段

当前建议必填字段：

- asset_class
- symbol
- venue
- market_type
- timestamp
- timeframe
- source
- source_type
- last_price

说明：

asset_class 用于区分资产类别。
symbol 用于标识交易标的。
venue 用于标识市场或交易场所。
market_type 用于区分 spot、perp、futures 等市场结构。
timestamp 用于事件时间。
timeframe 用于行情周期。
source 用于标识输入来源。
source_type 用于区分 mock、manual、fixture、adapter 等来源类型。
last_price 是最小行情输入必须具备的价格字段。

## 5. Raw Market Input 可选字段

当前建议可选字段：

- open
- high
- low
- close
- volume
- quote_volume
- best_bid
- best_ask
- bid_depth
- ask_depth

说明：

这些字段用于增强行情上下文。
缺失时不一定阻断全部输入。
但如果字段存在，必须通过类型转换和合法性校验。

## 6. 类型转换规则

当前建议规则：

- symbol 转为大写字符串
- venue 转为小写字符串
- asset_class 转为小写字符串
- market_type 转为标准枚举字符串
- timestamp 必须是非空字符串，后续可强化为 ISO 时间
- timeframe 必须是非空字符串
- 数字字段允许从字符串输入
- 数字字段必须能转换为 float
- last_price 必须大于 0
- volume 如果存在，必须大于等于 0
- bid_depth 如果存在，必须大于等于 0
- ask_depth 如果存在，必须大于等于 0
- best_bid 和 best_ask 如果同时存在，建议 best_bid 小于等于 best_ask

## 7. Market Type 归一化规则

建议支持：

- spot -> spot
- SPOT -> spot
- perp -> perpetual
- PERP -> perpetual
- perpetual -> perpetual
- futures -> futures
- FUTURES -> futures
- option -> option
- options -> option

非法 market_type 应返回 ValueError。

## 8. Asset Class 兼容策略

当前建议支持资产类别：

- crypto
- equities
- fx
- commodities
- rates
- index
- futures
- options

P4-D1 不要求一次性实现所有资产规则。
P4-D1 只定义兼容方向。

后续可以在 P4-D2 / P4-D3 中逐步实现：

- crypto 最小 schema
- equities 最小 schema
- fx 最小 schema
- commodities 最小 schema

## 9. 错误响应要求

schema hardening 的错误必须被 wrapper 包装成稳定 response dict。

错误响应继续保持：

- ok = false
- api
- api_version
- error.type
- error.message
- data = null

示例错误类型：

- MissingField
- InvalidFieldType
- InvalidEnumValue
- InvalidPrice
- InvalidDepth
- InvalidSpread

当前可以先用 ValueError。
后续再逐步引入更细的错误类型。

## 10. Dify 接入要求

Dify 仍然只做：

- 收集输入
- 整理字段
- 预检查字段
- 调用受控 wrapper
- 展示 FCF response
- 展示用户可见模板

Dify 禁止：

- 直接连接真实交易所
- 保存真实 API key
- 读取钱包私钥
- 真实下单
- 绕过 schema
- 绕过 EventStore
- 绕过 ReplayEngine
- 绕过 policy / risk

## 11. P4-D1 验收标准

P4-D1 完成需要满足：

- 新增 docs/25_p4_schema_hardening_plan.md
- README 更新 P4-D1 状态
- PROJECT_STATE 更新 P4-D1 状态
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 通过
- 不接真实交易所 API
- 不真实下单

## 12. 下一步建议

下一步进入 P4-D2：raw market input schema module。

建议新增：

- fcf/schemas/raw_market_input_schema.py
- tests/test_raw_market_input_schema.py

P4-D2 目标：

- 实现 required field check
- 实现 optional field normalize
- 实现 number conversion
- 实现 market_type normalization
- 实现 asset_class normalization
- 保持 local_market_input_api 返回稳定 response dict
- 不接真实交易所 API
- 不真实下单

