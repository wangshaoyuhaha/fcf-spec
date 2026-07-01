# P11-D3 - Versioned Run Commands Document

P11-D3 新增 versioned run commands document。

新增文件：

- docs/102_p11_versioned_run_commands.md
- tests/test_p11_versioned_run_commands.py

## 1. 目的

该文档记录当前 FCF paper-only / non-production 系统的版本化运行命令。

命令清单版本：

- command_profile_version = 0.1.0
- phase = P11
- day = P11-D3
- status = active

该文档用于：

- operator handoff
- release readiness
- regression stability review
- long-term maintenance

该文档不用于：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 钱包私钥读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. 本地完整回归命令 profile

profile name：

- local_full_regression

命令：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_acceptance_smoke.py
- python scripts/run_p10_dify_safe_package_summary.py
- python -m pytest -q

通过标准：

- python main.py 输出 events_recorded: 8
- python scripts/run_all_smokes.py 输出 status completed
- python scripts/run_p9_global_regression_summary.py 输出 status completed
- python scripts/run_p10_acceptance_smoke.py 输出 status completed
- python scripts/run_p10_dify_safe_package_summary.py 输出 status completed
- python -m pytest -q 全部 passed

## 3. CI-safe 回归命令 profile

profile name：

- ci_safe_regression

命令：

- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_acceptance_smoke.py
- python scripts/run_p10_dify_safe_package_summary.py
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

## 4. Dify-safe paper review 命令 profile

profile name：

- dify_safe_paper_review

代码入口：

- handle_dify_global_regression_request
- render_operator_review_response

允许输入：

- review_mode = paper_only
- review_mode = operator_review
- review_mode = non_production_review
- requested_checks = all_smokes
- requested_checks = global_report
- requested_checks = safe_boundary
- requested_checks = project_state_consistency
- output_format = json

通过标准：

- ok true
- ready_for_operator_review true
- operator_review_required true
- response_type = global_regression_passed
- safe_boundary.real_execution = false
- safe_boundary.real_exchange_api = false
- safe_boundary.bypass_operator_review = false
- safe_boundary.bypass_policy_risk_safe_boundary = false

## 5. 失败排查命令 profile

profile name：

- failure_triage

参考文档：

- docs/94_p10_failure_triage_guide.md

优先命令：

- python -m pytest -q
- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_acceptance_smoke.py
- python scripts/run_p10_dify_safe_package_summary.py

失败处理：

- 停止继续操作
- 不进入下一阶段
- 不解释为交易信号
- 不连接真实交易所
- 不配置 API key
- 不读取钱包私钥
- 不尝试真实下单
- 不删除测试绕过失败
- 不修改 safe_boundary 绕过失败

## 6. 命令维护规则

每次新增命令必须：

- 写入 README.md
- 写入 PROJECT_STATE.md
- 写入对应 docs 文件
- 增加测试
- 运行 python -m pytest -q
- commit
- push

每次废弃命令必须：

- 保留历史说明
- 标记 deprecated
- 说明替代命令
- 不删除安全边界
- 不删除 failed 停止规则

## 7. 安全边界

P11-D3 不接真实交易所 API。
P11-D3 不保存真实 API key。
P11-D3 不读取钱包私钥。
P11-D3 不真实下单。
P11-D3 不读取真实账户余额。
P11-D3 不读取真实仓位。
P11-D3 不声明真实成交。
P11-D3 不声明真实资金影响。
P11-D3 不配置 CI secret。
P11-D3 不做 production deployment。
P11-D3 不自动实盘交易。
P11-D3 不自动绕过人工复核。
P11-D3 不绕过 policy / risk / safe_boundary。
P11-D3 不把 paper-only passed 解释成真实交易信号。
P11-D3 不把 paper-only passed 解释成真实成交。

## 8. P11-D3 验收标准

P11-D3 完成需要满足：

- 新增 docs/102_p11_versioned_run_commands.md
- 新增 tests/test_p11_versioned_run_commands.py
- 文档明确 command_profile_version
- 文档明确 local_full_regression profile
- 文档明确 ci_safe_regression profile
- 文档明确 dify_safe_paper_review profile
- 文档明确 failure_triage profile
- 文档明确命令维护规则
- 文档明确安全边界
- python main.py 输出 events_recorded: 8
- python scripts/run_p10_dify_safe_package_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P11-D4：artifact inventory and ownership map。
