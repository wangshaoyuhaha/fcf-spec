# P0-D9 CLI Entry

状态：已完成

范围：

- 增加最小命令行入口
- 支持一条命令运行完整 paper pipeline
- 增加 CLI 测试
- 保持 paper-only 安全边界

命令示例：

- python main.py --symbol BTCUSDT --price 65000

安全：

- 不接真实交易所 API
- 不保存真实 API key
- 不真实下单
- 不读取真实余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响
- 必须等待人工复核
