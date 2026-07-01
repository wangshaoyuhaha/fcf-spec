# P9-D5 - PROJECT_STATE / README Consistency Checker

P9-D5 新增 PROJECT_STATE / README consistency checker。

新增文件：

- fcf/regression/project_state_consistency_checker.py
- tests/test_p9_project_state_consistency_checker.py
- docs/84_p9_project_state_consistency_checker.md

新增入口：

- check_project_state_consistency

输入：

- README.md path
- PROJECT_STATE.md path

输出：

- status
- checker
- checker_version
- ok
- checks
- violations
- files
- ready_for_p9_d6_ci_safe_command_doc

检查目标：

- README.md 存在
- PROJECT_STATE.md 存在
- README.md 包含 P9-D1 到 P9-D5
- PROJECT_STATE.md 包含 P9-D1 到 P9-D5
- README.md 包含安全边界
- PROJECT_STATE.md 包含安全边界
- README.md 包含下一步 P9-D6
- PROJECT_STATE.md 包含下一步 P9-D6

P9-D5 不接真实交易所 API。
P9-D5 不保存真实 API key。
P9-D5 不读取钱包私钥。
P9-D5 不真实下单。
P9-D5 不读取真实账户余额。
P9-D5 不读取真实仓位。
P9-D5 不声明真实成交。
P9-D5 不声明真实资金影响。
P9-D5 不配置 CI secret。
P9-D5 不做 production deployment。

下一步：

P9-D6：CI-safe regression command document。
