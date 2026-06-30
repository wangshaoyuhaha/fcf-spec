# P3-D10 - Dify HTTP Adapter Smoke Runner

## 1. 目的

P3-D10 增加一个本地 smoke runner，用来模拟 Dify HTTP/API Node 调用 FCF local HTTP adapter。

该 smoke runner 只做本地样例请求。
该 smoke runner 不启动真实 HTTP server。
该 smoke runner 不接真实 Dify。
该 smoke runner 不接真实交易所 API。
该 smoke runner 不保存真实 API key。
该 smoke runner 不真实下单。

## 2. 当前调用链

Dify style example payload
-> scripts/run_dify_http_adapter_smoke.py
-> fcf.api.dify_http_adapter.route_dify_http_request
-> fcf.api.local_market_input_api
-> fcf.pipelines.market_input_pipeline
-> EventStore / ReplayEngine
-> stable response dict

## 3. 覆盖范围

Smoke runner 覆盖：

- GET /api/v1/contract
- POST /api/v1/market-input/single
- POST /api/v1/market-input/batch
- bad input
- unknown route

## 4. 安全边界

P3-D10 继续保持：

- 不接真实交易所 API
- 不保存真实交易所 API key
- 不读取钱包私钥
- 不真实下单
- 不绕过 FCF API wrapper
- 不绕过 EventStore
- 不绕过 ReplayEngine

