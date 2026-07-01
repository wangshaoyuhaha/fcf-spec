# P9-D3 - Global Regression Report Schema

P9-D3 新增 machine-readable global regression report schema。

新增文件：

- fcf/regression/__init__.py
- fcf/regression/global_regression_report_schema.py
- tests/test_p9_global_regression_report_schema.py
- docs/82_p9_global_regression_report_schema.md

新增入口：

- build_global_regression_report

输入：

- scripts/run_all_smokes.py 的输出 dict

输出字段：

- report_version
- generated_by
- phase
- status
- source_runner
- suites
- counts
- readiness
- safe_boundary
- report_path
- next_action

P9-D3 不接真实交易所 API。
P9-D3 不保存真实 API key。
P9-D3 不读取钱包私钥。
P9-D3 不真实下单。
P9-D3 不读取真实账户余额。
P9-D3 不读取真实仓位。
P9-D3 不声明真实成交。
P9-D3 不声明真实资金影响。
P9-D3 不配置 CI secret。
P9-D3 不做 production deployment。

下一步：

P9-D4：global safe boundary checker。
