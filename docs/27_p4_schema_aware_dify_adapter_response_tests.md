# P4-D4 - Schema-aware Dify Adapter and Response Tests

## 1. 目的

P4-D4 增加 schema-aware Dify adapter and response tests。

P4-D3 已经把 raw_market_input_schema 接入 market_input_pipeline。
P4-D4 的目标是确认 Dify HTTP adapter 和 Dify response templates 能正确处理 schema error。

## 2. 覆盖场景

P4-D4 覆盖：

- schema normalized success
- missing required field
- bad market_type
- bad spread
- bad asset_class
- schema error to user-facing error response

## 3. 预期行为

当 schema 校验通过时：

- Dify HTTP adapter 返回 http_status 200
- body.ok 为 true
- data.schema 为 raw_market_input_schema
- data.symbol 已归一化
- data.market_type 已归一化

当 schema 校验失败时：

- Dify HTTP adapter 返回 http_status 422
- body.ok 为 false
- body.error.type 为 ValueError
- body.error.message 包含具体字段
- render_dify_user_response 返回 response_type error
- 用户可见回复保留安全边界说明

## 4. 安全边界

P4-D4 不接真实交易所 API。
P4-D4 不保存真实 API key。
P4-D4 不读取钱包私钥。
P4-D4 不真实下单。
P4-D4 不让 Dify 成为底层交易内核。
P4-D4 不把 pipeline 成功伪装成真实交易成功。

## 5. 验收标准

P4-D4 完成需要满足：

- 新增 docs/27_p4_schema_aware_dify_adapter_response_tests.md
- 新增 tests/test_schema_aware_dify_adapter_response.py
- 覆盖 success schema normalization
- 覆盖 missing required field
- 覆盖 bad market_type
- 覆盖 bad spread
- 覆盖 bad asset_class
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 通过

