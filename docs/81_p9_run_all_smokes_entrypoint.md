# P9-D2 - run_all_smokes Entrypoint

P9-D2 新增全局 smoke / regression 入口。

新增文件：

- scripts/run_all_smokes.py
- tests/test_p9_run_all_smokes_entrypoint.py
- docs/81_p9_run_all_smokes_entrypoint.md

入口命令：

- python scripts/run_all_smokes.py

当前汇总：

- P7 guarded paper execution regression summary
- P8 portfolio guarded paper regression summary

输出字段：

- status
- runner
- suites
- counts
- readiness
- safe_boundary

P9-D2 不接真实交易所 API。
P9-D2 不保存真实 API key。
P9-D2 不读取钱包私钥。
P9-D2 不真实下单。
P9-D2 不读取真实账户余额。
P9-D2 不读取真实仓位。
P9-D2 不声明真实成交。
P9-D2 不声明真实资金影响。
P9-D2 不配置 CI secret。
P9-D2 不做 production deployment。

下一步：

P9-D3：global regression report schema。
