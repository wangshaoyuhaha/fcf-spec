# Archive-D6 - Final Archive Acceptance Smoke

Archive-D6 新增 final archive acceptance smoke。

新增文件：

- docs/126_archive_d6_final_archive_acceptance_smoke.md
- scripts/run_final_archive_acceptance_smoke.py
- tests/test_archive_d6_final_archive_acceptance_smoke.py

## 1. 目的

该 smoke 用于最终确认 FCF paper-only / non-production delivery package 可以进入 Archive-D7 closeout。

final_archive_acceptance_smoke_version = 0.1.0
archive_mode = immutable_non_production_snapshot
paper_only = true
phase = Final Archive
day = Archive-D6
status = active

该 smoke 覆盖：

- P12 final delivery package summary
- ready_for_p12_d10_archive_bridge_plan
- Archive-D1 final archive plan
- Archive-D2 immutable delivery snapshot checklist
- Archive-D3 final release note
- Archive-D4 final archive manifest
- Archive-D5 final operator archive handoff
- Archive-D6 final archive acceptance smoke
- safe_boundary

## 2. 新增命令

新增命令：

- python scripts/run_final_archive_acceptance_smoke.py

## 3. 输出字段

输出字段：

- status
- runner
- runner_version
- acceptance_summary
- deliverables
- components
- safe_boundary

## 4. 验收目标

Archive-D6 验收目标：

- P12 final delivery package summary status completed
- ready_for_p12_d10_archive_bridge_plan true
- archive docs all present true
- final archive plan present true
- immutable delivery snapshot checklist present true
- final release note present true
- final archive manifest present true
- final operator archive handoff present true
- final archive acceptance smoke present true
- safe_boundary ok true
- ready_for_archive_d7_closeout true

## 5. 最终归档命令

最终归档验收命令：

- python main.py
- python scripts/run_p12_final_delivery_package_summary.py
- python scripts/run_final_archive_acceptance_smoke.py
- python -m pytest -q

通过标准：

- events_recorded: 8
- status completed
- ready_for_p12_d10_archive_bridge_plan true
- ready_for_archive_d7_closeout true
- pytest 全部 passed

## 6. 失败停止规则

如果 final archive acceptance smoke failed：

- 立即停止
- 不进入 Archive-D7
- 不进入归档状态
- 不解释为交易信号
- 不连接真实交易所
- 不配置 API key
- 不读取钱包私钥
- 不尝试真实下单
- 不删除测试绕过失败
- 不修改 safe_boundary 绕过失败
- 不绕过人工复核
- 不绕过 policy / risk / safe_boundary
- 回到 docs/94_p10_failure_triage_guide.md

## 7. Final Archive 安全边界

Archive-D6 不接真实交易所 API。
Archive-D6 不保存真实 API key。
Archive-D6 不读取钱包私钥。
Archive-D6 不真实下单。
Archive-D6 不读取真实账户余额。
Archive-D6 不读取真实仓位。
Archive-D6 不声明真实成交。
Archive-D6 不声明真实资金影响。
Archive-D6 不配置 CI secret。
Archive-D6 不做 production deployment。
Archive-D6 不自动实盘交易。
Archive-D6 不自动绕过人工复核。
Archive-D6 不绕过 policy / risk / safe_boundary。
Archive-D6 不把 paper-only passed 解释成真实交易信号。
Archive-D6 不把 paper-only passed 解释成真实成交。

下一步：

Archive-D7：final archive closeout。
