# P5-D8 - Dify Paper Execution Smoke Runner

## 1. 目的

P5-D8 新增 Dify paper execution smoke runner。

该 smoke runner 只做本地模拟调用：

- 不启动真实 HTTP server
- 不接真实 Dify
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单

## 2. 当前调用链

scripts/run_dify_paper_execution_smoke.py
-> fcf.api.dify_paper_execution_adapter.route_dify_paper_execution_request
-> fcf.api.paper_execution_api.handle_paper_execution
-> fcf.paper.sandbox_execution_engine.execute_sandbox_order_with_eventstore
-> EventStore
-> ReplayEngine
-> stable summary

## 3. 覆盖场景

P5-D8 smoke runner 覆盖：

- contract
- simulated_fill
- simulated_reject
- bad_order_error
- bad_simulation_mode_error
- missing_raw_order_error

## 4. 输出格式

Smoke runner 输出稳定 dict：

{
  "status": "completed",
  "runner": "dify_paper_execution_smoke",
  "case_count": 6,
  "cases": [],
  "safe_boundary": {}
}

每个 case 包含：

- name
- http_status
- ok
- api
- error_type
- execution_status
- event_name
- user_visible_safety

## 5. 安全边界

P5-D8 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交

## 6. 验收标准

P5-D8 完成需要满足：

- 新增 docs/44_p5_dify_paper_execution_smoke_runner.md
- 新增 scripts/run_dify_paper_execution_smoke.py
- 新增 tests/test_dify_paper_execution_smoke.py
- smoke runner 可直接运行
- contract 返回 200
- simulated_fill 返回 200
- simulated_reject 返回 200
- bad_order_error 返回 422
- bad_simulation_mode_error 返回 422
- missing_raw_order_error 返回 400
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

