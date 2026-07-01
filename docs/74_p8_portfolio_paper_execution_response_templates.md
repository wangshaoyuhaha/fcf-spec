# P8-D5 - Portfolio Paper Execution User-facing Response Templates

P8-D5 新增 portfolio paper execution 用户可见响应模板。

新增文件：

- fcf/api/portfolio_paper_execution_response_templates.py
- tests/test_portfolio_paper_execution_response_templates.py

新增入口：

- render_portfolio_paper_execution_user_response

覆盖响应类型：

- portfolio_paper_success
- portfolio_paper_partial_success
- portfolio_policy_deny
- portfolio_risk_deny
- portfolio_schema_error

安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响

下一步：

P8-D6：Portfolio guarded paper execution smoke runner。
