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

- external_non_fcf_project
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


## P1 当前状态

P1 已完成 paper-only 分析平台基础能力：

- paper 输入校验
- paper 市场分析
- paper 风险评分
- paper 策略草案
- paper 报告渲染
- paper 运行记录
- paper 报告导出
- paper 历史摘要
- analysis CLI
- 一键验证脚本

当前验证：

- python scripts/run_all_checks.py
- 45 passed
- ALL CHECKS PASSED

仍然禁止：

- 接真实交易所 API
- 保存真实 API key
- 读取钱包私钥
- 真实下单
- 读取真实余额
- 读取真实仓位
- 声明真实成交
- 声明真实资金影响
- 自动实盘交易
- 绕过人工复核


## P2 当前状态

P2 已完成多 symbol / 批量 paper 分析基础能力：

- 多 symbol paper 输入
- 批量 paper 分析
- 批量 paper 报告
- JSON / CSV 批量文件导入
- 批量 CLI
- 批量报告导出
- 批量运行记录
- 批量历史摘要
- 批量质量闸门
- 批量错误收集
- 批量 manifest

当前验证：

- python scripts/run_all_checks.py
- 69 passed
- ALL CHECKS PASSED

仍然禁止：

- 接真实交易所 API
- 保存真实 API key
- 读取钱包私钥
- 真实下单
- 读取真实余额
- 读取真实仓位
- 声明真实成交
- 声明真实资金影响
- 自动实盘交易
- 绕过人工复核

## FCF Architecture Anchor

This repository is currently named btc_finance_platform, but BTC is only the first paper-only implementation line.

The broader target is a general FCF-style finance platform for stocks and other financial markets.

Original FCF skeleton ideas preserved:
- event-driven core
- event model
- policy engine
- perception module
- regime module
- governor module
- execution module restricted to paper-only at this stage
- simulation module
- meta/self-check module
- audit store

Safety boundary:
- paper-only
- no real exchange API
- no real API key
- no wallet private key
- no real order
- no real execution
- no real balance
- no real position
- no real money impact
- operator review required
