# P9-D4 - Global Safe Boundary Checker

P9-D4 新增 global safe boundary checker。

新增文件：

- fcf/regression/global_safe_boundary_checker.py
- tests/test_p9_global_safe_boundary_checker.py
- docs/83_p9_global_safe_boundary_checker.md

新增入口：

- check_global_safe_boundary

输入：

- global regression report dict
- 或者直接输入 safe_boundary dict

输出：

- status
- checker
- checker_version
- ok
- checks
- violations
- safe_boundary
- ready_for_p9_d5_project_state_checker

必须验证：

- paper_only = true
- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false
- no_real_exchange_api = true
- no_real_order_placement = true
- no_exchange_api_key_storage = true
- no_wallet_private_key_access = true
- no_real_account_balance_read = true
- no_real_position_read = true
- does_not_claim_real_trade_success = true
- ci_secret_required = false
- production_deployment = false

P9-D4 不接真实交易所 API。
P9-D4 不保存真实 API key。
P9-D4 不读取钱包私钥。
P9-D4 不真实下单。
P9-D4 不读取真实账户余额。
P9-D4 不读取真实仓位。
P9-D4 不声明真实成交。
P9-D4 不声明真实资金影响。
P9-D4 不配置 CI secret。
P9-D4 不做 production deployment。

下一步：

P9-D5：PROJECT_STATE / README consistency checker。
