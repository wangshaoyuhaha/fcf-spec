# P0-D10 One Command Validation

状态：已完成

范围：

- 增加一键验证脚本
- 一次性运行所有 smoke
- 一次性运行 CLI smoke
- 一次性运行全部 pytest

命令：

- python scripts/run_all_checks.py

当前预期：

- 19 passed
- ALL CHECKS PASSED

安全：

- paper-only 不变
- 不接真实交易所 API
- 不保存真实 API key
- 不真实下单
- 不读取真实余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响
- 必须人工复核
