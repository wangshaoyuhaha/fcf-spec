# P5-D10 - Dify Paper Execution Response Integration Smoke

## 1. 目的

P5-D10 新增 Dify paper execution response integration smoke。

目标是把 Dify paper execution adapter 的 http-style response 接入 paper execution user-facing response templates，形成本地端到端样例链路。

调用链：

Dify style paper execution request
-> route_dify_paper_execution_request
-> paper_execution_api
-> sandbox_execution_engine
-> EventStore
-> ReplayEngine
-> paper_execution_response_templates
-> stable user-facing response summary

## 2. 覆盖场景

P5-D10 覆盖：

- fill_to_user_paper_fill_success
- reject_to_user_paper_reject_success
- bad_order_to_user_paper_execution_error
- real_execution_intent_to_safety_refusal

## 3. 输出格式

Smoke runner 输出稳定 dict：

- status
- runner
- case_count
- cases
- safe_boundary

每个 case 包含：

- name
- adapter_http_status
- adapter_ok
- adapter_api
- user_response_type
- user_title
- user_safety_notice_present

## 4. 安全边界

P5-D10 不启动真实 HTTP server。
P5-D10 不接真实 Dify。
P5-D10 不接真实交易所 API。
P5-D10 不保存真实 API key。
P5-D10 不读取钱包私钥。
P5-D10 不真实下单。
P5-D10 不把 paper execution 伪装成 real execution。
P5-D10 不把 sandbox fill 伪装成真实成交。

## 5. 验收标准

P5-D10 完成需要满足：

- 新增 docs/46_p5_dify_paper_execution_response_smoke.md
- 新增 scripts/run_dify_paper_execution_response_smoke.py
- 新增 tests/test_dify_paper_execution_response_smoke.py
- smoke runner 可直接运行
- fill -> paper_fill_success
- reject -> paper_reject_success
- bad order -> paper_execution_error
- real execution intent -> paper_safety_refusal
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

