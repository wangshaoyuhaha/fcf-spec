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

