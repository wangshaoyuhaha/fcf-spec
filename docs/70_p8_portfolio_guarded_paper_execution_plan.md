# P8-D1 - Portfolio-level Guarded Paper Execution Plan

## 1. 目的

P8-D1 启动 Phase 8。

Phase 8 建议主题是 Portfolio-level guarded paper execution，也就是组合级 guarded paper execution。

P8-D1 只做规划文档。
P8-D1 不改核心执行逻辑。
P8-D1 不接真实交易所 API。
P8-D1 不保存真实 API key。
P8-D1 不读取钱包私钥。
P8-D1 不真实下单。

## 2. 当前基础

Phase 7 guarded paper execution 第一轮已经完成阶段收尾。

当前系统已经具备：

- 单笔 paper order schema
- sandbox execution engine
- paper execution API wrapper
- Dify paper execution adapter
- paper execution response templates
- policy gate
- risk guardian
- policy deny response
- risk deny response
- multi-asset guarded paper fixture
- guarded paper execution smoke runner
- guarded paper Dify response smoke
- guarded paper acceptance smoke
- post-closeout regression summary

当前覆盖资产类别：

- crypto
- equities
- fx
- commodities

当前覆盖 guarded 分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

当前用户响应类型：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny

## 3. Phase 8 核心目标

Phase 8 第一轮目标是把单笔 guarded paper execution 扩展为组合级 guarded paper execution。

组合级执行不是实盘执行。

组合级执行只是对一组 paper orders 做：

- schema validation
- policy gate
- risk guardian
- sandbox execution
- result aggregation
- portfolio-level exposure summary
- user-facing response summary
- replay / regression friendly summary

## 4. Portfolio 输入结构规划

建议 portfolio request 输入结构包含：

- portfolio_id
- correlation_id
- source
- orders
- portfolio_policy_context
- portfolio_risk_context
- metadata

字段说明：

- portfolio_id：组合请求 ID
- correlation_id：追踪 ID
- source：输入来源
- orders：paper order 列表
- portfolio_policy_context：组合级 policy 上下文
- portfolio_risk_context：组合级 risk 上下文
- metadata：扩展信息

## 5. Portfolio order 结构规划

orders 内每一笔 order 继续复用单笔 paper order 字段：

- asset_class
- symbol
- venue
- market_type
- side
- order_type
- quantity
- price
- time_in_force
- source
- correlation_id
- metadata

每笔 order 仍然必须走：

1. evaluate_paper_execution_policy
2. evaluate_paper_execution_risk
3. execute_sandbox_order_with_eventstore

不允许任何一笔 order 绕过 policy / risk。

## 6. Portfolio 输出结构规划

建议 portfolio response 输出包含：

- ok
- api
- api_version
- error
- data
- portfolio_id
- execution_mode
- order_count
- filled_count
- sandbox_rejected_count
- policy_denied_count
- risk_denied_count
- asset_class_counts
- notional_by_asset_class
- results
- safe_boundary

## 7. Portfolio 分支规划

组合级结果可以包含多种 order 分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

组合级本身也可以有 portfolio-level deny：

- portfolio_policy_deny
- portfolio_risk_deny

第一轮建议：

- P8-D2 先做 fixture
- P8-D3 再做组合级 API wrapper
- P8-D4 再做 cross-asset exposure checks
- P8-D5 再做用户响应模板
- P8-D6 再做 smoke runner

## 8. Portfolio-level policy 候选规则

组合级 policy gate 可先规划以下规则：

- 禁止真实执行请求
- 禁止绕过 risk 请求
- 禁止保存 API key 请求
- 禁止连接真实交易所请求
- 禁止 force execute 请求
- 禁止 real_order 标记
- 禁止 real_execution 标记

命中任意规则：

- portfolio_policy_deny
- ok=false
- 不进入单笔 sandbox execution
- 不生成真实交易行为

## 9. Portfolio-level risk 候选规则

组合级 risk guardian 可先规划以下规则：

- max_order_count
- max_total_notional
- max_asset_class_notional
- blocked_asset_classes
- blocked_symbols
- duplicate_order_keys
- max_same_side_count
- max_single_order_notional

命中组合级风险规则：

- portfolio_risk_deny
- ok=false
- 不进入 sandbox execution
- 不生成真实交易行为

## 10. Cross-asset exposure checks 规划

Cross-asset exposure checks 只做本地 deterministic 计算。

第一轮不接外部行情。
第一轮不接账户余额。
第一轮不接真实仓位。
第一轮不接真实交易所。

建议输出：

- total_notional
- notional_by_asset_class
- order_count_by_asset_class
- side_count_by_asset_class
- symbols
- duplicated_symbols
- blocked_symbols_hit
- blocked_asset_classes_hit

## 11. Portfolio user-facing response 规划

组合级用户响应必须说明：

- 这是 paper-only portfolio execution
- 没有真实下单
- 没有连接真实交易所
- 没有使用真实 API key
- 没有真实成交
- 没有真实资金影响

建议响应类型：

- portfolio_paper_success
- portfolio_paper_partial_success
- portfolio_policy_deny
- portfolio_risk_deny
- portfolio_schema_error

## 12. Regression / CI 入口规划

Phase 8 可以新增统一回归入口：

- scripts/run_regression_suite.py
- scripts/run_all_smokes.py

该入口用于汇总：

- Dify market input smoke
- multi-asset market smoke
- paper execution smoke
- guarded paper execution smoke
- P7 regression summary
- P8 portfolio smoke

当前不配置真实 CI secret。
当前不保存 API key。
当前不接真实交易所。

## 13. Phase 8 第一轮建议路线

P8-D1：Portfolio-level guarded paper execution plan。
P8-D2：Portfolio paper order fixture。
P8-D3：Portfolio paper execution API wrapper。
P8-D4：Portfolio-level risk exposure checks。
P8-D5：Portfolio paper execution user-facing response templates。
P8-D6：Portfolio guarded paper execution smoke runner。
P8-D7：Portfolio guarded paper execution acceptance。
P8-D8：Phase 8 closeout / project state consolidation。

## 14. Phase 8 不做事项

Phase 8 第一轮不做：

- 真实交易所 API
- 真实下单
- 真实 API key 保存
- 钱包私钥读取
- 真实账户余额读取
- 真实仓位读取
- 实盘收益声明
- 实盘成交声明
- 交易所真实拒单声明
- 真实资金影响声明

## 15. P8-D1 验收标准

P8-D1 完成需要满足：

- 新增 docs/70_p8_portfolio_guarded_paper_execution_plan.md
- 文档明确 portfolio 输入结构
- 文档明确 portfolio 输出结构
- 文档明确 portfolio 分支规划
- 文档明确 portfolio-level policy 候选规则
- 文档明确 portfolio-level risk 候选规则
- 文档明确 cross-asset exposure checks
- 文档明确 user-facing response 规划
- 文档明确 regression / CI 入口规划
- 文档明确安全边界
- python main.py 输出 events_recorded: 8
- 所有现有 smoke runner 输出 status completed
- python -m pytest -q 通过

## 16. 下一步建议

进入 P8-D2：Portfolio paper order fixture。

建议新增：

- fixtures/paper_order_portfolios_multi_asset.json
- tests/test_portfolio_paper_order_fixture.py

目标：

- 覆盖 portfolio_all_fill
- 覆盖 portfolio_mixed_results
- 覆盖 portfolio_policy_deny
- 覆盖 portfolio_risk_deny
- 覆盖 crypto / equities / fx / commodities
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

