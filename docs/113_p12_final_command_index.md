# P12-D4 - Final Command Index

P12-D4 新增 final command index。

新增文件：

- docs/113_p12_final_command_index.md
- tests/test_p12_final_command_index.py

## 1. 目的

该文档是 FCF paper-only / non-production delivery package 的最终命令索引。

final_command_index_version = 0.1.0
command_index_mode = non_production
paper_only = true
phase = P12
day = P12-D4
status = active

该命令索引用于：

- local_full_regression
- ci_safe_regression
- dify_safe_paper_review
- release_readiness_review
- archive_readiness_review
- failure_triage

该命令索引不用于：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 钱包私钥读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. local_full_regression

用途：

本地完整回归。

命令：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_dify_safe_package_summary.py
- python scripts/run_p11_acceptance_smoke.py
- python scripts/run_p11_release_readiness_package_summary.py
- python -m pytest -q

通过标准：

- events_recorded: 8
- status completed
- ready_for_p11_d10_bridge_plan true
- pytest 全部 passed

## 3. ci_safe_regression

用途：

CI-safe 回归检查。

命令：

- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_dify_safe_package_summary.py
- python scripts/run_p11_acceptance_smoke.py
- python scripts/run_p11_release_readiness_package_summary.py
- python -m pytest -q

CI-safe 约束：

- 不需要 exchange API key
- 不需要 wallet private key
- 不需要 real account credentials
- 不需要 real broker credentials
- 不需要 CI secret
- 不需要 production deployment permission
- 不连接真实交易所
- 不真实下单

## 4. dify_safe_paper_review

用途：

Dify-safe paper-only operator review。

入口：

- fcf/api/dify_global_regression_api.py
- handle_dify_global_regression_request
- fcf/api/operator_review_response_templates.py
- render_operator_review_response

允许 review_mode：

- paper_only
- operator_review
- non_production_review

允许 requested_checks：

- all_smokes
- global_report
- safe_boundary
- project_state_consistency

允许 output_format：

- json

通过标准：

- ok true
- ready_for_operator_review true
- operator_review_required true
- response_type = global_regression_passed
- real_execution = false
- bypass_operator_review = false
- bypass_policy_risk_safe_boundary = false

## 5. release_readiness_review

用途：

发布准备复核。

命令：

- python scripts/run_p10_dify_safe_package_summary.py
- python scripts/run_p11_acceptance_smoke.py
- python scripts/run_p11_release_readiness_package_summary.py
- python -m pytest -q

通过标准：

- P10 package summary status completed
- P11 acceptance smoke status completed
- P11 release readiness package summary status completed
- ready_for_p11_d8_closeout true
- ready_for_p11_d10_bridge_plan true
- safe_boundary ok true
- pytest 全部 passed

## 6. archive_readiness_review

用途：

归档准备复核。

命令：

- python scripts/run_p11_release_readiness_package_summary.py
- python -m pytest -q

参考文档：

- docs/112_p12_archive_readiness_checklist.md
- docs/111_p12_final_non_production_delivery_package.md
- docs/103_p11_artifact_inventory.md

通过标准：

- archive_checklist_version = 0.1.0
- archive_mode = non_production
- paper_only = true
- ready_for_p11_d10_bridge_plan true
- git status --short 干净
- commit 已完成
- push 已完成

## 7. failure_triage

用途：

失败排查。

优先命令：

- python -m pytest -q
- python scripts/run_all_smokes.py
- python scripts/run_p10_dify_safe_package_summary.py
- python scripts/run_p11_acceptance_smoke.py
- python scripts/run_p11_release_readiness_package_summary.py

参考文档：

- docs/94_p10_failure_triage_guide.md

失败处理：

- 立即停止
- 不进入下一阶段
- 不进入归档状态
- 不解释为交易信号
- 不连接真实交易所
- 不配置 API key
- 不读取钱包私钥
- 不尝试真实下单
- 不删除测试绕过失败
- 不修改 safe_boundary 绕过失败
- 保留完整错误输出

## 8. command maintenance rules

命令维护规则：

- 新增命令必须写入 docs/113_p12_final_command_index.md
- 新增命令必须写入 README.md
- 新增命令必须写入 PROJECT_STATE.md
- 新增命令必须增加测试
- 修改命令必须同步修改对应文档
- 删除命令必须标记 deprecated
- deprecated 命令必须说明替代命令
- 每次修改必须运行 python -m pytest -q
- 每次阶段完成必须 commit
- 每次阶段完成必须 push
- 不允许删除安全边界
- 不允许删除 failed 停止规则
- 不允许绕过测试

## 9. final safety boundary

最终命令索引必须继续声明：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响
- 不配置 CI secret
- 不做 production deployment
- 不自动实盘交易
- 不自动绕过人工复核
- 不绕过 policy / risk / safe_boundary
- 不把 paper-only passed 解释成真实交易信号
- 不把 paper-only passed 解释成真实成交

## 10. P12-D4 验收标准

P12-D4 完成需要满足：

- 新增 docs/113_p12_final_command_index.md
- 新增 tests/test_p12_final_command_index.py
- 文档明确 final_command_index_version
- 文档明确 local_full_regression
- 文档明确 ci_safe_regression
- 文档明确 dify_safe_paper_review
- 文档明确 release_readiness_review
- 文档明确 archive_readiness_review
- 文档明确 failure_triage
- 文档明确 command maintenance rules
- 文档明确 final safety boundary
- P11 release readiness package summary 仍然 completed
- ready_for_p11_d10_bridge_plan 仍然 true
- python main.py 输出 events_recorded: 8
- python scripts/run_p11_release_readiness_package_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P12-D5：final artifact manifest。
