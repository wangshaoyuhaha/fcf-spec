# P8-D2 - Portfolio Paper Order Fixture

## 1. 目的

P8-D2 新增 Portfolio paper order fixture。

该 fixture 用于 Phase 8 组合级 guarded paper execution 的后续实现。

P8-D2 只新增 fixture 和 fixture schema 测试。
P8-D2 不实现 portfolio execution API。
P8-D2 不改核心执行逻辑。
P8-D2 不接真实交易所 API。
P8-D2 不保存真实 API key。
P8-D2 不读取钱包私钥。
P8-D2 不真实下单。

## 2. 新增文件

- docs/71_p8_portfolio_paper_order_fixture.md
- fixtures/paper_order_portfolios_multi_asset.json
- tests/test_portfolio_paper_order_fixture.py

## 3. Fixture 覆盖组合场景

当前 fixture 覆盖 4 个 portfolio case：

- portfolio_all_fill
- portfolio_mixed_results
- portfolio_policy_deny
- portfolio_risk_deny

## 4. Fixture 覆盖资产类别

当前 fixture 覆盖：

- crypto
- equities
- fx
- commodities

## 5. Fixture 覆盖订单分支

当前 fixture 覆盖：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

## 6. Portfolio case 结构

每个 portfolio case 包含：

- portfolio_id
- case_id
- branch
- description
- request
- expected

request 包含：

- portfolio_id
- correlation_id
- source
- orders
- portfolio_policy_context
- portfolio_risk_context
- metadata

expected 包含：

- ok
- portfolio_status
- order_count
- filled_count
- sandbox_rejected_count
- policy_denied_count
- risk_denied_count
- asset_class_counts
- branch_counts
- real_execution
- safe_boundary

## 7. 安全边界

P8-D2 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响
- 不把 paper execution 伪装成 real execution

## 8. 验收标准

P8-D2 完成需要满足：

- fixture 文件存在
- fixture 是 JSON list
- fixture 覆盖 4 个 portfolio case
- fixture 覆盖 portfolio_all_fill
- fixture 覆盖 portfolio_mixed_results
- fixture 覆盖 portfolio_policy_deny
- fixture 覆盖 portfolio_risk_deny
- fixture 覆盖 crypto / equities / fx / commodities
- fixture 覆盖 fill_success / sandbox_reject / policy_deny / risk_deny
- 每个 order 必须保持 paper-only
- 每个 portfolio expected 必须声明 real_execution false
- python main.py 输出 events_recorded: 8
- 所有现有 smoke runner 输出 status completed
- python -m pytest -q 通过

## 9. 下一步建议

进入 P8-D3：Portfolio paper execution API wrapper。

建议新增：

- fcf/api/portfolio_paper_execution_api.py
- tests/test_portfolio_paper_execution_api.py

目标：

- 读取 portfolio fixture
- 逐笔调用 handle_paper_execution
- 汇总 filled / sandbox_rejected / policy_denied / risk_denied
- 汇总 asset_class_counts
- 汇总 branch_counts
- 返回稳定 response dict
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

