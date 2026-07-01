# P7-D6 - Guarded Paper Execution Acceptance Smoke Runner

## 1. 目的

P7-D6 新增 guarded paper execution acceptance smoke runner。

该 runner 汇总 P7-D2 到 P7-D5 的验收结果：

- P7-D2 multi-asset guarded paper execution fixture
- P7-D3 multi-asset guarded paper execution smoke runner
- P7-D4 guarded paper execution Dify response smoke
- P7-D5 guarded paper execution phase acceptance

## 2. 新增文件

- scripts/run_p7_guarded_paper_execution_acceptance_smoke.py
- tests/test_p7_guarded_paper_execution_acceptance_smoke.py

## 3. 验收汇总内容

runner 输出：

- status
- runner
- acceptance_summary
- artifact_checks
- execution_smoke_summary
- response_smoke_summary
- safe_boundary

acceptance_summary 包含：

- p7_d2_fixture_complete
- p7_d3_execution_smoke_complete
- p7_d4_response_smoke_complete
- p7_d5_acceptance_doc_complete
- case_count
- asset_class_count
- branch_count
- response_type_count

## 4. 安全边界

P7-D6 不接真实交易所 API。
P7-D6 不保存真实 API key。
P7-D6 不读取钱包私钥。
P7-D6 不真实下单。
P7-D6 不允许绕过 policy / risk。
P7-D6 不把 paper execution 伪装成 real execution。

sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
PolicyDeny 不是交易所真实拒单。
RiskDeny 不是交易所真实拒单。

## 5. 验收标准

P7-D6 完成需要满足：

- 新增 acceptance smoke runner
- runner 输出 status completed
- runner 检查 P7-D2 到 P7-D5 关键 artifact 存在
- runner 汇总 execution smoke
- runner 汇总 response smoke
- runner 汇总 paper-only safe boundary
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 输出 status completed
- python -m pytest -q 通过

