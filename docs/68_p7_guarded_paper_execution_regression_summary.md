# P7-D8 - Post-closeout Guarded Paper Execution Regression Summary

## 1. 目的

P7-D8 新增 post-closeout guarded paper execution regression summary。

该步骤用于在 P7-D7 closeout 后，把当前所有 smoke runner 的输出集中汇总，形成 Phase 7 第一轮后的回归摘要。

P7-D8 不改变交易逻辑。
P7-D8 不改变 policy / risk / sandbox execution 顺序。
P7-D8 不接真实交易所 API。
P7-D8 不真实下单。

## 2. 新增文件

- docs/68_p7_guarded_paper_execution_regression_summary.md
- scripts/run_p7_guarded_paper_execution_regression_summary.py
- tests/test_p7_guarded_paper_execution_regression_summary.py

## 3. regression summary 覆盖的 smoke runner

P7-D8 汇总以下 smoke runner：

- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py
- scripts/run_multi_asset_dify_smoke.py
- scripts/run_multi_asset_error_dify_smoke.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py
- scripts/run_multi_asset_guarded_paper_execution_smoke.py
- scripts/run_multi_asset_guarded_paper_execution_response_smoke.py
- scripts/run_p7_guarded_paper_execution_acceptance_smoke.py

## 4. regression summary 输出

runner 输出：

- status
- runner
- smoke_count
- completed_count
- failed_count
- smoke_results
- guarded_summary
- regression_summary
- safe_boundary

## 5. 当前 guarded paper execution 覆盖

资产类别：

- crypto
- equities
- fx
- commodities

分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

用户响应：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny

## 6. 安全边界

P7-D8 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不允许绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- sandbox fill 不是真实成交
- sandbox reject 不是交易所真实拒单
- PolicyDeny 不是交易所真实拒单
- RiskDeny 不是交易所真实拒单

## 7. 验收标准

P7-D8 完成需要满足：

- 新增 regression summary runner
- runner 输出 status completed
- smoke_count 为 9
- completed_count 为 9
- failed_count 为 0
- guarded summary 覆盖 16 个 case
- guarded summary 覆盖 4 个资产类别
- guarded summary 覆盖 4 个分支
- guarded response summary 覆盖 4 个用户响应类型
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 输出 status completed
- python -m pytest -q 通过

## 8. 下一步建议

进入 P7-D9：Phase 7 to Phase 8 bridge plan。

建议目标：

- 新增 Phase 8 规划文档
- 明确下一阶段是否做 portfolio-level guarded paper execution
- 明确是否引入 cross-asset exposure checks
- 明确是否引入 regression CI entrypoint
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

