# P11-D2 - Operator Handoff Package

P11-D2 新增 operator handoff package document。

新增文件：

- docs/101_p11_operator_handoff_package.md
- tests/test_p11_operator_handoff_package.py

## 1. 交接目的

该文档用于把当前 FCF paper-only / non-production 系统交接给 operator。

operator 接手范围：

- 运行本地回归命令
- 读取 smoke / regression status
- 读取 safe_boundary
- 调用 Dify-safe adapter
- 阅读 operator review response
- 识别 failed
- 停止错误流程
- 维护 README.md / PROJECT_STATE.md 一致性

operator 不接手：

- 真实交易所 API
- 真实下单
- 真实账户余额读取
- 真实仓位读取
- 钱包私钥读取
- CI secret 配置
- production deployment
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. 当前系统定位

当前系统是：

- paper-only
- non-production
- multi-asset event system
- Dify-safe operator review package
- regression-first validation package

当前系统不是：

- 不是真实交易系统
- 实盘下单系统
- 真实成交系统
- 真实资金管理系统
- 真实交易信号系统
- 自动实盘交易机器人

## 3. operator 必跑命令

本地完整回归命令：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_acceptance_smoke.py
- python scripts/run_p10_dify_safe_package_summary.py
- python -m pytest -q

通过标准：

- python main.py 输出 events_recorded: 8
- run_all_smokes 输出 status completed
- run_p9_global_regression_summary 输出 status completed
- run_p10_acceptance_smoke 输出 status completed
- run_p10_dify_safe_package_summary 输出 status completed
- python -m pytest -q 全部 passed

## 4. Dify-safe operator review 入口

Dify-safe API wrapper：

- fcf/api/dify_global_regression_api.py
- handle_dify_global_regression_request

Operator response template：

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

## 5. operator response 读取规则

允许 response_type：

- global_regression_passed
- global_regression_failed
- safe_boundary_failed
- project_state_inconsistent
- operator_review_required

如果 response_type 是 global_regression_passed，只能说明：

- paper-only regression 通过
- safe_boundary 当前 ok
- project state 当前一致
- 可以进入人工复核

不能说明：

- 真实交易信号成立
- 真实下单成功
- 真实成交成功
- 真实资金发生变化
- 真实账户余额已读取
- 真实仓位已读取

## 6. 交接清单

operator 接手前必须确认：

- README.md 存在
- PROJECT_STATE.md 存在
- docs/100_p11_release_readiness_plan.md 存在
- docs/101_p11_operator_handoff_package.md 存在
- scripts/run_all_smokes.py 存在
- scripts/run_p10_dify_safe_package_summary.py 存在
- fcf/api/dify_global_regression_api.py 存在
- fcf/api/operator_review_response_templates.py 存在
- python -m pytest -q 通过

## 7. failed 停止规则

如果任何命令 failed：

- 立即停止
- 不进入下一阶段
- 不解释为交易信号
- 不连接真实交易所
- 不配置 API key
- 不读取钱包私钥
- 不尝试真实下单
- 不修改 safe_boundary 绕过失败
- 不删除测试绕过失败
- 回到 docs/94_p10_failure_triage_guide.md

## 8. 长期维护规则

operator 长期维护时必须：

- 每次变更后运行 python -m pytest -q
- 每次阶段完成后更新 README.md
- 每次阶段完成后更新 PROJECT_STATE.md
- 每次阶段完成后 commit
- 每次阶段完成后 push
- 保留安全边界
- 保留 paper-only 声明
- 保留 failed 停止规则

## 9. 安全边界

P11-D2 不接真实交易所 API。
P11-D2 不保存真实 API key。
P11-D2 不读取钱包私钥。
P11-D2 不真实下单。
P11-D2 不读取真实账户余额。
P11-D2 不读取真实仓位。
P11-D2 不声明真实成交。
P11-D2 不声明真实资金影响。
P11-D2 不配置 CI secret。
P11-D2 不做 production deployment。
P11-D2 不自动实盘交易。
P11-D2 不自动绕过人工复核。
P11-D2 不绕过 policy / risk / safe_boundary。
P11-D2 不把 paper-only passed 解释成真实交易信号。
P11-D2 不把 paper-only passed 解释成真实成交。

## 10. P11-D2 验收标准

P11-D2 完成需要满足：

- 新增 docs/101_p11_operator_handoff_package.md
- 新增 tests/test_p11_operator_handoff_package.py
- 文档明确 operator 接手范围
- 文档明确系统定位
- 文档明确必跑命令
- 文档明确 Dify-safe operator review 入口
- 文档明确 response_type 读取规则
- 文档明确交接清单
- 文档明确 failed 停止规则
- 文档明确长期维护规则
- python main.py 输出 events_recorded: 8
- python scripts/run_p10_dify_safe_package_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P11-D3：versioned run commands document。
