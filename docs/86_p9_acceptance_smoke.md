# P9-D7 - Phase 9 Acceptance Smoke

P9-D7 新增 Phase 9 acceptance smoke。

新增文件：

- docs/86_p9_acceptance_smoke.md
- scripts/run_p9_acceptance_smoke.py
- tests/test_p9_acceptance_smoke.py

P9-D7 汇总验证：

- run_all_smokes
- build_global_regression_report
- check_global_safe_boundary
- check_project_state_consistency

P9-D7 覆盖阶段：

- P9-D1：Global regression suite plan
- P9-D2：run_all_smokes entrypoint
- P9-D3：global regression report schema
- P9-D4：global safe boundary checker
- P9-D5：PROJECT_STATE / README consistency checker
- P9-D6：CI-safe regression command document
- P9-D7：Phase 9 acceptance smoke

输出字段：

- status
- runner
- runner_version
- acceptance_summary
- components
- safe_boundary

验收目标：

- run_all_smokes status completed
- global regression report status completed
- global safe boundary checker status completed
- project state consistency checker status completed
- ready_for_p9_d8_closeout = true

P9-D7 不接真实交易所 API。
P9-D7 不保存真实 API key。
P9-D7 不读取钱包私钥。
P9-D7 不真实下单。
P9-D7 不读取真实账户余额。
P9-D7 不读取真实仓位。
P9-D7 不声明真实成交。
P9-D7 不声明真实资金影响。
P9-D7 不配置 CI secret。
P9-D7 不做 production deployment。

下一步：

P9-D8：Phase 9 closeout。
