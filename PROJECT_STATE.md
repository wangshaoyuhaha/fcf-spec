# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。

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

## 当前关键能力

当前系统已经具备：

- FCFEvent
- EventStore
- ReplayEngine
- main.py 最小事件链
- 多资产 MarketContext 基础层
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

## Phase 5 已完成范围

P5-D1：Paper-only sandbox execution boundary plan，已完成。
P5-D2：paper order schema module，已完成。
P5-D3：sandbox execution engine skeleton，已完成。
P5-D4：sandbox execution EventStore and Replay integration，已完成。
P5-D5：paper execution API wrapper，已完成。
P5-D6：Dify paper execution contract and local adapter planning，已完成。
P5-D7：Dify paper execution local adapter，已完成。
P5-D8：Dify paper execution smoke runner，已完成。
P5-D9：paper execution user-facing response templates，已完成。
P5-D10：Dify paper execution response integration smoke，已完成。
P5-D11：Phase 5 paper execution acceptance，已完成。
P5-D12：Phase 5 closeout / project state consolidation，已完成。

## 当前关键代码

- fcf/schemas/raw_market_input_schema.py
- fcf/schemas/schema_error_catalog.py
- fcf/pipelines/market_input_pipeline.py
- fcf/api/local_market_input_api.py
- fcf/api/dify_http_adapter.py
- fcf/api/dify_response_templates.py
- fcf/paper/paper_order_schema.py
- fcf/paper/sandbox_execution_engine.py
- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py
- fcf/api/paper_execution_response_templates.py

## 当前关键 smoke runner

- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py
- scripts/run_multi_asset_dify_smoke.py
- scripts/run_multi_asset_error_dify_smoke.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

## 当前关键 fixture

- fixtures/raw_market_data_crypto.json
- fixtures/raw_market_data_multi_asset.json

## 当前关键文档

- docs/37_p5_paper_sandbox_execution_boundary_plan.md
- docs/38_p5_paper_order_schema_module.md
- docs/39_p5_sandbox_execution_engine_skeleton.md
- docs/40_p5_sandbox_execution_eventstore_replay.md
- docs/41_p5_paper_execution_api_wrapper.md
- docs/42_p5_dify_paper_execution_contract.md
- docs/43_p5_dify_paper_execution_local_adapter.md
- docs/44_p5_dify_paper_execution_smoke_runner.md
- docs/45_p5_paper_execution_user_facing_response_templates.md
- docs/46_p5_dify_paper_execution_response_smoke.md
- docs/47_p5_paper_execution_acceptance.md
- docs/48_p5_closeout_project_state.md

## 当前验证命令

python main.py

预期输出：

- events_recorded: 8

python scripts/run_dify_http_project_state.md

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

python -m pytest -q

预期输出：

- 186 passed

## 安全边界

Dify 不作为底层交易内核。
Dify 不直接接真实交易所 API。
Dify 不保存真实 API key。
Dify 不读取钱包私钥。
Dify 不真实下单。
Dify 只调用受控 API wrapper / pipeline。
Dify 不把 pipeline 成功伪装成真实交易成功。

当前系统不接真实交易所 API。
当前系统不保存真实 API key。
当前系统不读取钱包私钥。
当前系统不真实下单。

paper execution 只是 paper / sandbox。
sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
paper execution 不修改真实账户。
paper execution 不修改真实仓位。

## Phase 6 推荐方向

建议下一步进入：

P6-D1：Policy and risk deny case hardening plan。

目标：

- 新增 policy / risk deny case hardening 文档
- 明确 paper execution 也不能绕过 policy / risk
- 增加后续 deny case 测试规划
- 明确 Dify safety refusal 与 policy deny 的区别
- 明确 risk guardian deny 与 schema error 的区别
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 执行 git rev-parse --short HEAD 后填写
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成，D1-D11 已完成。Phase 2 多资产 MarketContext 基础层已完成，P2-D1 到 P2-D10 已完成。Phase 3 数据接入与 Dify integration 已完成阶段收尾，P3-D1 到 P3-D14 已完成。Phase 4 schema hardening 与 multi-asset fixture expansion 已完成阶段收尾，P4-D1 到 P4-D13 已完成。Phase 5 paper-only sandbox execution 已完成阶段收尾，P5-D1 到 P5-D12 已完成。当前不是足球系统，也不是 BTC-only。BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。
当前能力：raw market input schema、schema error catalog、market input pipeline schema integration、local_market_input_api、dify_http_adapter、dify_response_templates、multi-asset fixture、multi-asset Dify success smoke、multi-asset Dify error smoke、paper order schema、sandbox execution engine、sandbox execution EventStore / Replay integration、paper execution API wrapper、Dify paper execution local adapter、paper execution user-facing response templates、Dify paper execution smoke runner、Dify paper execution response integration smoke 均已完成。
当前验证：python main.py 输出 events_recorded: 8；python scripts/run_dify_http_adapter_smoke.py 输出 status completed；python scripts/run_dify_integration_smoke.py 输出 status completed；python scripts/run_multi_asset_dify_smoke.py 输出 status completed；python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed；python scripts/run_dify_paper_execution_smoke.py 输出 status completed；python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed；python -m pytest -q 预计显示 186 passed。
安全边界：Dify 不作为底层交易内核，不直接接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，只调用受控 API wrapper / pipeline，不把 paper execution 伪装成 real execution。sandbox fill 不是真实成交，sandbox reject 不是交易所真实拒单。
next_action: 进入 P6-D1：Policy and risk deny case hardening plan。新增 policy / risk deny case hardening 文档，明确 paper execution 也不能绕过 policy / risk，增加后续 deny case 测试规划，明确 Dify safety refusal 与 policy deny 的区别。不接真实交易所 API，不真实下单，不破坏测试。
要求：全程中文一步步指挥；命令必须是可直接复制的 Git Bash 格式；多行 cat 必须包含完整 EOF；每次重要更新都 commit 并 push，并更新新的续聊话术。成功后直接给下一步代码，不必等待用户说继续。


## P6-D1 完成记录

P6-D1：Policy and risk deny case hardening plan 已完成。

新增文件：

- docs/49_p6_policy_risk_deny_case_hardening_plan.md

完成内容：

- 明确 schema error 定义
- 明确 policy deny 定义
- 明确 risk deny 定义
- 明确 Dify safety refusal 定义
- 明确 deny case 优先级
- 明确后续事件类型
- 明确后续模块规划
- 明确 policy deny 候选规则
- 明确 risk deny 候选规则
- 明确 Dify 用户可见要求
- 明确测试规划
- 明确 P6-D2 下一步方向

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 186 passed

下一步：

进入 P6-D2：paper execution policy gate module。

建议新增：

- fcf/policy/paper_execution_policy.py
- tests/test_paper_execution_policy.py

P6-D2 目标：

- 定义 policy deny reason
- 实现 evaluate_paper_execution_policy
- 拒绝 real_execution_requested
- 拒绝 save_api_key_requested
- 拒绝 read_private_key_requested
- 拒绝 bypass_risk_requested
- 拒绝 force_execute_requested
- 拒绝 convert_paper_to_real_requested
- 返回稳定 decision dict
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P6-D2 完成记录

P6-D2：paper execution policy gate module 已完成。

新增文件：

- docs/50_p6_paper_execution_policy_gate.md
- fcf/policy/paper_execution_policy.py
- tests/test_paper_execution_policy.py

完成内容：

- 新增 describe_paper_execution_policy
- 新增 evaluate_paper_execution_policy
- 支持稳定 allowed decision dict
- 支持稳定 denied decision dict
- 支持检查 request 顶层字段
- 支持检查 request.metadata 字段
- 支持检查 raw_order 字段
- 支持检查 raw_order.metadata 字段
- 拒绝 real_execution_requested
- 拒绝 real_order
- 拒绝 real_exchange_api
- 拒绝 save_api_key_requested
- 拒绝 read_private_key_requested
- 拒绝 bypass_risk_requested
- 拒绝 force_execute_requested
- 拒绝 convert_paper_to_real_requested
- 拒绝 place_real_order_requested
- 拒绝 connect_exchange_requested
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 199 passed

下一步：

进入 P6-D3：integrate paper execution policy gate into paper execution API。

建议目标：

- 在 paper_execution_api.handle_paper_execution 前调用 evaluate_paper_execution_policy
- policy denied 时直接返回 ok=false
- 不进入 sandbox execution engine
- 保持现有成功路径不变
- 增加 API integration tests
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P6-D3 完成记录

P6-D3：integrate paper execution policy gate into paper execution API 已完成。

新增文件：

- docs/51_p6_integrate_policy_gate_into_paper_execution_api.md
- tests/test_paper_execution_api_policy_integration.py

修改文件：

- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py
- 部分 tests / scripts safe sample，移除 real_order=true 等危险字段

完成内容：

- paper_execution_api.handle_paper_execution 前置调用 evaluate_paper_execution_policy
- policy denied 时直接返回 ok=false
- policy denied 时不进入 sandbox execution engine
- policy denied 时不生成 sandbox execution event
- Dify paper execution adapter 传入 policy_context
- raw_order.real_order=true 返回 PolicyDeny
- policy_context.save_api_key_requested=true 返回 PolicyDeny
- Dify adapter top-level bypass_risk_requested=true 返回 422 / PolicyDeny
- safe paper execution 成功路径保持可用
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 204 passed

下一步：

进入 P6-D4：paper execution policy deny response templates。

建议目标：

- 扩展 paper_execution_response_templates
- 增加 policy deny user-facing response
- 明确 policy deny 不是交易所拒单
- 明确没有真实下单
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P6-D4 完成记录

P6-D4：paper execution policy deny response templates 已完成。

新增文件：

- docs/52_p6_paper_execution_policy_deny_response_templates.md
- tests/test_paper_execution_policy_deny_response_templates.py

修改文件：

- fcf/api/paper_execution_response_templates.py

完成内容：

- 新增 render_paper_policy_deny_response
- render_paper_execution_user_response 自动识别 PolicyDeny
- PolicyDeny 渲染为 paper_policy_deny
- ValueError 仍渲染为 paper_execution_error
- safety refusal 仍渲染为 paper_safety_refusal
- 用户可见文案明确 policy deny 不是交易所真实拒单
- 用户可见文案明确没有真实下单
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 209 passed

下一步：

进入 P6-D5：Dify paper execution response smoke includes policy deny。

建议目标：

- 更新 scripts/run_dify_paper_execution_response_smoke.py
- 增加 policy_deny case
- 区分 policy_deny / execution_error / safety_refusal
- 更新测试
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P6-D5 完成记录

P6-D5：Dify paper execution response smoke includes policy deny 已完成。

新增文件：

- docs/53_p6_dify_paper_execution_response_smoke_policy_deny.md

修改文件：

- scripts/run_dify_paper_execution_response_smoke.py
- tests/test_dify_paper_execution_response_smoke.py

完成内容：

- response smoke case_count 从 4 增加到 5
- 新增 policy_deny_to_user_paper_policy_deny
- policy deny 渲染为 paper_policy_deny
- bad order 仍渲染为 paper_execution_error
- real execution intent 仍渲染为 paper_safety_refusal
- fill / reject 成功路径保持不变
- 明确 policy deny 不是交易所真实拒单
- 明确不接真实交易所 API
- 明确不真实下单

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 210 passed

下一步：

进入 P6-D6：paper execution risk guardian module plan。

建议目标：

- 新增 paper execution risk guardian plan
- 明确 max_quantity / max_notional / duplicate order / missing risk_context 等 risk deny
- 明确 risk deny 不是交易所真实拒单
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P6-D6 完成记录

P6-D6：paper execution risk guardian module plan 已完成。

新增文件：

- docs/54_p6_paper_execution_risk_guardian_plan.md

完成内容：

- 明确 risk deny 定义
- 明确 risk deny 不是 schema error
- 明确 risk deny 不是 policy deny
- 明确 risk deny 不是 Dify safety refusal
- 明确 risk deny 不是交易所真实拒单
- 明确后续 paper execution risk guardian 模块规划
- 明确建议 risk_context
- 明确 max_quantity 风控规则
- 明确 max_notional 风控规则
- 明确 duplicate order 风控规则
- 明确 blocked symbol / asset class 风控规则
- 明确 leverage / margin 风控规则
- 明确 high risk flags 风控规则
- 明确 RiskDeny 用户可见文案要求
- 明确后续 P6-D7 到 P6-D10 集成路线

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 210 passed

下一步：

进入 P6-D7：paper execution risk guardian module。

建议新增：

- fcf/risk/paper_execution_risk_guardian.py
- tests/test_paper_execution_risk_guardian.py

P6-D7 目标：

- 新增 describe_paper_execution_risk_guardian
- 新增 evaluate_paper_execution_risk
- 支持 stable allowed decision dict
- 支持 stable denied decision dict
- 拒绝 missing risk_context
- 拒绝 quantity > max_quantity
- 拒绝 notional > max_notional
- 拒绝 duplicate order
- 拒绝 blocked symbol
- 拒绝 blocked asset_class
- 拒绝 leverage / margin request
- 拒绝 high risk flags
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

