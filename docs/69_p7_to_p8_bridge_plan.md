# P7-D9 - Phase 7 to Phase 8 Bridge Plan

## 1. 目的

P7-D9 是 Phase 7 到 Phase 8 的桥接规划文档。

P7-D8 已经完成 post-closeout guarded paper execution regression summary，并确认：

- Phase 7 第一轮 smoke runner 全部 completed
- guarded execution 16 个 case 全部通过
- guarded response 16 个 case 全部通过
- ready_for_phase8_planning 为 true

P7-D9 不改核心交易逻辑。
P7-D9 不接真实交易所 API。
P7-D9 不保存真实 API key。
P7-D9 不读取钱包私钥。
P7-D9 不真实下单。

## 2. Phase 7 当前完成状态

Phase 7 已完成：

- P7-D1：multi-asset guarded paper fixture plan
- P7-D2：multi-asset guarded paper execution fixture
- P7-D3：multi-asset guarded paper execution smoke runner
- P7-D4：Dify response integration for guarded paper fixture smoke
- P7-D5：guarded paper execution phase acceptance
- P7-D6：guarded paper execution acceptance smoke runner
- P7-D7：Phase 7 closeout / project state consolidation
- P7-D8：post-closeout guarded paper execution regression summary
- P7-D9：Phase 7 to Phase 8 bridge plan

当前覆盖：

- crypto
- equities
- fx
- commodities

当前 guarded 分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

当前用户响应类型：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny

## 3. Phase 8 候选主题

Phase 8 建议主题：

Portfolio-level guarded paper execution。

中文含义：

组合级 guarded paper execution。

当前 Phase 5 / Phase 6 / Phase 7 已经完成单笔 paper order 的 sandbox / policy / risk / response / multi-asset fixture 覆盖。

Phase 8 可以开始进入组合层：

- 多订单组合
- 多资产组合
- 组合级 exposure
- 跨资产 exposure
- portfolio-level policy
- portfolio-level risk guardian
- portfolio-level paper-only response
- portfolio-level regression smoke

## 4. Phase 8 候选方向一：portfolio-level guarded paper execution

目标：

- 支持一次提交多笔 paper order
- 每笔 order 仍然走 policy -> risk -> sandbox execution
- portfolio 层汇总所有 order 的结果
- portfolio 层汇总 filled / rejected / policy_deny / risk_deny 数量
- portfolio 层汇总资产类别 exposure
- portfolio 层汇总 notional
- portfolio 层返回稳定 response dict

明确边界：

- 不真实下单
- 不接真实交易所 API
- 不把 portfolio paper execution 伪装成 real execution
- 不允许某笔 order 绕过 policy / risk

## 5. Phase 8 候选方向二：cross-asset exposure checks

目标：

- 汇总 crypto / equities / fx / commodities 的组合级风险暴露
- 增加 max_total_notional
- 增加 max_asset_class_notional
- 增加 blocked_asset_class
- 增加 max_order_count
- 增加 duplicate symbol 检查
- 增加 same side concentration 检查

第一轮建议只做本地 deterministic checks。
不接外部行情。
不接交易所。
不接账户余额。
不接真实仓位。

## 6. Phase 8 候选方向三：portfolio-level user-facing response

目标：

- 把 portfolio paper execution 的结果转成用户可见响应
- 汇总 filled_count
- 汇总 sandbox_rejected_count
- 汇总 policy_denied_count
- 汇总 risk_denied_count
- 汇总 asset_class_counts
- 汇总 notional_by_asset_class
- 明确 paper-only 安全说明

用户响应必须明确：

- 这不是实盘交易
- 没有连接真实交易所
- 没有使用真实 API key
- 没有真实成交
- 没有真实资金影响

## 7. Phase 8 候选方向四：regression CI entrypoint

目标：

新增统一回归入口：

- scripts/run_all_smokes.py 或 scripts/run_regression_suite.py

该入口汇总：

- Dify market input smoke
- multi-asset market smoke
- paper execution smoke
- guarded paper execution smoke
- Phase 7 regression summary
- Phase 8 portfolio smoke

输出：

- status
- runner
- total_smoke_count
- completed_count
- failed_count
- safe_boundary

该入口可以作为未来 CI 的候选入口。

当前仍不配置真实 CI secret。
当前仍不保存 API key。
当前仍不接真实交易所。

## 8. Phase 8 建议 D1-D6 路线

### P8-D1

Portfolio-level guarded paper execution plan。

只做文档。

新增：

- docs/70_p8_portfolio_guarded_paper_execution_plan.md

### P8-D2

Portfolio paper order fixture。

新增：

- fixtures/paper_order_portfolios_multi_asset.json
- tests/test_portfolio_paper_order_fixture.py

### P8-D3

Portfolio execution schema / summary module。

候选新增：

- fcf/schemas/portfolio_paper_order_schema.py
- fcf/api/portfolio_paper_execution_api.py
- tests/test_portfolio_paper_execution_api.py

### P8-D4

Portfolio-level risk exposure checks。

候选新增：

- fcf/policy/portfolio_risk_guardian.py
- tests/test_portfolio_risk_guardian.py

### P8-D5

Portfolio Dify response templates。

候选新增：

- fcf/api/portfolio_paper_execution_response_templates.py
- tests/test_portfolio_paper_execution_response_templates.py

### P8-D6

Portfolio guarded paper execution smoke runner。

候选新增：

- scripts/run_portfolio_guarded_paper_execution_smoke.py
- tests/test_portfolio_guarded_paper_execution_smoke.py

## 9. Phase 8 不做事项

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

## 10. Phase 8 验收前置条件

进入 Phase 8 前必须保持：

- python main.py 输出 events_recorded: 8
- 所有现有 smoke runner 输出 status completed
- python scripts/run_p7_guarded_paper_execution_regression_summary.py 输出 status completed
- python -m pytest -q 通过
- PROJECT_STATE.md 已记录 P7-D9
- README.md 已记录 P7-D9
- 新聊天续接话术已更新

## 11. P7-D9 验收结论

P7-D9 完成后，Phase 7 到 Phase 8 的桥接规划完成。

推荐下一步进入：

P8-D1：Portfolio-level guarded paper execution plan。

该步骤只做文档规划，不改核心代码，不接真实交易所 API，不真实下单。

