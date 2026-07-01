# P4-D3 - Schema Integration Into Market Input Pipeline

## 1. 目的

P4-D3 将 P4-D2 新增的 raw market input schema module 接入 market input pipeline。

目标是让 process_raw_market_input 和 process_raw_market_batch 在进入事件构建前先完成：

- 必填字段检查
- asset_class normalization
- symbol normalization
- venue normalization
- market_type normalization
- number conversion
- last_price 正数校验
- volume / depth 非负校验
- best_bid <= best_ask 校验

## 2. 接入位置

接入文件：

- fcf/pipelines/market_input_pipeline.py

接入 schema：

- fcf/schemas/raw_market_input_schema.py
- normalize_raw_market_input
- SCHEMA_NAME
- SCHEMA_VERSION

## 3. 设计原则

schema 在 pipeline 边界执行。

Dify、adapter、API wrapper 可以做预检查，但最终进入 pipeline 前仍由 FCF schema 层做硬校验。

## 4. 稳定返回

process_raw_market_input 继续返回 summary dict。

成功返回包含：

- status
- pipeline
- correlation_id
- schema
- schema_version
- asset_class
- symbol
- venue
- market_type
- event_count
- persisted
- output_path
- replay

batch 成功返回包含：

- status
- pipeline
- correlation_id
- schema
- schema_version
- event_count
- symbols
- asset_classes
- market_types
- persisted
- output_path
- replay

## 5. 安全边界

P4-D3 不接真实交易所 API。
P4-D3 不保存真实 API key。
P4-D3 不读取钱包私钥。
P4-D3 不真实下单。
P4-D3 不绕过 EventStore。
P4-D3 不绕过 ReplayEngine。

## 6. 验收标准

P4-D3 完成需要满足：

- market_input_pipeline 调用 normalize_raw_market_input
- single input 可被 schema 归一化
- batch input 可被 schema 归一化
- schema 错误可被 pipeline 抛出 ValueError
- local_market_input_api 继续包装错误为稳定 response dict
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 通过

