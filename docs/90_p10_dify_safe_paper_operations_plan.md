# P10-D1 - Dify-safe Paper Operations Plan

P10-D1 启动 Phase 10。

Phase 10 主题：

Dify-safe paper operations packaging and operator review readiness。

中文含义：

Dify 安全纸面操作封装与人工复核准备。

P10-D1 只做规划文档。
P10-D1 不改核心执行逻辑。
P10-D1 不接真实交易所 API。
P10-D1 不保存真实 API key。
P10-D1 不读取钱包私钥。
P10-D1 不真实下单。
P10-D1 不读取真实账户余额。
P10-D1 不读取真实仓位。
P10-D1 不声明真实成交。
P10-D1 不声明真实资金影响。
P10-D1 不配置 CI secret。
P10-D1 不做 production deployment。
P10-D1 不自动实盘交易。
P10-D1 不自动绕过人工复核。
P10-D1 不绕过 policy / risk / safe_boundary。

## 当前基础

当前已完成：

- Phase 7 guarded paper execution regression summary
- Phase 8 portfolio guarded paper execution regression summary
- Phase 9 global paper-only regression suite
- run_all_smokes
- run_p9_acceptance_smoke
- run_p9_global_regression_summary
- build_global_regression_report
- check_global_safe_boundary
- check_project_state_consistency

## Phase 10 目标

Phase 10 第一轮目标：

- Dify-safe global regression adapter
- operator review response templates
- paper-only operator runbook
- failure triage guide
- Dify workflow node contract document
- handoff package for non-production paper-only use
- Phase 10 acceptance smoke

## Dify-safe global regression adapter 规划

建议新增：

- fcf/api/dify_global_regression_api.py

入口建议：

- handle_dify_global_regression_request

输入建议：

- request_id
- operator_id
- review_mode
- requested_checks
- output_format

输出建议：

- ok
- api
- api_version
- error
- data
- safe_boundary

该 adapter 只允许调用现有 paper-only regression runner。
该 adapter 不允许接真实交易所。
该 adapter 不允许读取真实账户余额。
该 adapter 不允许读取真实仓位。
该 adapter 不允许触发真实订单。

## Operator review response templates 规划

建议新增：

- fcf/api/operator_review_response_templates.py

覆盖响应：

- global_regression_passed
- global_regression_failed
- safe_boundary_failed
- project_state_inconsistent
- operator_review_required

所有响应必须明确：

- 这是 paper-only / non-production 响应
- 不是真实交易信号
- 不是真实下单结果
- 不是真实成交结果
- 需要人工复核

## Paper-only operator runbook 规划

建议新增：

- docs/91_p10_paper_only_operator_runbook.md

内容建议：

- 如何运行 python scripts/run_all_smokes.py
- 如何运行 python scripts/run_p9_acceptance_smoke.py
- 如何运行 python scripts/run_p9_global_regression_summary.py
- 如何读取 status
- 如何读取 safe_boundary
- 如何处理 failed
- 如何确认没有真实交易所连接

## Failure triage guide 规划

建议新增：

- docs/92_p10_failure_triage_guide.md

覆盖：

- pytest failed
- smoke failed
- safe_boundary failed
- project state consistency failed
- Dify adapter input invalid
- response template mismatch

## Dify workflow node contract 规划

建议新增：

- docs/93_p10_dify_workflow_node_contract.md

节点建议：

- Input validation node
- Global regression API node
- Safe boundary review node
- Operator response template node
- Human review node
- Final non-production output node

Dify 节点不允许：

- 真实交易所 API key
- 钱包私钥
- 真实账户凭证
- 自动实盘下单
- 绕过人工复核
- 绕过 policy / risk / safe_boundary

## Phase 10 第一轮路线

P10-D1：Dify-safe paper operations plan。

P10-D2：global regression Dify adapter contract。

P10-D3：operator review response templates。

P10-D4：paper-only operator runbook。

P10-D5：failure triage guide。

P10-D6：Dify workflow node contract document。

P10-D7：Phase 10 acceptance smoke。

P10-D8：Phase 10 closeout。

## P10-D1 验收标准

P10-D1 完成需要满足：

- 新增 docs/90_p10_dify_safe_paper_operations_plan.md
- 新增 tests/test_p10_dify_safe_paper_operations_plan.py
- 文档明确 Phase 10 主题
- 文档明确 Dify-safe global regression adapter
- 文档明确 operator review response templates
- 文档明确 paper-only operator runbook
- 文档明确 failure triage guide
- 文档明确 Dify workflow node contract
- 文档明确 P10-D1 到 P10-D8 路线
- P9 global regression summary 仍然 completed
- ready_for_phase10_planning 仍然 true
- python main.py 输出 events_recorded: 8
- python scripts/run_p9_global_regression_summary.py 输出 status completed
- python -m pytest -q 通过

下一步：

进入 P10-D2：global regression Dify adapter contract。
