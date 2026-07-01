# P7-D4 - Dify Response Integration for Guarded Paper Fixture Smoke

## 1. 目的

P7-D4 新增 guarded paper execution Dify response smoke。

该 smoke 读取：

- fixtures/paper_orders_multi_asset_guarded.json

并通过 Dify paper execution adapter 调用：

- route_dify_paper_execution_request
- ROUTE_EXECUTE

随后使用用户可见响应模板：

- render_paper_execution_user_response

把 guarded paper execution 的结果转成用户可见响应。

## 2. 覆盖范围

P7-D4 覆盖资产类别：

- crypto
- equities
- fx
- commodities

覆盖分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

## 3. 预期用户响应类型

fill_success：

- paper_fill_success

sandbox_reject：

- paper_reject_success

policy_deny：

- paper_policy_deny

risk_deny：

- paper_risk_deny

## 4. 安全边界

P7-D4 不接真实交易所 API。
P7-D4 不保存真实 API key。
P7-D4 不读取钱包私钥。
P7-D4 不真实下单。
P7-D4 不允许绕过 policy / risk。
P7-D4 不把 paper execution 伪装成 real execution。

sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
policy deny 不是交易所真实拒单。
risk deny 不是交易所真实拒单。

## 5. 验收标准

P7-D4 完成需要满足：

- 新增 scripts/run_multi_asset_guarded_paper_execution_response_smoke.py
- 新增 tests/test_multi_asset_guarded_paper_execution_response_smoke.py
- runner 输出 status completed
- runner 覆盖 16 个 fixture case
- runner 覆盖 4 个资产类别
- runner 覆盖 4 个分支
- fill_success 转成 paper_fill_success
- sandbox_reject 转成 paper_reject_success
- policy_deny 转成 paper_policy_deny
- risk_deny 转成 paper_risk_deny
- 所有用户响应都包含没有真实下单的安全说明
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 输出 status completed
- python -m pytest -q 通过

