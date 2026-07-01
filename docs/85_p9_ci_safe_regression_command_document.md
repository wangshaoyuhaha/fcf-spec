# P9-D6 - CI-safe Regression Command Document

P9-D6 新增 CI-safe regression command document。

新增文件：

- docs/85_p9_ci_safe_regression_command_document.md
- tests/test_p9_ci_safe_regression_command_document.py

## 1. 目的

P9-D6 只补充 CI-safe regression 命令文档和测试。

P9-D6 不改核心交易逻辑。
P9-D6 不接真实交易所 API。
P9-D6 不保存真实 API key。
P9-D6 不读取钱包私钥。
P9-D6 不真实下单。
P9-D6 不读取真实账户余额。
P9-D6 不读取真实仓位。
P9-D6 不声明真实成交。
P9-D6 不声明真实资金影响。
P9-D6 不配置 CI secret。
P9-D6 不做 production deployment。

## 2. 本地推荐命令

本地完整回归建议运行：

- python main.py
- python scripts/run_all_smokes.py
- python -m pytest -q

## 3. CI 推荐命令

CI 中推荐运行：

- python scripts/run_all_smokes.py
- python -m pytest -q

## 4. CI 不需要的内容

CI 不需要：

- exchange API key
- wallet private key
- real account credentials
- real broker credentials
- CI secret
- production deployment permission

## 5. CI 必须保持的安全边界

CI 必须保持：

- no_real_exchange_api = true
- no_real_order_placement = true
- no_exchange_api_key_storage = true
- no_wallet_private_key_access = true
- no_real_account_balance_read = true
- no_real_position_read = true
- does_not_claim_real_trade_success = true
- ci_secret_required = false
- production_deployment = false

## 6. 当前全局回归入口

当前全局入口：

- scripts/run_all_smokes.py

该入口汇总：

- P7 guarded paper execution regression summary
- P8 portfolio guarded paper regression summary

输出：

- status
- suites
- counts
- readiness
- safe_boundary

## 7. 当前 schema / checker

当前已有：

- build_global_regression_report
- check_global_safe_boundary
- check_project_state_consistency

## 8. P9-D6 验收标准

P9-D6 完成需要满足：

- 新增 docs/85_p9_ci_safe_regression_command_document.md
- 新增 tests/test_p9_ci_safe_regression_command_document.py
- 文档明确本地回归命令
- 文档明确 CI 回归命令
- 文档明确 CI 不需要 secret
- 文档明确 CI 不需要交易所 API key
- 文档明确 CI 不读取钱包私钥
- 文档明确 CI 不连接真实交易所
- 文档明确 CI 不真实下单
- run_all_smokes 仍然 completed
- global safe boundary checker 仍然 completed
- project state consistency checker 仍然 completed
- python main.py 输出 events_recorded: 8
- python scripts/run_all_smokes.py 输出 status completed
- python -m pytest -q 通过

下一步：

P9-D7：Phase 9 acceptance smoke。
