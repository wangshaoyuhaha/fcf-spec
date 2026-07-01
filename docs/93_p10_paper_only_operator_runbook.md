# P10-D4 - Paper-only Operator Runbook

P10-D4 新增 paper-only operator runbook。

新增文件：

- docs/93_p10_paper_only_operator_runbook.md
- tests/test_p10_paper_only_operator_runbook.py

## 1. 目的

该 runbook 给 operator 使用，只用于 non-production / paper-only 复核。

该 runbook 不用于真实交易。
该 runbook 不用于实盘下单。
该 runbook 不用于读取真实账户余额。
该 runbook 不用于读取真实仓位。
该 runbook 不用于绕过人工复核。
该 runbook 不用于绕过 policy / risk / safe_boundary。

## 2. 本地完整回归命令

operator 本地推荐运行：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_acceptance_smoke.py
- python scripts/run_p9_global_regression_summary.py
- python -m pytest -q

## 3. Dify-safe adapter 复核入口

当前 Dify-safe adapter：

- fcf/api/dify_global_regression_api.py
- handle_dify_global_regression_request

operator review response template：

- fcf/api/operator_review_response_templates.py
- render_operator_review_response

## 4. status 读取规则

如果看到：

- status completed
- ok true
- ready_for_operator_review true
- ready_for_phase10_planning true
- safe_boundary ok true

只能说明：

- paper-only regression 通过
- non-production 检查通过
- 可以进入人工复核

不能说明：

- 真实交易信号成立
- 真实下单成功
- 真实成交成功
- 真实资金发生变化

## 5. safe_boundary 读取规则

operator 必须确认：

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

## 6. failed 处理规则

如果任何命令出现 failed：

- 停止继续操作
- 不要进入下一阶段
- 不要把结果解释为交易信号
- 不要连接真实交易所
- 不要配置 API key
- 不要读取钱包私钥
- 不要尝试真实下单
- 记录失败命令
- 记录错误输出
- 回到 failure triage guide

## 7. operator review required 处理规则

如果 response_type 是 operator_review_required：

- 必须人工复核
- 不允许自动通过
- 不允许自动实盘交易
- 不允许绕过 safe_boundary
- 不允许绕过 policy / risk

## 8. 明确禁止事项

P10-D4 不接真实交易所 API。
P10-D4 不保存真实 API key。
P10-D4 不读取钱包私钥。
P10-D4 不真实下单。
P10-D4 不读取真实账户余额。
P10-D4 不读取真实仓位。
P10-D4 不声明真实成交。
P10-D4 不声明真实资金影响。
P10-D4 不配置 CI secret。
P10-D4 不做 production deployment。
P10-D4 不自动实盘交易。
P10-D4 不自动绕过人工复核。
P10-D4 不绕过 policy / risk / safe_boundary。

## 9. P10-D4 验收标准

P10-D4 完成需要满足：

- 新增 docs/93_p10_paper_only_operator_runbook.md
- 新增 tests/test_p10_paper_only_operator_runbook.py
- runbook 明确本地完整回归命令
- runbook 明确 Dify-safe adapter 入口
- runbook 明确 operator review response template
- runbook 明确 status 读取规则
- runbook 明确 safe_boundary 读取规则
- runbook 明确 failed 处理规则
- runbook 明确 operator_review_required 处理规则
- python main.py 输出 events_recorded: 8
- python scripts/run_p9_global_regression_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P10-D5：failure triage guide。
