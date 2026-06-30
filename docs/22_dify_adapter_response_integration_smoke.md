# P3-D12 - Dify Adapter Response Integration Smoke

## 1. 目的

P3-D12 把 Dify local HTTP adapter 和 Dify user-facing response templates 接起来。

目标是形成一条本地端到端样例链路：

Dify style request
-> route_dify_http_request
-> local_market_input_api
-> market_input_pipeline
-> stable http-style response
-> render_dify_user_response
-> stable user-facing response

## 2. 当前边界

P3-D12 不启动真实 HTTP server。
P3-D12 不接真实 Dify。
P3-D12 不接真实交易所 API。
P3-D12 不保存真实 API key。
P3-D12 不读取钱包私钥。
P3-D12 不真实下单。

## 3. 覆盖场景

Integration smoke 覆盖：

- single_success_to_user_success
- single_bad_input_to_user_error
- forbidden_intent_to_safety_refusal

## 4. 稳定输出

Integration smoke 输出稳定 dict：

- status
- runner
- case_count
- cases
- safe_boundary

每个 case 包含：

- name
- adapter_http_status
- adapter_ok
- user_response_type
- user_title

## 5. 验收标准

P3-D12 完成需要满足：

- 新增 docs/22_dify_adapter_response_integration_smoke.md
- 新增 scripts/run_dify_integration_smoke.py
- 新增 tests/test_dify_integration_smoke.py
- integration smoke 可本地运行
- success adapter response 能转成 user success response
- error adapter response 能转成 user error response
- forbidden intent 能转成 safety refusal response
- python main.py 仍输出 events_recorded: 8
- python -m pytest -q 通过

