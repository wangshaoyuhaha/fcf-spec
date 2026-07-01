# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

当前不是足球系统。
当前不是 BTC-only。

BTC / crypto 只是资产类别之一，不是项目终点。

当前系统仍然是本地安全受控开发版本。
当前系统不接真实交易所 API。
当前系统不保存真实 API key。
当前系统不读取钱包私钥。
当前系统不真实下单。

## 当前阶段

Phase 1 Build Spine 已完成。
D1-D11 已完成。

Phase 2 多资产 MarketContext 基础层已完成。
P2-D1 到 P2-D10 已完成。

Phase 3 数据接入与 Dify integration 已完成阶段收尾。
P3-D1 到 P3-D14 已完成。

Phase 4 schema hardening 与 multi-asset fixture expansion 已完成阶段收尾。
P4-D1 到 P4-D13 已完成。

Phase 5 paper-only sandbox execution 已完成阶段收尾。
P5-D1 到 P5-D12 已完成。

Phase 6 policy / risk deny hardening 已完成阶段收尾。
P6-D1 到 P6-D12 已完成。

Phase 7 guarded paper execution 第一轮已完成阶段收尾。
P7-D1 到 P7-D7 已完成。

## Phase 7 已完成范围

P7-D1：multi-asset guarded paper execution fixture plan，已完成。
P7-D2：multi-asset guarded paper execution fixture，已完成。
P7-D3：multi-asset guarded paper execution smoke runner，已完成。
P7-D4：Dify response integration for guarded paper fixture smoke，已完成。
P7-D5：guarded paper execution phase acceptance，已完成。
P7-D6：guarded paper execution acceptance smoke runner，已完成。
P7-D7：Phase 7 closeout / project state consolidation，已完成。

## 当前关键能力

当前系统已经具备：

- raw market input schema
- schema error catalog
- market input pipeline schema integration
- local_market_input_api
- dify_http_adapter
- dify_response_templates
- multi-asset fixture
- multi-asset Dify success smoke
- multi-asset Dify error smoke
- paper order schema
- sandbox execution engine
- sandbox execution EventStore / Replay integration
- paper execution API wrapper
- Dify paper execution local adapter
- paper execution user-facing response templates
- Dify paper execution smoke runner
- Dify paper execution response integration smoke
- paper execution policy gate
- policy gate API integration
- paper_policy_deny user-facing response
- policy deny response smoke coverage
- paper execution risk guardian
- risk guardian API integration
- paper_risk_deny user-facing response
- risk deny response smoke coverage
- multi-asset guarded paper execution fixture
- multi-asset guarded paper execution smoke runner
- multi-asset guarded paper execution Dify response smoke
- P7 guarded paper execution acceptance smoke runner

## 当前 guarded paper execution 覆盖

资产类别：

- crypto
- equities
- fx
- commodities

guarded 分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

用户响应类型：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny

## 当前 paper execution API 顺序

当前 paper execution API 顺序：

1. evaluate_paper_execution_policy
2. evaluate_paper_execution_risk
3. execute_sandbox_order_with_eventstore

PolicyDeny / RiskDeny 都直接返回 ok=false。
PolicyDeny / RiskDeny 都不进入 sandbox execution。
PolicyDeny / RiskDeny 都不生成 sandbox execution event。
PolicyDeny / RiskDeny 都不真实下单。

## 当前关键文件

Phase 7 关键文件：

- docs/61_p7_multi_asset_guarded_paper_execution_fixture_plan.md
- docs/62_p7_multi_asset_guarded_paper_execution_fixture.md
- docs/63_p7_multi_asset_guarded_paper_execution_smoke_runner.md
- docs/64_p7_guarded_paper_execution_dify_response_smoke.md
- docs/65_p7_guarded_paper_execution_acceptance.md
- docs/66_p7_guarded_paper_execution_acceptance_smoke_runner.md
- docs/67_p7_closeout_project_state.md
- fixtures/paper_orders_multi_asset_guarded.json
- scripts/run_multi_asset_guarded_paper_execution_smoke.py
- scripts/run_multi_asset_guarded_paper_execution_response_smoke.py
- scripts/run_p7_guarded_paper_execution_acceptance_smoke.py
- tests/test_multi_asset_guarded_paper_fixture.py
- tests/test_multi_asset_guarded_paper_execution_smoke_runner.py
- tests/test_multi_asset_guarded_paper_execution_response_smoke.py
- tests/test_p7_guarded_paper_execution_acceptance.py
- tests/test_p7_guarded_paper_execution_acceptance_smoke.py
- tests/test_p7_closeout_project_state.py

## 当前验证命令

python main.py

预期输出：

- events_recorded: 8

python scripts/run_dify_http_adapter_smoke.py

预期输出：

- status completed

python scripts/run_dify_integration_smoke.py

预期输出：

- status completed

python scripts/run_multi_asset_dify_smoke.py

预期输出：

- status completed

python scripts/run_multi_asset_error_dify_smoke.py

预期输出：

- status completed

python scripts/run_dify_paper_execution_smoke.py

预期输出：

- status completed

python scripts/run_dify_paper_execution_response_smoke.py

预期输出：

- status completed

python scripts/run_multi_asset_guarded_paper_execution_smoke.py

预期输出：

- status completed

python scripts/run_multi_asset_guarded_paper_execution_response_smoke.py

预期输出：

- status completed

python scripts/run_p7_guarded_paper_execution_acceptance_smoke.py

预期输出：

- status completed

python -m pytest -q

预期输出：

- 283 passed 左右

## 安全边界

Dify 不作为底层交易内核。
Dify 不直接接真实交易所 API。
Dify 不保存真实交易所 API key。
Dify 不读取钱包私钥。
Dify 不真实下单。
Dify 只调用受控 API wrapper / pipeline。
不允许绕过 policy / risk。
不把 paper execution 伪装成 real execution。

sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
PolicyDeny 不是交易所真实拒单。
RiskDeny 不是交易所真实拒单。

## 下一步任务

进入 P7-D8：post-closeout guarded paper execution regression summary。

建议目标：

- 新增 regression summary runner 或文档
- 汇总 Phase 7 第一轮所有 smoke runner 输出
- 为后续 Phase 8 做准备
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 执行 git rev-parse --short HEAD 后填写
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成，D1-D11 已完成。Phase 2 多资产 MarketContext 基础层已完成，P2-D1 到 P2-D10 已完成。Phase 3 数据接入与 Dify integration 已完成阶段收尾，P3-D1 到 P3-D14 已完成。Phase 4 schema hardening 与 multi-asset fixture expansion 已完成阶段收尾，P4-D1 到 P4-D13 已完成。Phase 5 paper-only sandbox execution 已完成阶段收尾，P5-D1 到 P5-D12 已完成。Phase 6 policy / risk deny hardening 已完成阶段收尾，P6-D1 到 P6-D12 已完成。Phase 7 guarded paper execution 第一轮已完成阶段收尾，P7-D1 到 P7-D7 已完成。当前不是足球系统，也不是 BTC-only。
当前覆盖：crypto / equities / fx / commodities；fill_success / sandbox_reject / policy_deny / risk_deny；paper_fill_success / paper_reject_success / paper_policy_deny / paper_risk_deny。
当前 paper execution API 顺序：evaluate_paper_execution_policy -> evaluate_paper_execution_risk -> execute_sandbox_order_with_eventstore。PolicyDeny / RiskDeny 都直接返回 ok=false，不进入 sandbox execution，不生成 sandbox execution event，不真实下单。
当前验证：python main.py 输出 events_recorded: 8；所有 Dify / multi-asset / paper execution / guarded paper execution smoke runner 均 status completed；python scripts/run_p7_guarded_paper_execution_acceptance_smoke.py 输出 status completed；python -m pytest -q 预计显示 283 passed 左右。
安全边界：Dify 不作为底层交易内核，不直接接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，只调用受控 API wrapper / pipeline，不允许绕过 policy / risk，不把 paper execution 伪装成 real execution。sandbox fill 不是真实成交，sandbox reject 不是交易所真实拒单，PolicyDeny / RiskDeny 都不是交易所真实拒单。
next_action: 进入 P7-D8：post-closeout guarded paper execution regression summary。新增 regression summary runner 或文档，汇总 Phase 7 第一轮所有 smoke runner 输出，为后续 Phase 8 做准备。不接真实交易所 API，不真实下单，不破坏测试。
要求：全程中文一步步指挥；命令必须是可直接复制的 Git Bash 格式；多行 cat 必须包含完整 EOF；每次重要更新都 commit 并 push，并更新新的续聊话术。


## P7-D8 完成记录

P7-D8：post-closeout guarded paper execution regression summary 已完成。

新增文件：

- docs/68_p7_guarded_paper_execution_regression_summary.md
- scripts/run_p7_guarded_paper_execution_regression_summary.py
- tests/test_p7_guarded_paper_execution_regression_summary.py

完成内容：

- 新增 P7 post-closeout regression summary runner
- 汇总 9 个 smoke runner
- 汇总 guarded execution smoke
- 汇总 guarded response smoke
- 汇总 P7 acceptance smoke
- 输出 smoke_results
- 输出 guarded_summary
- 输出 regression_summary
- 输出 safe_boundary
- 验证 smoke_count 为 9
- 验证 completed_count 为 9
- 验证 failed_count 为 0
- 验证 guarded execution 16 个 case 全部通过
- 验证 guarded response 16 个 case 全部通过
- 验证 ready_for_phase8_planning 为 true

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python scripts/run_multi_asset_guarded_paper_execution_smoke.py 输出 status completed
- python scripts/run_multi_asset_guarded_paper_execution_response_smoke.py 输出 status completed
- python scripts/run_p7_guarded_paper_execution_acceptance_smoke.py 输出 status completed
- python scripts/run_p7_guarded_paper_execution_regression_summary.py 输出 status completed
- python -m pytest -q 显示 289 passed 左右

下一步：

进入 P7-D9：Phase 7 to Phase 8 bridge plan。

建议目标：

- 新增 Phase 8 规划文档
- 明确 portfolio-level guarded paper execution 候选方向
- 明确 cross-asset exposure checks 候选方向
- 明确 regression CI entrypoint 候选方向
- 不接真实交易所 API
- 不真实下单
- 不破坏测试


## P7-D9 完成记录

P7-D9：Phase 7 to Phase 8 bridge plan 已完成。

新增文件：

- docs/69_p7_to_p8_bridge_plan.md
- tests/test_p7_to_p8_bridge_plan.py

完成内容：

- 新增 Phase 7 到 Phase 8 桥接规划
- 汇总 P7-D1 到 P7-D9
- 明确 Phase 8 建议主题为 Portfolio-level guarded paper execution
- 明确 portfolio-level guarded paper execution 候选方向
- 明确 cross-asset exposure checks 候选方向
- 明确 portfolio-level user-facing response 候选方向
- 明确 regression CI entrypoint 候选方向
- 明确 P8-D1 到 P8-D6 候选路线
- 明确 Phase 8 第一轮不做真实交易所 API、不真实下单、不保存真实 API key、不读取钱包私钥

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python scripts/run_multi_asset_guarded_paper_execution_smoke.py 输出 status completed
- python scripts/run_multi_asset_guarded_paper_execution_response_smoke.py 输出 status completed
- python scripts/run_p7_guarded_paper_execution_acceptance_smoke.py 输出 status completed
- python scripts/run_p7_guarded_paper_execution_regression_summary.py 输出 status completed
- python -m pytest -q 显示 296 passed 左右

下一步：

进入 P8-D1：Portfolio-level guarded paper execution plan。

建议目标：

- 新增 docs/70_p8_portfolio_guarded_paper_execution_plan.md
- 明确 portfolio-level 输入 / 输出 / 分支 / 安全边界
- 只做规划文档
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

