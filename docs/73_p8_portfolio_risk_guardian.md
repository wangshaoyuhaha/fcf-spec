# P8-D4 - Portfolio-level Risk Exposure Checks

## 1. 目的

P8-D4 新增 Portfolio-level risk guardian。

该模块把 P8-D3 中 portfolio paper execution API wrapper 内部的组合级风险检查拆成独立模块。

新增模块：

- fcf/policy/portfolio_risk_guardian.py

新增测试：

- tests/test_portfolio_risk_guardian.py

P8-D4 不接真实交易所 API。
P8-D4 不保存真实 API key。
P8-D4 不读取钱包私钥。
P8-D4 不真实下单。
P8-D4 不读取真实账户余额。
P8-D4 不读取真实仓位。
P8-D4 不声明真实成交。
P8-D4 不声明真实资金影响。

## 2. 新增入口

新增函数：

- evaluate_portfolio_risk_guardian

输入：

- orders
- risk_context

输出稳定 dict：

- ok
- guardian
- guardian_version
- deny_reasons
- checks
- exposure
- safe_boundary

## 3. 覆盖风险规则

P8-D4 覆盖：

- max_order_count
- max_total_notional
- max_asset_class_notional
- blocked_asset_classes
- blocked_symbols
- duplicate_order_keys
- max_same_side_count
- max_single_order_notional

## 4. Exposure summary

P8-D4 输出 exposure summary：

- order_count
- total_notional
- notional_by_asset_class
- order_count_by_asset_class
- side_count_by_asset_class
- symbols
- duplicated_symbols
- blocked_symbols_hit
- blocked_asset_classes_hit
- max_single_order_notional

## 5. 与 P8-D3 API 的关系

P8-D4 后，portfolio_paper_execution_api 使用：

- evaluate_portfolio_risk_guardian

来执行组合级 risk checks。

portfolio paper execution API 仍然保持：

- portfolio policy 先执行
- portfolio risk 后执行
- 逐笔 order 再调用 handle_paper_execution
- 不允许绕过 policy / risk

## 6. 安全边界

P8-D4 继续保持：

- execution_mode=paper
- real_order=false
- real_execution=false
- real_exchange_api=false
- real_money_impact=false
- no_real_exchange_api=true
- no_real_order_placement=true
- no_exchange_api_key_storage=true
- no_wallet_private_key_access=true
- policy_risk_cannot_be_bypassed=true

PortfolioRiskDeny 不是交易所真实拒单。
PortfolioRiskDeny 不是实盘失败。
PortfolioRiskDeny 是本地 deterministic 风险拒绝。

## 7. 验收标准

P8-D4 完成需要满足：

- 新增 fcf/policy/portfolio_risk_guardian.py
- 新增 tests/test_portfolio_risk_guardian.py
- portfolio_paper_execution_api 使用 evaluate_portfolio_risk_guardian
- 覆盖 max_order_count
- 覆盖 max_total_notional
- 覆盖 max_asset_class_notional
- 覆盖 blocked_asset_classes
- 覆盖 blocked_symbols
- 覆盖 duplicate_order_keys
- 覆盖 max_same_side_count
- 覆盖 max_single_order_notional
- python main.py 输出 events_recorded: 8
- 所有现有 smoke runner 输出 status completed
- python -m pytest -q 通过

## 8. 下一步建议

进入 P8-D5：Portfolio paper execution user-facing response templates。

建议新增：

- fcf/api/portfolio_paper_execution_response_templates.py
- tests/test_portfolio_paper_execution_response_templates.py

目标：

- portfolio_paper_success
- portfolio_paper_partial_success
- portfolio_policy_deny
- portfolio_risk_deny
- portfolio_schema_error
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

