# P4-D8 - Schema Hardening Closeout and Phase 4 Midpoint Acceptance

## 1. 目的

P4-D8 用于汇总 P4-D1 到 P4-D7 的 schema hardening 成果，并形成 Phase 4 中段验收文档。

P4-D8 不改核心交易逻辑。
P4-D8 不接真实交易所 API。
P4-D8 不保存真实 API key。
P4-D8 不读取钱包私钥。
P4-D8 不真实下单。

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。

## 3. P4-D1 到 P4-D7 完成范围

已完成：

- P4-D1：Schema hardening plan
- P4-D2：raw market input schema module
- P4-D3：schema integration into market input pipeline
- P4-D4：schema-aware Dify adapter and response tests
- P4-D5：schema error catalog and stable error messages
- P4-D6：integrate schema error catalog into raw market input schema
- P4-D7：schema batch error behavior and Dify batch tests

## 4. 当前 raw market input schema 能力

当前 schema 能力：

- 必填字段检查
- 可选数字字段归一化
- 数字类型转换
- asset_class normalization
- market_type normalization
- symbol normalization
- venue normalization
- last_price 正数校验
- volume / quote_volume / depth 非负校验
- best_bid <= best_ask 校验
- stable schema description
- stable schema error catalog
- stable error message builder

## 5. 当前支持的必填字段

当前必填字段：

- asset_class
- symbol
- venue
- market_type
- timestamp
- timeframe
- source
- source_type
- last_price

## 6. 当前支持的可选字段

当前可选数字字段：

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

## 7. 当前支持的 asset_class

当前支持：

- crypto
- equities
- fx
- commodities
- rates
- index
- futures
- options

## 8. 当前支持的 market_type

当前归一化支持：

- spot -> spot
- perp -> perpetual
- perpetual -> perpetual
- future -> futures
- futures -> futures
- option -> option
- options -> option

## 9. 当前 schema error catalog

当前错误类型：

- MissingField
- InvalidEnumValue
- InvalidNumber
- InvalidPositiveNumber
- InvalidNonNegativeNumber
- InvalidSpread
- InvalidPayloadType

## 10. 当前 Dify adapter schema error 行为

当前 Dify HTTP adapter 行为：

- single schema success 返回 200
- single schema error 返回 422
- batch schema success 返回 200
- batch 中任意一行 schema error，整个 batch 返回 422
- 不做部分成功
- 不写入部分成功事件
- local_market_input_api 返回 ok false
- response templates 转成 user-facing error response

## 11. 当前 batch error 策略

当前策略：

batch 中任意一行 schema 校验失败，整个 batch 失败。

原因：

- 避免部分数据进入事件链造成回放不一致
- 避免 Dify 把部分成功误解为全部成功
- 保持 EventStore / ReplayEngine 的审计清晰
- 保持 workflow 分支简单

## 12. 当前验证命令

当前主流程：

python main.py

预期：

events_recorded: 8

当前 Dify HTTP adapter smoke：

python scripts/run_dify_http_adapter_smoke.py

预期：

status completed

当前 Dify integration smoke：

python scripts/run_dify_integration_smoke.py

预期：

status completed

当前测试：

python -m pytest -q

预期：

116 passed

## 13. 安全边界

当前仍然保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核
- 不绕过 EventStore
- 不绕过 ReplayEngine
- 不把 pipeline 成功伪装成真实交易成功

## 14. P4-D8 验收结论

P4-D8 完成后，Phase 4 schema hardening 已达到中段验收点。

当前系统已经从“能接收 mock raw market input”增强为：

- 有 schema 边界
- 有错误目录
- 有稳定错误消息
- 有 Dify adapter 422 行为
- 有 batch 整体失败策略
- 有用户可见 error response
- 有完整 pytest 覆盖

## 15. 下一步建议

下一步进入 P4-D9：multi-asset fixture expansion plan。

建议目标：

- 新增多资产 fixture 扩展规划
- 设计 crypto / equities / fx / commodities 的 fixture 样例字段
- 不一次性接真实数据源
- 不接真实交易所 API
- 不真实下单
- 保持 schema 兼容

