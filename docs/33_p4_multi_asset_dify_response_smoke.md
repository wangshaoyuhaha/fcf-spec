# P4-D10 - Multi-asset Fixture Dify Response Smoke

## 1. 目的

P4-D10 增加 multi-asset fixture Dify response smoke。

目标是把 P4-D9 的多资产 fixture 接入 Dify batch route，并进一步接入 user-facing response template。

调用链：

fixtures/raw_market_data_multi_asset.json
-> route_dify_http_request POST /api/v1/market-input/batch
-> local_market_input_api
-> market_input_pipeline
-> raw_market_input_schema
-> EventStore / ReplayEngine
-> render_dify_user_response
-> stable smoke summary

## 2. 覆盖资产

当前 smoke 覆盖：

- crypto / BTCUSDT
- equities / AAPL
- fx / EURUSD
- commodities / XAUUSD

## 3. 输出目标

Smoke runner 输出稳定 summary：

- status
- runner
- fixture_path
- asset_classes
- symbols
- market_types
- adapter_http_status
- adapter_ok
- event_count
- user_response_type
- user_title
- safe_boundary

## 4. 安全边界

P4-D10 不接真实交易所 API。
P4-D10 不保存真实 API key。
P4-D10 不读取钱包私钥。
P4-D10 不真实下单。
P4-D10 不让 Dify 成为底层交易内核。
P4-D10 不把 pipeline 成功伪装成真实交易成功。

## 5. 验收标准

P4-D10 完成需要满足：

- 新增 docs/33_p4_multi_asset_dify_response_smoke.md
- 新增 scripts/run_multi_asset_dify_smoke.py
- 新增 tests/test_multi_asset_dify_smoke.py
- smoke runner 可直接运行
- smoke runner 输出 status completed
- adapter response 为 200 / ok true
- user response type 为 success
- event_count 为 4
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python -m pytest -q 通过

