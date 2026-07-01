# P10-D6 - Dify Workflow Node Contract Document

P10-D6 新增 Dify workflow node contract document。

新增文件：

- docs/95_p10_dify_workflow_node_contract.md
- tests/test_p10_dify_workflow_node_contract.py

## 1. 目的

该文档定义 Dify workflow 中如何安全调用 FCF paper-only regression / operator review 能力。

该 workflow 只允许用于：

- paper-only
- non-production
- operator review
- safe boundary review

该 workflow 不允许用于：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. 当前可调用入口

Dify-safe API wrapper：

- fcf/api/dify_global_regression_api.py
- handle_dify_global_regression_request

Operator response template：

- fcf/api/operator_review_response_templates.py
- render_operator_review_response

当前可运行命令：

- python scripts/run_all_smokes.py
- python scripts/run_p9_acceptance_smoke.py
- python scripts/run_p9_global_regression_summary.py
- python -m pytest -q

## 3. Workflow 节点总览

建议 Dify workflow 包含 6 个节点：

- Input validation node
- Global regression API node
- Safe boundary review node
- Operator response template node
- Human review node
- Final non-production output node

## 4. Input validation node

输入字段：

- request_id
- operator_id
- review_mode
- requested_checks
- output_format

允许 review_mode：

- paper_only
- operator_review
- non_production_review

允许 requested_checks：

- all_smokes
- global_report
- safe_boundary
- project_state_consistency

允许 output_format：

- json

Input validation node 必须拒绝：

- review_mode=live_trading
- requested_checks=real_exchange_balance
- output_format=html
- exchange_api_key
- wallet_private_key
- real_account_credentials
- real_broker_credentials
- live_order_request
- bypass_operator_review=true
- bypass_policy_risk_safe_boundary=true

## 5. Global regression API node

该节点调用：

- handle_dify_global_regression_request

该节点输出：

- ok
- api
- api_version
- error
- data

data 内必须包含：

- run_all_smokes
- global_regression_report
- global_safe_boundary_check
- project_state_consistency_check
- operator_review_required
- ready_for_operator_review
- safe_boundary

Global regression API node 只允许调用 paper-only regression runner。

Global regression API node 不允许：

- 连接真实交易所
- 读取真实账户余额
- 读取真实仓位
- 创建真实订单
- 保存真实 API key
- 读取钱包私钥

## 6. Safe boundary review node

该节点必须检查：

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

如果 Safe boundary review node failed：

- 必须停止 workflow
- 不允许进入 Human review passed
- 不允许进入 Final non-production output node
- 不允许自动修正为 passed
- 不允许绕过 policy / risk / safe_boundary

## 7. Operator response template node

该节点调用：

- render_operator_review_response

允许 response_type：

- global_regression_passed
- global_regression_failed
- safe_boundary_failed
- project_state_inconsistent
- operator_review_required

所有 response_type 都必须明确：

- paper-only / non-production
- 不是真实交易信号
- 不是真实下单结果
- 不是真实成交结果
- 没有真实资金影响
- 需要人工复核

## 8. Human review node

Human review node 必须由 operator 人工确认。

Human review node 不允许：

- 自动通过
- 自动实盘交易
- 绕过 safe_boundary
- 绕过 policy / risk
- 把 paper-only passed 解释成真实交易信号
- 把 paper-only passed 解释成真实成交

Human review node 只能确认：

- regression 是否 completed
- safe_boundary 是否 ok
- project state 是否一致
- response template 是否明确 non-production
- 是否可以继续进入下一步文档流程

## 9. Final non-production output node

Final non-production output node 只能输出：

- paper-only regression status
- operator review required
- safe_boundary summary
- non-production notice
- next documentation step

Final non-production output node 不允许输出：

- 真实交易建议
- 真实下单指令
- 真实成交确认
- 真实资金变化
- 真实账户余额
- 真实仓位
- 交易所真实拒单

## 10. 明确禁止事项

P10-D6 不接真实交易所 API。
P10-D6 不保存真实 API key。
P10-D6 不读取钱包私钥。
P10-D6 不真实下单。
P10-D6 不读取真实账户余额。
P10-D6 不读取真实仓位。
P10-D6 不声明真实成交。
P10-D6 不声明真实资金影响。
P10-D6 不配置 CI secret。
P10-D6 不做 production deployment。
P10-D6 不自动实盘交易。
P10-D6 不自动绕过人工复核。
P10-D6 不绕过 policy / risk / safe_boundary。

## 11. P10-D6 验收标准

P10-D6 完成需要满足：

- 新增 docs/95_p10_dify_workflow_node_contract.md
- 新增 tests/test_p10_dify_workflow_node_contract.py
- 文档包含 Input validation node
- 文档包含 Global regression API node
- 文档包含 Safe boundary review node
- 文档包含 Operator response template node
- 文档包含 Human review node
- 文档包含 Final non-production output node
- 文档明确 Dify-safe API wrapper
- 文档明确 operator response template
- 文档明确禁止真实交易所 API
- 文档明确禁止真实下单
- 文档明确禁止绕过人工复核
- 文档明确禁止绕过 policy / risk / safe_boundary
- python main.py 输出 events_recorded: 8
- python scripts/run_p9_global_regression_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P10-D7：Phase 10 acceptance smoke。
