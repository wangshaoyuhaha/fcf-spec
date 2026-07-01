# P10-D5 - Failure Triage Guide

P10-D5 新增 failure triage guide。

新增文件：

- docs/94_p10_failure_triage_guide.md
- tests/test_p10_failure_triage_guide.py

## 1. 目的

该 guide 用于 paper-only / non-production 失败排查。

该 guide 不用于真实交易。
该 guide 不用于实盘下单。
该 guide 不用于读取真实账户余额。
该 guide 不用于读取真实仓位。
该 guide 不用于绕过人工复核。
该 guide 不用于绕过 policy / risk / safe_boundary。

## 2. 总原则

任何 failed 都必须：

- 停止继续操作
- 不要进入下一阶段
- 不要把结果解释为交易信号
- 不要连接真实交易所
- 不要配置 API key
- 不要读取钱包私钥
- 不要尝试真实下单
- 记录失败命令
- 记录错误输出
- 回到对应排查分支

## 3. pytest failed

如果命令失败：

- python -m pytest -q

处理步骤：

- 保留完整红色报错
- 记录失败 test name
- 记录失败 assertion
- 不要跳过测试
- 不要删除测试绕过失败
- 不要把失败结果解释为交易信号
- 修复后重新运行 python -m pytest -q

## 4. smoke failed

如果以下命令 failed：

- python scripts/run_all_smokes.py
- python scripts/run_p9_acceptance_smoke.py
- python scripts/run_p9_global_regression_summary.py

处理步骤：

- 读取 status
- 读取 failed_count
- 读取 components
- 读取 readiness
- 读取 safe_boundary
- 找到 failed component
- 不进入下一阶段
- 修复后重新运行对应 smoke

## 5. safe_boundary failed

如果 check_global_safe_boundary failed：

- 立即停止
- 不允许进入 operator review passed
- 不允许继续到下一阶段
- 不允许连接真实交易所
- 不允许设置 real_execution=true
- 不允许设置 real_exchange_api=true
- 不允许设置 real_money_impact=true
- 不允许绕过 policy / risk / safe_boundary

必须确认：

- paper_only = true
- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false
- no_real_exchange_api = true
- no_real_order_placement = true
- no_exchange_api_key_storage = true
- no_wallet_private_key_access = true
- no_real_account_balance_read = true
- no_real_position_read = true
- does_not_claim_real_trade_success = true
- ci_secret_required = false
- production_deployment = false
- operator_review_required = true
- auto_live_trading = false
- bypass_operator_review = false
- bypass_policy_risk_safe_boundary = false

## 6. project state consistency failed

如果 check_project_state_consistency failed：

- 检查 README.md
- 检查 PROJECT_STATE.md
- 检查 phase marker
- 检查 safety marker
- 检查 next marker
- 不要删除历史阶段记录
- 不要删除安全边界记录
- 修复后重新运行 python -m pytest -q

## 7. Dify adapter input invalid

如果 handle_dify_global_regression_request 返回：

- ok false
- error.type = DifyGlobalRegressionSchemaError

处理步骤：

- 检查 review_mode
- 检查 requested_checks
- 检查 output_format
- 不允许 review_mode=live_trading
- 不允许 requested_checks 包含 real_exchange_balance
- 不允许 output_format=html
- 保持 output_format=json
- 保持 review_mode=operator_review 或 paper_only 或 non_production_review

## 8. response template mismatch

如果 render_operator_review_response 输出不符合预期：

- 检查 response_type
- 检查 safety_notice
- 检查 fields.real_execution
- 检查 fields.real_exchange_api
- 检查 fields.operator_review_required
- 检查 fields.bypass_operator_review
- 检查 fields.bypass_policy_risk_safe_boundary

允许 response_type：

- global_regression_passed
- global_regression_failed
- safe_boundary_failed
- project_state_inconsistent
- operator_review_required

## 9. 明确禁止事项

P10-D5 不接真实交易所 API。
P10-D5 不保存真实 API key。
P10-D5 不读取钱包私钥。
P10-D5 不真实下单。
P10-D5 不读取真实账户余额。
P10-D5 不读取真实仓位。
P10-D5 不声明真实成交。
P10-D5 不声明真实资金影响。
P10-D5 不配置 CI secret。
P10-D5 不做 production deployment。
P10-D5 不自动实盘交易。
P10-D5 不自动绕过人工复核。
P10-D5 不绕过 policy / risk / safe_boundary。

## 10. P10-D5 验收标准

P10-D5 完成需要满足：

- 新增 docs/94_p10_failure_triage_guide.md
- 新增 tests/test_p10_failure_triage_guide.py
- guide 覆盖 pytest failed
- guide 覆盖 smoke failed
- guide 覆盖 safe_boundary failed
- guide 覆盖 project state consistency failed
- guide 覆盖 Dify adapter input invalid
- guide 覆盖 response template mismatch
- python main.py 输出 events_recorded: 8
- python scripts/run_p9_global_regression_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P10-D6：Dify workflow node contract document。
