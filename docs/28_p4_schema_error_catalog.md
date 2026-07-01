# P4-D5 - Schema Error Catalog and Stable Error Messages

## 1. 目的

P4-D5 定义 raw market input schema 的稳定错误目录和错误消息格式。

目标是让 Dify、API wrapper、pipeline、测试都能依赖稳定的 schema error type 和 message。

P4-D5 不接真实交易所 API。
P4-D5 不保存真实 API key。
P4-D5 不读取钱包私钥。
P4-D5 不真实下单。

## 2. 当前错误目录

当前 schema error catalog 包含：

- MissingField
- InvalidEnumValue
- InvalidNumber
- InvalidPositiveNumber
- InvalidNonNegativeNumber
- InvalidSpread
- InvalidPayloadType

## 3. 稳定错误消息规则

MissingField:

missing required fields: field_a, field_b

InvalidEnumValue:

field_name is not supported: value

InvalidNumber:

field_name must be a valid number

InvalidPositiveNumber:

field_name must be greater than 0

InvalidNonNegativeNumber:

field_name must be greater than or equal to 0

InvalidSpread:

best_bid must be less than or equal to best_ask

InvalidPayloadType:

raw market input must be a dict

## 4. Dify 使用方式

Dify 不直接解释 Python 异常栈。
Dify 只读取 wrapper 返回的稳定 response dict：

- ok
- api
- api_version
- error.type
- error.message
- data

Dify 收到 ok=false 时必须进入 error branch。

## 5. 安全边界

P4-D5 继续保持：

- Dify 不作为底层交易内核
- Dify 不直接接真实交易所 API
- Dify 不保存真实 API key
- Dify 不读取钱包私钥
- Dify 不真实下单
- Dify 不把 pipeline 成功伪装成真实交易成功

## 6. 验收标准

P4-D5 完成需要满足：

- 新增 docs/28_p4_schema_error_catalog.md
- 新增 fcf/schemas/schema_error_catalog.py
- 新增 tests/test_schema_error_catalog.py
- error catalog 可描述
- error message builder 稳定
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 通过

