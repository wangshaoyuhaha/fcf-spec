# P8-D6 - Portfolio Guarded Paper Execution Smoke Runner

P8-D6 新增 portfolio guarded paper execution smoke runner。

新增文件：

- scripts/run_portfolio_guarded_paper_execution_smoke.py
- tests/test_portfolio_guarded_paper_execution_smoke.py

runner 读取：

- fixtures/paper_order_portfolios_multi_asset.json

runner 调用：

- handle_portfolio_paper_execution
- render_portfolio_paper_execution_user_response

覆盖 portfolio case：

- portfolio_all_fill
- portfolio_mixed_results
- portfolio_policy_deny
- portfolio_risk_deny

覆盖 response type：

- portfolio_paper_success
- portfolio_paper_partial_success
- portfolio_policy_deny
- portfolio_risk_deny

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

P8-D7：Portfolio guarded paper execution acceptance。
