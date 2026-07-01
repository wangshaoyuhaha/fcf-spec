# P4-D6 - Integrate Schema Error Catalog Into Raw Market Input Schema

## 1. 目的

P4-D6 将 P4-D5 新增的 schema_error_catalog 接入 raw_market_input_schema。

目标：

- raw_market_input_schema 使用稳定 message builder
- 保持现有错误 message 兼容
- 保持 Dify adapter 422 行为
- 保持 response templates error 行为
- 不破坏现有测试

## 2. 接入范围

修改文件：

- fcf/schemas/raw_market_input_schema.py

使用文件：

- fcf/schemas/schema_error_catalog.py

新增测试：

- tests/test_raw_market_input_schema_error_catalog_integration.py

## 3. 兼容要求

现有测试依赖的错误消息不能被破坏：

- missing required fields
- asset_class is not supported
- market_type is not supported
- last_price must be a valid number
- last_price must be greater than 0
- volume must be greater than or equal to 0
- best_bid must be less than or equal to best_ask
- raw market input must be a dict

## 4. 安全边界

P4-D6 不接真实交易所 API。
P4-D6 不保存真实 API key。
P4-D6 不读取钱包私钥。
P4-D6 不真实下单。
P4-D6 不改变 Dify 的安全边界。

## 5. 验收标准

P4-D6 完成需要满足：

- raw_market_input_schema 使用 schema_error_catalog message builder
- 新增 integration tests
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 通过

