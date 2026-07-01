# P4-D7 - Schema Batch Error Behavior and Dify Batch Tests

## 1. 目的

P4-D7 明确 batch market input 遇到 schema error 时的行为，并增加 Dify batch tests。

当前策略：

batch 中任意一行 schema 校验失败，整个 batch 失败。
不做部分成功。
不写入部分成功事件。
不伪装成功。
Dify HTTP adapter 返回 http_status 422。
local_market_input_api 返回 ok false。
Dify response templates 转成 user-facing error response。

## 2. 覆盖场景

P4-D7 覆盖：

- batch success schema normalization
- batch missing required field
- batch bad market_type
- batch bad spread
- batch bad asset_class
- batch bad number

## 3. 预期行为

成功时：

- http_status = 200
- body.ok = true
- body.data.schema = raw_market_input_schema
- body.data.event_count = 2
- symbols 已归一化
- market_types 已归一化

失败时：

- http_status = 422
- body.ok = false
- body.error.type = ValueError
- body.error.message 包含对应字段
- render_dify_user_response 返回 response_type error
- user-facing response 保留安全边界说明

## 4. 安全边界

P4-D7 不接真实交易所 API。
P4-D7 不保存真实 API key。
P4-D7 不读取钱包私钥。
P4-D7 不真实下单。
P4-D7 不让 Dify 成为底层交易内核。
P4-D7 不把 pipeline 成功伪装成真实交易成功。

## 5. 验收标准

P4-D7 完成需要满足：

- 新增 docs/30_p4_schema_batch_error_behavior.md
- 新增 tests/test_schema_batch_dify_adapter_errors.py
- batch success 测试通过
- batch schema error 422 测试通过
- schema error 能转成 user-facing error response
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 通过

