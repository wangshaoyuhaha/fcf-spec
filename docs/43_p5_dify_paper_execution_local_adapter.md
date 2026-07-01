# P5-D7 - Dify Paper Execution Local Adapter

## 1. 目的

P5-D7 新增 Dify paper execution local adapter。

该 adapter 提供本地 HTTP-style route function，用于未来 Dify HTTP/API Node 调用 paper execution API wrapper。

P5-D7 不启动真实 HTTP server。
P5-D7 不接真实 Dify。
P5-D7 不接真实交易所 API。
P5-D7 不保存真实 API key。
P5-D7 不读取钱包私钥。
P5-D7 不真实下单。

## 2. 当前调用链

Dify style paper execution request
-> route_dify_paper_execution_request
-> fcf.api.paper_execution_api.handle_paper_execution
-> fcf.paper.sandbox_execution_engine.execute_sandbox_order_with_eventstore
-> EventStore
-> ReplayEngine
-> stable http-style response dict

## 3. 当前支持路由

当前支持：

- GET /api/v1/paper-execution/contract
- POST /api/v1/paper-execution/execute

## 4. Contract Route

GET /api/v1/paper-execution/contract 返回：

- adapter 信息
- paper_execution_api contract
- supported routes
- safe boundary

## 5. Execute Route

POST /api/v1/paper-execution/execute 接收：

{
  "raw_order": {},
  "simulation_mode": "simulated_fill",
  "fill_price": "60050.5",
  "filled_quantity": "0.25",
  "reject_reason": null,
  "output_path": null
}

simulation_mode 支持：

- simulated_fill
- simulated_reject

## 6. 成功响应

成功返回：

{
  "http_status": 200,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "ok": true,
    "api": "paper_execution_api",
    "api_version": "0.1.0",
    "error": null,
    "data": {}
  }
}

## 7. 错误响应

adapter 层错误：

- unknown route -> 404
- method not allowed -> 405
- missing body -> 400
- missing raw_order -> 400

paper_execution_api 错误：

- bad order -> 422
- bad simulation_mode -> 422
- bad fill_price -> 422
- overfill -> 422

## 8. 安全边界

P5-D7 必须保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不调用真实执行器
- 不把 paper execution 伪装成 real execution
- 只调用 paper_execution_api

## 9. 验收标准

P5-D7 完成需要满足：

- 新增 docs/43_p5_dify_paper_execution_local_adapter.md
- 新增 fcf/api/dify_paper_execution_adapter.py
- 新增 tests/test_dify_paper_execution_adapter.py
- contract route 返回 200
- execute simulated_fill 返回 200
- execute simulated_reject 返回 200
- bad order 返回 422
- bad simulation_mode 返回 422
- unknown route 返回 404
- wrong method 返回 405
- missing raw_order 返回 400
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

