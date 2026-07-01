# P9-D1 - Global Regression Suite Plan

P9-D1 启动 Phase 9。

Phase 9 建议主题：

Global paper-only regression suite and CI-safe operational readiness。

中文含义：

全局 paper-only 回归套件与 CI 安全运行准备。

P9-D1 只做规划文档。
P9-D1 不改核心执行逻辑。
P9-D1 不接真实交易所 API。
P9-D1 不保存真实 API key。
P9-D1 不读取钱包私钥。
P9-D1 不真实下单。
P9-D1 不读取真实账户余额。
P9-D1 不读取真实仓位。
P9-D1 不声明真实成交。
P9-D1 不声明真实资金影响。
P9-D1 不配置 CI secret。
P9-D1 不做 production deployment。

## 当前基础

当前已完成：

- Phase 1 Build Spine
- Phase 2 多资产 MarketContext 基础层
- Phase 3 数据接入与 Dify integration
- Phase 4 schema hardening 与 multi-asset fixture expansion
- Phase 5 paper-only sandbox execution
- Phase 6 policy / risk deny hardening
- Phase 7 guarded paper execution 第一轮
- Phase 8 portfolio guarded paper execution 第一轮

## Phase 9 目标

Phase 9 第一轮目标：

- 建立统一 smoke / regression 入口
- 汇总 P7 regression summary
- 汇总 P8 portfolio regression summary
- 生成 machine-readable regression report
- 增加全局 safe_boundary checker
- 增加 PROJECT_STATE / README consistency checker
- 增加 CI-safe regression command document

## 候选全局入口

建议新增：

- scripts/run_all_smokes.py

或者：

- scripts/run_regression_suite.py

入口输出：

- status
- runner
- total_smoke_count
- completed_count
- failed_count
- p7_summary
- p8_summary
- safe_boundary
- report_path

## Machine-readable report 规划

建议输出 JSON report，包含：

- report_version
- generated_by
- phase
- suites
- counts
- safe_boundary
- readiness
- next_action

## Global safe boundary checker 规划

全局 safe_boundary 必须验证：

- no_real_exchange_api
- no_real_order_placement
- no_exchange_api_key_storage
- no_wallet_private_key_access
- no_real_account_balance_read
- no_real_position_read
- does_not_claim_real_trade_success
- paper_only

## Project state consistency checker 规划

建议检查：

- README.md 是否包含最新 phase
- PROJECT_STATE.md 是否包含最新 phase
- README.md 是否包含安全边界
- PROJECT_STATE.md 是否包含安全边界
- README.md 是否包含下一步
- PROJECT_STATE.md 是否包含下一步

## CI-safe command document 规划

建议新增文档说明：

- 本地如何运行 regression suite
- CI 中如何运行 regression suite
- CI 不需要 secret
- CI 不需要交易所 API key
- CI 不需要钱包私钥
- CI 不连接真实交易所
- CI 不真实下单

## Phase 9 第一轮路线

P9-D1：Global regression suite plan。

P9-D2：run_all_smokes entrypoint。

P9-D3：global regression report schema。

P9-D4：global safe boundary checker。

P9-D5：PROJECT_STATE / README consistency checker。

P9-D6：CI-safe regression command document。

P9-D7：Phase 9 acceptance smoke。

P9-D8：Phase 9 closeout。

## Phase 9 不做事项

Phase 9 第一轮不做：

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
- CI secret 配置
- production deployment

## P9-D1 验收标准

P9-D1 完成需要满足：

- 新增 docs/80_p9_global_regression_suite_plan.md
- 新增 tests/test_p9_global_regression_suite_plan.py
- 文档明确 Phase 9 主题
- 文档明确全局 regression suite 目标
- 文档明确 machine-readable report
- 文档明确 safe_boundary checker
- 文档明确 project state consistency checker
- 文档明确 CI-safe command document
- 文档明确 P9-D1 到 P9-D8 路线
- P8 regression summary 仍然 completed
- ready_for_phase9_planning 仍然 true
- python main.py 输出 events_recorded: 8
- python scripts/run_p8_portfolio_guarded_paper_regression_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

进入 P9-D2：run_all_smokes entrypoint。
