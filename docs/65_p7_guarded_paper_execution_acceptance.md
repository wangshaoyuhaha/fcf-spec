# P7-D5 - Guarded Paper Execution Phase Acceptance

## 1. 目的

P7-D5 是 Phase 7 guarded paper execution 的阶段验收文档。

本验收汇总 P7-D1 到 P7-D4：

- P7-D1：multi-asset guarded paper fixture plan
- P7-D2：multi-asset guarded paper execution fixture
- P7-D3：multi-asset guarded paper execution smoke runner
- P7-D4：Dify response integration for guarded paper fixture smoke

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

当前不是足球系统。
当前不是 BTC-only。

BTC / crypto 只是资产类别之一。
当前系统已覆盖：

- crypto
- equities
- fx
- commodities

## 3. 当前 guarded paper execution 分支

当前 guarded paper execution 覆盖四类分支：

### 3.1 fill_success

含义：

- policy gate 通过
- risk guardian 通过
- sandbox execution engine 返回 filled
- 生成 sandbox execution event
- 用户响应类型为 paper_fill_success

边界：

- sandbox fill 不是真实成交
- 不接真实交易所 API
- 不真实下单

### 3.2 sandbox_reject

含义：

- policy gate 通过
- risk guardian 通过
- sandbox execution engine 返回 rejected
- 生成 sandbox execution rejected event
- 用户响应类型为 paper_reject_success

边界：

- sandbox reject 不是交易所真实拒单
- 不接真实交易所 API
- 不真实下单

### 3.3 policy_deny

含义：

- policy gate 拒绝
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 用户响应类型为 paper_policy_deny

边界：

- PolicyDeny 不是交易所真实拒单
- PolicyDeny 不是真实下单失败
- PolicyDeny 是 FCF 本地 policy gate 的安全拒绝

### 3.4 risk_deny

含义：

- policy gate 通过
- risk guardian 拒绝
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 用户响应类型为 paper_risk_deny

边界：

- RiskDeny 不是交易所真实拒单
- RiskDeny 不是真实下单失败
- RiskDeny 是 FCF 本地 risk guardian 的安全拒绝

## 4. 当前 fixture 覆盖

当前 fixture 文件：

- fixtures/paper_orders_multi_asset_guarded.json

覆盖资产类别：

- crypto
- equities
- fx
- commodities

每个资产类别覆盖：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

总 case 数：

- 16

## 5. 当前 smoke runner 覆盖

### 5.1 Guarded paper execution smoke

脚本：

- scripts/run_multi_asset_guarded_paper_execution_smoke.py

验证：

- 读取 guarded fixture
- 调用 handle_paper_execution
- 覆盖 16 个 case
- 输出 status completed
- 验证 expected 与 actual 一致
- 验证 policy_deny / risk_deny 不写 sandbox event
- 验证 paper-only 安全边界

### 5.2 Guarded paper execution response smoke

脚本：

- scripts/run_multi_asset_guarded_paper_execution_response_smoke.py

验证：

- 读取 guarded fixture
- 调用 route_dify_paper_execution_request
- 调用 render_paper_execution_user_response
- fill_success 转成 paper_fill_success
- sandbox_reject 转成 paper_reject_success
- policy_deny 转成 paper_policy_deny
- risk_deny 转成 paper_risk_deny
- 验证用户响应不声称真实成交
- 验证用户响应保留 paper-only 安全边界

## 6. 当前 paper execution API 顺序

当前 paper execution API 顺序固定为：

1. evaluate_paper_execution_policy
2. evaluate_paper_execution_risk
3. execute_sandbox_order_with_eventstore

含义：

- policy 在 risk 之前执行
- risk 在 sandbox execution 之前执行
- policy deny 直接返回 ok=false
- risk deny 直接返回 ok=false
- policy deny 不进入 sandbox execution
- risk deny 不进入 sandbox execution
- policy deny / risk deny 都不生成 sandbox execution event

## 7. 当前安全边界

Phase 7 当前继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不允许绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- Dify 不作为底层交易内核
- Dify 只调用受控 API wrapper / pipeline

关键说明：

- sandbox fill 不是真实成交
- sandbox reject 不是交易所真实拒单
- PolicyDeny 不是交易所真实拒单
- RiskDeny 不是交易所真实拒单

## 8. 当前验证命令

P7-D5 当前验收命令：

python main.py

python scripts/run_dify_http_adapter_smoke.py

python scripts/run_dify_integration_smoke.py

python scripts/run_multi_asset_dify_smoke.py

python scripts/run_multi_asset_error_dify_smoke.py

python scripts/run_dify_paper_execution_smoke.py

python scripts/run_dify_paper_execution_response_smoke.py

python scripts/run_multi_asset_guarded_paper_execution_smoke.py

python scripts/run_multi_asset_guarded_paper_execution_response_smoke.py

python -m pytest -q

## 9. P7-D5 验收结论

P7-D5 完成后，Phase 7 guarded paper execution 的第一轮验收通过。

当前系统已经具备：

- 多资产 guarded paper fixture
- 多资产 guarded paper execution smoke
- 多资产 guarded paper Dify response smoke
- policy deny / risk deny 阻断执行
- sandbox fill / reject paper-only 响应
- 用户响应安全边界校验

当前仍然不具备、也不应该声称具备：

- 真实交易所连接
- 真实下单
- 真实成交
- 真实交易所拒单
- 真实资金影响

## 10. 下一步建议

进入 P7-D6：guarded paper execution acceptance smoke runner。

建议目标：

- 新增 scripts/run_p7_guarded_paper_execution_acceptance_smoke.py
- 汇总 P7-D2 / P7-D3 / P7-D4 的验收结果
- 输出 status completed
- 输出 acceptance_summary
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

