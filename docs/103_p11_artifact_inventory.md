# P11-D4 - Artifact Inventory and Ownership Map

P11-D4 新增 artifact inventory and ownership map。

新增文件：

- docs/103_p11_artifact_inventory.md
- tests/test_p11_artifact_inventory.py

## 1. 目的

该文档记录当前 FCF paper-only / non-production 系统的关键 artifact 清单与维护责任。

inventory_version = 0.1.0
phase = P11
day = P11-D4
status = active

该文档用于：

- release readiness
- operator handoff
- long-term maintainability
- regression stability review
- paper-only safety review

该文档不用于：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 钱包私钥读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. owner 角色

当前 owner 角色：

- owner = operator
- owner = maintainer
- owner = reviewer
- owner = safety_guardian

operator 负责：

- 运行命令
- 读取 status
- 读取 safe_boundary
- 识别 failed
- 停止错误流程

maintainer 负责：

- 修改代码
- 增加测试
- 更新 README.md
- 更新 PROJECT_STATE.md
- commit
- push

reviewer 负责：

- 检查 operator handoff package
- 检查 versioned run commands
- 检查 artifact inventory
- 检查 maintenance checklist

safety_guardian 负责：

- 检查 paper-only 声明
- 检查 safe_boundary
- 检查不接真实交易所 API
- 检查不真实下单
- 检查不绕过人工复核
- 检查不绕过 policy / risk / safe_boundary

## 3. Core docs artifacts

核心文档 artifacts：

- README.md | owner = maintainer | status = active
- PROJECT_STATE.md | owner = maintainer | status = active
- docs/100_p11_release_readiness_plan.md | owner = reviewer | status = active
- docs/101_p11_operator_handoff_package.md | owner = operator | status = active
- docs/102_p11_versioned_run_commands.md | owner = operator | status = active
- docs/103_p11_artifact_inventory.md | owner = maintainer | status = active

## 4. Phase 10 Dify-safe package artifacts

Phase 10 Dify-safe artifacts：

- docs/90_p10_dify_safe_paper_operations_plan.md | owner = reviewer | status = active
- docs/91_p10_global_regression_dify_adapter_contract.md | owner = maintainer | status = active
- docs/92_p10_operator_review_response_templates.md | owner = maintainer | status = active
- docs/93_p10_paper_only_operator_runbook.md | owner = operator | status = active
- docs/94_p10_failure_triage_guide.md | owner = operator | status = active
- docs/95_p10_dify_workflow_node_contract.md | owner = reviewer | status = active
- docs/96_p10_acceptance_smoke.md | owner = maintainer | status = active
- docs/97_p10_closeout_project_state.md | owner = reviewer | status = active
- docs/98_p10_post_closeout_dify_safe_package_summary.md | owner = reviewer | status = active
- docs/99_p10_to_p11_bridge_plan.md | owner = reviewer | status = active

## 5. Scripts artifacts

脚本 artifacts：

- scripts/run_all_smokes.py | owner = maintainer | status = active
- scripts/run_p9_global_regression_summary.py | owner = maintainer | status = active
- scripts/run_p10_acceptance_smoke.py | owner = maintainer | status = active
- scripts/run_p10_dify_safe_package_summary.py | owner = maintainer | status = active
- scripts/run_p7_guarded_paper_execution_regression_summary.py | owner = maintainer | status = active
- scripts/run_portfolio_guarded_paper_execution_smoke.py | owner = maintainer | status = active

## 6. API artifacts

API artifacts：

- fcf/api/dify_global_regression_api.py | owner = maintainer | status = active
- fcf/api/operator_review_response_templates.py | owner = maintainer | status = active
- fcf/api/portfolio_paper_execution_api.py | owner = maintainer | status = active
- fcf/api/portfolio_paper_execution_response_templates.py | owner = maintainer | status = active

## 7. Regression artifacts

Regression artifacts：

- fcf/regression/global_regression_report_schema.py | owner = maintainer | status = active
- fcf/regression/global_safe_boundary_checker.py | owner = safety_guardian | status = active
- fcf/regression/project_state_consistency_checker.py | owner = safety_guardian | status = active

## 8. Policy / fixture artifacts

Policy and fixture artifacts：

- fcf/policy/portfolio_risk_guardian.py | owner = safety_guardian | status = active
- fixtures/paper_order_portfolios_multi_asset.json | owner = maintainer | status = active
- fixtures/paper_orders_multi_asset_guarded.json | owner = maintainer | status = active

## 9. Test artifacts

Test artifacts：

- tests/test_p11_release_readiness_plan.py | owner = maintainer | status = active
- tests/test_p11_operator_handoff_package.py | owner = maintainer | status = active
- tests/test_p11_versioned_run_commands.py | owner = maintainer | status = active
- tests/test_p11_artifact_inventory.py | owner = maintainer | status = active
- tests/test_p10_dify_safe_package_summary.py | owner = maintainer | status = active
- tests/test_p10_acceptance_smoke.py | owner = maintainer | status = active

## 10. Artifact maintenance rules

artifact 维护规则：

- 新增 artifact 必须写入 inventory
- 修改 artifact 必须更新对应测试
- 删除 artifact 必须标记 deprecated
- deprecated artifact 必须说明替代 artifact
- README.md 和 PROJECT_STATE.md 必须同步更新
- 每次变更必须运行 python -m pytest -q
- 每次阶段完成必须 commit
- 每次阶段完成必须 push
- 不允许删除安全边界
- 不允许删除 failed 停止规则
- 不允许绕过测试

## 11. 安全边界

P11-D4 不接真实交易所 API。
P11-D4 不保存真实 API key。
P11-D4 不读取钱包私钥。
P11-D4 不真实下单。
P11-D4 不读取真实账户余额。
P11-D4 不读取真实仓位。
P11-D4 不声明真实成交。
P11-D4 不声明真实资金影响。
P11-D4 不配置 CI secret。
P11-D4 不做 production deployment。
P11-D4 不自动实盘交易。
P11-D4 不自动绕过人工复核。
P11-D4 不绕过 policy / risk / safe_boundary。
P11-D4 不把 paper-only passed 解释成真实交易信号。
P11-D4 不把 paper-only passed 解释成真实成交。

## 12. P11-D4 验收标准

P11-D4 完成需要满足：

- 新增 docs/103_p11_artifact_inventory.md
- 新增 tests/test_p11_artifact_inventory.py
- 文档明确 inventory_version
- 文档明确 owner 角色
- 文档明确 core docs artifacts
- 文档明确 Phase 10 Dify-safe package artifacts
- 文档明确 scripts artifacts
- 文档明确 API artifacts
- 文档明确 regression artifacts
- 文档明确 policy / fixture artifacts
- 文档明确 test artifacts
- 文档明确 artifact maintenance rules
- 文档明确安全边界
- python main.py 输出 events_recorded: 8
- python scripts/run_p10_dify_safe_package_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P11-D5：maintenance checklist。
