# P6-D11 - Phase 6 Policy / Risk Deny Acceptance

## 1. 目的

P6-D11 用于验收 Phase 6 policy / risk deny hardening 成果。

Phase 6 的核心目标是：

- paper execution 不能绕过 policy gate
- paper execution 不能绕过 risk guardian
- Dify 不能绕过 policy / risk
- PolicyDeny 不进入 sandbox execution
- RiskDeny 不进入 sandbox execution
- PolicyDeny / RiskDeny 都不是交易所真实拒单
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。

## 3. Phase 6 已完成范围

Phase 6 当前已完成：

- P6-D1：Policy and risk deny case hardening plan
- P6-D2：paper execution policy gate module
- P6-D3：integrate paper execution policy gate into paper execution API
- P6-D4：paper execution policy deny response templates
- P6-D5：Dify paper execution response smoke includes policy deny
- P6-D6：paper execution risk guardian module plan
- P6-D7：paper execution risk guardian module
- P6-D8：integrate risk guardian into paper execution API
- P6-D9：paper execution risk deny response templates
- P6-D10：Dify paper execution response smoke includes risk deny
- P6-D11：Phase 6 policy / risk deny acceptance

## 4. Policy Gate 验收

当前 policy gate：

- fcf/policy/paper_execution_policy.py

当前函数：

- describe_paper_execution_policy
- evaluate_paper_execution_policy

当前拒绝字段：

- real_execution_requested
- real_order
- real_exchange_api
- save_api_key_requested
- read_private_key_requested
- bypass_risk_requested
- force_execute_requested
- convert_paper_to_real_requested
- place_real_order_requested
- connect_exchange_requested

当前检查位置：

- request 顶层字段
- request.metadata
- raw_order 字段
- raw_order.metadata

当前稳定 decision dict：

- ok
- gate
- gate_version
- decision
- error
- data

PolicyDeny 时：

- ok = false
- decision = denied
- error.type = PolicyDeny
- 不进入 sandbox execution engine
- 不真实下单

## 5. Policy Gate API Integration 验收

当前 paper execution API：

- fcf/api/paper_execution_api.py

当前 handle_paper_execution 执行顺序：

1. evaluate_paper_execution_policy
2. evaluate_paper_execution_risk
3. execute_sandbox_order_with_eventstore

PolicyDeny 时：

- 直接返回 ok=false
- data=null
- error.type=PolicyDeny
- 不进入 risk guardian
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 不真实下单

Dify adapter：

- fcf/api/dify_paper_execution_adapter.py

当前会把 body 作为 policy_context 传入 paper_execution_api。

## 6. PolicyDeny Response Template 验收

当前 user-facing template：

- fcf/api/paper_execution_response_templates.py

当前新增：

- render_paper_policy_deny_response

当前 response_type：

- paper_policy_deny

PolicyDeny 用户可见文案必须说明：

- policy gate 拒绝了请求
- 这不是交易所真实拒单
- 这不是真实下单失败
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化

## 7. Risk Guardian 验收

当前 risk guardian：

- fcf/risk/paper_execution_risk_guardian.py

当前函数：

- describe_paper_execution_risk_guardian
- evaluate_paper_execution_risk

当前 RiskDeny 覆盖：

- non-dict request
- missing raw_order
- missing risk_context
- quantity > max_quantity
- notional > max_notional
- duplicate order key
- blocked symbol
- blocked asset_class
- leverage request
- margin request
- high risk flags

当前稳定 decision dict：

- ok
- guardian
- guardian_version
- decision
- error
- data

RiskDeny 时：

- ok = false
- decision = denied
- error.type = RiskDeny
- 不进入 sandbox execution engine
- 不真实下单

## 8. Risk Guardian API Integration 验收

当前 handle_paper_execution 已接入：

- evaluate_paper_execution_policy
- evaluate_paper_execution_risk
- execute_sandbox_order_with_eventstore

RiskDeny 时：

- 直接返回 ok=false
- data=null
- error.type=RiskDeny
- 不进入 sandbox execution engine
- 不生成 sandbox execution event
- 不真实下单

Dify adapter：

- 会传入 body.risk_context
- risk deny 返回 HTTP-style 422
- safe risk_context 仍可正常进入 sandbox execution

## 9. RiskDeny Response Template 验收

当前新增：

- render_paper_risk_deny_response

当前 response_type：

- paper_risk_deny

RiskDeny 用户可见文案必须说明：

- risk guardian 拒绝了 paper / sandbox execution
- 这不是交易所真实拒单
- 这不是真实下单失败
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化

## 10. Dify Response Smoke 验收

当前 smoke runner：

- scripts/run_dify_paper_execution_response_smoke.py

当前覆盖 6 个分支：

- fill_to_user_paper_fill_success
- reject_to_user_paper_reject_success
- policy_deny_to_user_paper_policy_deny
- risk_deny_to_user_paper_risk_deny
- bad_order_to_user_paper_execution_error
- real_execution_intent_to_safety_refusal

当前明确区分：

- paper_fill_success：sandbox fill，不是真实成交
- paper_reject_success：sandbox reject，不是交易所真实拒单
- paper_policy_deny：policy gate 拒绝，不是交易所真实拒单
- paper_risk_deny：risk guardian 拒绝，不是交易所真实拒单
- paper_execution_error：输入校验失败或普通执行错误，不是实盘下单失败
- paper_safety_refusal：Dify / UI 层直接拒绝危险 intent

## 11. 当前关键文件

Policy：

- fcf/policy/paper_execution_policy.py
- tests/test_paper_execution_policy.py
- tests/test_paper_execution_api_policy_integration.py

Risk：

- fcf/risk/paper_execution_risk_guardian.py
- tests/test_paper_execution_risk_guardian.py
- tests/test_paper_execution_api_risk_integration.py

Response templates：

- fcf/api/paper_execution_response_templates.py
- tests/test_paper_execution_policy_deny_response_templates.py
- tests/test_paper_execution_risk_deny_response_templates.py

Smoke：

- scripts/run_dify_paper_execution_response_smoke.py
- tests/test_dify_paper_execution_response_smoke.py

## 12. 当前验证命令

当前验收命令：

python main.py

python scripts/run_dify_http_adapter_smoke.py

python scripts/run_dify_integration_smoke.py

python scripts/run_multi_asset_dify_smoke.py

python scripts/run_multi_asset_error_dify_smoke.py

python scripts/run_dify_paper_execution_smoke.py

python scripts/run_dify_paper_execution_response_smoke.py

python -m pytest -q

当前预期：

- events_recorded: 8
- status completed
- 235 passed

## 13. 安全边界验收

Phase 6 当前明确保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不展示真实收益
- 不允许 Dify 绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交
- 不把 sandbox reject 伪装成交易所真实拒单
- 不把 PolicyDeny 伪装成交易所真实拒单
- 不把 RiskDeny 伪装成交易所真实拒单

## 14. P6-D11 验收结论

P6-D11 完成后，Phase 6 policy / risk deny hardening 达到阶段验收点。

当前系统已经具备：

- paper execution policy gate
- policy gate API integration
- paper_policy_deny user-facing response
- policy deny smoke coverage
- paper execution risk guardian
- risk guardian API integration
- paper_risk_deny user-facing response
- risk deny smoke coverage
- Dify response smoke 全分支覆盖

当前仍然只支持 paper / sandbox。
当前不接真实交易所。
当前不真实下单。

