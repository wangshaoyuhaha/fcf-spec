# P8-D3 - Portfolio Paper Execution API Wrapper

## 1. 目的

P8-D3 新增 Portfolio paper execution API wrapper。

该 API wrapper 读取 portfolio request，逐笔调用现有单笔 paper execution API：

- handle_paper_execution

并汇总 portfolio-level 结果。

P8-D3 不接真实交易所 API。
P8-D3 不保存真实 API key。
P8-D3 不读取钱包私钥。
P8-D3 不真实下单。
P8-D3 不读取真实账户余额。
P8-D3 不读取真实仓位。
P8-D3 不声明真实成交。
P8-D3 不声明真实资金影响。

## 2. 新增文件

- docs/72_p8_portfolio_paper_execution_api_wrapper.md
- fcf/api/portfolio_paper_execution_api.py
- tests/test_portfolio_paper_execution_api.py

## 3. API 入口

新增入口：

- handle_portfolio_paper_execution

输入：

- portfolio_request
- output_dir

输出稳定 response dict：

- ok
- api
- api_version
- error
- data

## 4. Portfolio 执行顺序

portfolio-level 顺序：

1. validate portfolio request
2. evaluate portfolio policy context
3. evaluate portfolio risk context
4. 逐笔调用 handle_paper_execution
5. 汇总 order results
6. 汇总 safe_boundary
7. 返回稳定 response dict

单笔 order 仍然保持现有顺序：

1. evaluate_paper_execution_policy
2. evaluate_paper_execution_risk
3. execute_sandbox_order_with_eventstore

## 5. Portfolio-level deny 行为

portfolio_policy_deny：

- ok=false
- error.type=PortfolioPolicyDeny
- 不进入逐笔 sandbox execution
- 所有 order 标记为 blocked_by_portfolio_policy
- 不生成真实交易行为

portfolio_risk_deny：

- ok=false
- error.type=PortfolioRiskDeny
- 不进入逐笔 sandbox execution
- 所有 order 标记为 blocked_by_portfolio_risk
- 不生成真实交易行为

## 6. Order-level 汇总行为

逐笔 order 可能产生：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

portfolio 汇总：

- filled_count
- sandbox_rejected_count
- policy_denied_count
- risk_denied_count
- asset_class_counts
- branch_counts
- total_notional
- notional_by_asset_class
- results

## 7. 安全边界

P8-D3 继续保持：

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

sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
PolicyDeny 不是交易所真实拒单。
RiskDeny 不是交易所真实拒单。
PortfolioPolicyDeny 不是交易所真实拒单。
PortfolioRiskDeny 不是交易所真实拒单。

## 8. 验收标准

P8-D3 完成需要满足：

- 新增 portfolio paper execution API wrapper
- portfolio_all_fill 返回 completed
- portfolio_mixed_results 返回 partial
- portfolio_policy_deny 返回 PortfolioPolicyDeny
- portfolio_risk_deny 返回 PortfolioRiskDeny
- 汇总 filled / sandbox_rejected / policy_denied / risk_denied
- 汇总 asset_class_counts
- 汇总 branch_counts
- 保持 paper-only safe_boundary
- python main.py 输出 events_recorded: 8
- 所有现有 smoke runner 输出 status completed
- python -m pytest -q 通过

## 9. 下一步建议

进入 P8-D4：Portfolio-level risk exposure checks。

建议新增：

- fcf/policy/portfolio_risk_guardian.py
- tests/test_portfolio_risk_guardian.py

目标：

- 把 P8-D3 内部 portfolio risk checks 拆成独立模块
- 覆盖 max_order_count
- 覆盖 max_total_notional
- 覆盖 max_asset_class_notional
- 覆盖 blocked_asset_classes
- 覆盖 blocked_symbols
- 覆盖 max_same_side_count
- 覆盖 max_single_order_notional
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

