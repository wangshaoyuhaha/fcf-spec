# P12-D5 - Final Artifact Manifest

P12-D5 新增 final artifact manifest。

新增文件：

- docs/114_p12_final_artifact_manifest.md
- tests/test_p12_final_artifact_manifest.py

## 1. 目的

该文档是 FCF paper-only / non-production delivery package 的最终 artifact manifest。

final_artifact_manifest_version = 0.1.0
manifest_mode = non_production
paper_only = true
phase = P12
day = P12-D5
status = active

该 manifest 用于：

- final non-production delivery
- archive readiness review
- documentation hardening review
- operator handoff review
- release readiness review
- regression stability review

该 manifest 不用于：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 钱包私钥读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. Owner / status 规则

owner 角色：

- owner = operator
- owner = maintainer
- owner = reviewer
- owner = safety_guardian

status 类型：

- status = active
- status = deprecated
- status = planned

manifest 规则：

- 每个 final artifact 必须有 path
- 每个 final artifact 必须有 owner
- 每个 final artifact 必须有 status
- deprecated artifact 必须说明 replacement artifact
- planned artifact 必须说明 planned phase
- 新增 artifact 必须同步 README.md
- 新增 artifact 必须同步 PROJECT_STATE.md
- 新增 artifact 必须增加测试

## 3. Docs manifest

docs artifacts：

- README.md | owner = maintainer | status = active
- PROJECT_STATE.md | owner = maintainer | status = active
- docs/93_p10_paper_only_operator_runbook.md | owner = operator | status = active
- docs/94_p10_failure_triage_guide.md | owner = operator | status = active
- docs/95_p10_dify_workflow_node_contract.md | owner = reviewer | status = active
- docs/100_p11_release_readiness_plan.md | owner = reviewer | status = active
- docs/101_p11_operator_handoff_package.md | owner = operator | status = active
- docs/102_p11_versioned_run_commands.md | owner = operator | status = active
- docs/103_p11_artifact_inventory.md | owner = maintainer | status = active
- docs/104_p11_maintenance_checklist.md | owner = maintainer | status = active
- docs/105_p11_regression_stability_gate.md | owner = reviewer | status = active
- docs/106_p11_acceptance_smoke.md | owner = maintainer | status = active
- docs/107_p11_closeout_project_state.md | owner = reviewer | status = active
- docs/108_p11_post_closeout_release_readiness_package_summary.md | owner = reviewer | status = active
- docs/109_p11_to_p12_bridge_plan.md | owner = reviewer | status = active
- docs/110_p12_documentation_hardening_plan.md | owner = reviewer | status = active
- docs/111_p12_final_non_production_delivery_package.md | owner = reviewer | status = active
- docs/112_p12_archive_readiness_checklist.md | owner = reviewer | status = active
- docs/113_p12_final_command_index.md | owner = operator | status = active
- docs/114_p12_final_artifact_manifest.md | owner = maintainer | status = active

## 4. Scripts manifest

scripts artifacts：

- scripts/run_all_smokes.py | owner = maintainer | status = active
- scripts/run_p9_global_regression_summary.py | owner = maintainer | status = active
- scripts/run_p10_acceptance_smoke.py | owner = maintainer | status = active
- scripts/run_p10_dify_safe_package_summary.py | owner = maintainer | status = active
- scripts/run_p11_acceptance_smoke.py | owner = maintainer | status = active
- scripts/run_p11_release_readiness_package_summary.py | owner = maintainer | status = active
- scripts/run_p7_guarded_paper_execution_regression_summary.py | owner = maintainer | status = active
- scripts/run_portfolio_guarded_paper_execution_smoke.py | owner = maintainer | status = active

## 5. API manifest

api artifacts：

- fcf/api/dify_global_regression_api.py | owner = maintainer | status = active
- fcf/api/operator_review_response_templates.py | owner = maintainer | status = active
- fcf/api/portfolio_paper_execution_api.py | owner = maintainer | status = active
- fcf/api/portfolio_paper_execution_response_templates.py | owner = maintainer | status = active
- fcf/api/local_market_input_api.py | owner = maintainer | status = active
- fcf/api/dify_http_adapter.py | owner = maintainer | status = active

## 6. Regression manifest

regression artifacts：

- fcf/regression/global_regression_report_schema.py | owner = maintainer | status = active
- fcf/regression/global_safe_boundary_checker.py | owner = safety_guardian | status = active
- fcf/regression/project_state_consistency_checker.py | owner = safety_guardian | status = active
- fcf/regression/regression_stability_gate.py | owner = safety_guardian | status = active

## 7. Policy manifest

policy artifacts：

- fcf/policy/portfolio_risk_guardian.py | owner = safety_guardian | status = active

## 8. Fixtures manifest

fixtures artifacts：

- fixtures/paper_order_portfolios_multi_asset.json | owner = maintainer | status = active
- fixtures/paper_orders_multi_asset_guarded.json | owner = maintainer | status = active
- fixtures/multi_asset_market_inputs.json | owner = maintainer | status = active

## 9. Tests manifest

tests artifacts：

- tests/test_p11_release_readiness_plan.py | owner = maintainer | status = active
- tests/test_p11_operator_handoff_package.py | owner = maintainer | status = active
- tests/test_p11_versioned_run_commands.py | owner = maintainer | status = active
- tests/test_p11_artifact_inventory.py | owner = maintainer | status = active
- tests/test_p11_maintenance_checklist.py | owner = maintainer | status = active
- tests/test_p11_regression_stability_gate.py | owner = maintainer | status = active
- tests/test_p11_acceptance_smoke.py | owner = maintainer | status = active
- tests/test_p11_closeout_project_state.py | owner = maintainer | status = active
- tests/test_p11_release_readiness_package_summary.py | owner = maintainer | status = active
- tests/test_p11_to_p12_bridge_plan.py | owner = maintainer | status = active
- tests/test_p12_documentation_hardening_plan.py | owner = maintainer | status = active
- tests/test_p12_final_non_production_delivery_package.py | owner = maintainer | status = active
- tests/test_p12_archive_readiness_checklist.py | owner = maintainer | status = active
- tests/test_p12_final_command_index.py | owner = maintainer | status = active
- tests/test_p12_final_artifact_manifest.py | owner = maintainer | status = active

## 10. Planned final artifacts

planned artifacts：

- docs/115_p12_final_safety_boundary_declaration.md | owner = safety_guardian | status = planned | planned phase = P12-D6
- docs/116_p12_final_operator_delivery_note.md | owner = operator | status = planned | planned phase = P12-D7
- docs/117_p12_acceptance_smoke.md | owner = reviewer | status = planned | planned phase = P12-D7
- scripts/run_p12_acceptance_smoke.py | owner = maintainer | status = planned | planned phase = P12-D7
- docs/118_p12_closeout_project_state.md | owner = reviewer | status = planned | planned phase = P12-D8

## 11. Deprecated artifact rule

当前无 deprecated artifact。

如后续出现 deprecated artifact，必须写明：

- deprecated artifact path
- replacement artifact path
- deprecated reason
- deprecated phase
- safe removal status

deprecated 不允许用于绕过测试。
deprecated 不允许用于删除安全边界。
deprecated 不允许用于删除 failed 停止规则。

## 12. Archive readiness linkage

该 manifest 与以下文档共同构成归档准备基础：

- docs/111_p12_final_non_production_delivery_package.md
- docs/112_p12_archive_readiness_checklist.md
- docs/113_p12_final_command_index.md
- docs/114_p12_final_artifact_manifest.md

归档前必须确认：

- final non-production delivery package exists
- archive readiness checklist exists
- final command index exists
- final artifact manifest exists
- P11 release readiness package summary completed
- ready_for_p11_d10_bridge_plan true
- pytest 全部 passed
- git status --short 干净
- commit 已完成
- push 已完成

## 13. Final safety boundary

最终 artifact manifest 必须继续声明：

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

## 14. P12-D5 验收标准

P12-D5 完成需要满足：

- 新增 docs/114_p12_final_artifact_manifest.md
- 新增 tests/test_p12_final_artifact_manifest.py
- 文档明确 final_artifact_manifest_version
- 文档明确 owner / status 规则
- 文档明确 docs manifest
- 文档明确 scripts manifest
- 文档明确 api manifest
- 文档明确 regression manifest
- 文档明确 policy manifest
- 文档明确 fixtures manifest
- 文档明确 tests manifest
- 文档明确 planned final artifacts
- 文档明确 deprecated artifact rule
- 文档明确 archive readiness linkage
- 文档明确 final safety boundary
- P11 release readiness package summary 仍然 completed
- ready_for_p11_d10_bridge_plan 仍然 true
- python main.py 输出 events_recorded: 8
- python scripts/run_p11_release_readiness_package_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

P12-D6：final safety boundary declaration。
