# P10-D3 - Operator Review Response Templates

P10-D3 新增 operator review response templates。

新增文件：

- docs/92_p10_operator_review_response_templates.md
- fcf/api/operator_review_response_templates.py
- tests/test_p10_operator_review_response_templates.py

新增入口：

- render_operator_review_response

输入：

- handle_dify_global_regression_request 的 response dict

输出稳定 user-facing response dict：

- response_type
- template
- template_version
- title
- message
- fields
- safety_notice

覆盖 response_type：

- global_regression_passed
- global_regression_failed
- safe_boundary_failed
- project_state_inconsistent
- operator_review_required

所有响应必须明确：

- 这是 paper-only / non-production 响应
- 不是真实交易信号
- 不是真实下单结果
- 不是真实成交结果
- 需要人工复核

P10-D3 不接真实交易所 API。
P10-D3 不保存真实 API key。
P10-D3 不读取钱包私钥。
P10-D3 不真实下单。
P10-D3 不读取真实账户余额。
P10-D3 不读取真实仓位。
P10-D3 不声明真实成交。
P10-D3 不声明真实资金影响。
P10-D3 不配置 CI secret。
P10-D3 不做 production deployment。
P10-D3 不自动实盘交易。
P10-D3 不自动绕过人工复核。
P10-D3 不绕过 policy / risk / safe_boundary。

下一步：

P10-D4：paper-only operator runbook。
