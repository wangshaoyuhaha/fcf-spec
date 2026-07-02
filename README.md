# BTC Finance Platform

状态：P0 开发中
模式：paper-only
路径：C:\Users\Admin\Desktop\btc_finance_platform

## 当前项目说明

这是一个新的独立 BTC / 金融平台项目。

它不是 FCF / fcf-spec。

FCF / fcf-spec 已经最终归档并关闭：

- final commit: 3287896
- latest verified test result: 773 passed
- final backup zip exists on Desktop

不要把本项目和以下文件夹混用：

- football_quant_ai
- _WC2026_项目全量备份

## 当前已完成

- P0-D1：项目骨架和安全边界 smoke
- P0-D2：架构文档
- P0-D3：paper-only 市场快照模块
- P0-D4：paper-only 决策草案模块
- P0-D5：人工复核闸门
- P0-D6：端到端 paper pipeline smoke
- P0-D7：续聊说明和状态总结
- P0-D8：README 快速入口说明

## 当前验证

最近验证：

- python -m pytest -q
- 17 passed

## 常用命令

运行安全边界检查：

- python scripts/run_safety_smoke.py

运行市场快照 smoke：

- python scripts/run_market_snapshot_smoke.py

运行决策草案 smoke：

- python scripts/run_decision_draft_smoke.py

运行人工复核 smoke：

- python scripts/run_operator_review_smoke.py

运行端到端 paper pipeline：

- python scripts/run_paper_pipeline_smoke.py

运行全部测试：

- python -m pytest -q

## 安全边界

本项目必须保持 paper-only。

禁止：

- 接真实交易所 API
- 保存真实 API key
- 读取钱包私钥
- 真实下单
- 读取真实账户余额
- 读取真实仓位
- 声明真实成交
- 声明真实资金影响
- 配置 CI secret
- production deployment
- 自动实盘交易
- 绕过人工复核
- 绕过 policy / risk / safe_boundary

## 下一步

P0-D9：添加最小命令行入口，让用户可以一条命令跑完整 paper pipeline。
