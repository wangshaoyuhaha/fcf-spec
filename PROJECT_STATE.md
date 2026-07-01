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

## Phase 4 已完成范围

P4-D1：Schema hardening plan，已完成。
P4-D2：raw market input schema module，已完成。
P4-D3：schema integration into market input pipeline，已完成。
P4-D4：schema-aware Dify adapter and response tests，已完成。
P4-D5：schema error catalog and stable error messages，已完成。
P4-D6：integrate schema error catalog into raw market input schema，已完成。
P4-D7：schema batch error behavior and Dify batch tests，已完成。
P4-D8：schema hardening midpoint acceptance，已完成。
P4-D9：multi-asset fixture expansion，已完成。
P4-D10：multi-asset fixture Dify response smoke，已完成。
P4-D11：multi-asset error fixture and negative smoke，已完成。
P4-D12：Phase 4 multi-asset schema acceptance，已完成。
P4-D13：Phase 4 closeout / project state consolidation，已完成。

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
- Dify HTTP adapter smoke runner
- Dify integration smoke
- multi-asset fixture
- multi-asset Dify success smoke
- multi-asset Dify error smoke

## 当前关键代码

- fcf/schemas/raw_market_input_schema.py
- fcf/schemas/schema_error_catalog.py
- fcf/pipelines/market_input_pipeline.py
- fcf/api/local_market_input_api.py
- fcf/api/dify_http_adapter.py
- fcf/api/dify_response_templates.py
- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py
- scripts/run_multi_asset_dify_smoke.py
- scripts/run_multi_asset_error_dify_smoke.py

## 当前关键 fixture

- fixtures/raw_market_data_crypto.json
- fixtures/raw_market_data_multi_asset.json

## 当前关键文档

- docs/25_p4_schema_hardening_plan.md
- docs/26_p4_schema_pipeline_integration.md
- docs/27_p4_schema_aware_dify_adapter_response_tests.md
- docs/28_p4_schema_error_catalog.md
- docs/29_p4_integrate_schema_error_catalog.md
- docs/30_p4_schema_batch_error_behavior.md
- docs/31_p4_schema_hardening_midpoint_acceptance.md
- docs/32_p4_multi_asset_fixture_expansion_plan.md
- docs/33_p4_multi_asset_dify_response_smoke.md
- docs/34_p4_multi_asset_error_negative_smoke.md
- docs/35_p4_multi_asset_schema_acceptance.md
- docs/36_p4_closeout_project_state.md

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

python -m pytest -q

预期输出：

- 127 passed

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

## Phase 5 推荐方向

建议下一步进入：

P5-D1：Paper-only sandbox execution boundary plan。

目标：

- 新增 paper-only sandbox execution boundary 文档
- 明确 paper order 与 real order 的区别
- 明确 Dify 不可触达真实执行器
- 明确 sandbox execution 只能产生模拟事件
- 明确 sandbox execution 必须进入 EventStore
- 明确 sandbox execution 必须可 Replay
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 执行 git rev-parse --short HEAD 后填写
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成，D1-D11 已完成。Phase 2 多资产 MarketContext 基础层已完成，P2-D1 到 P2-D10 已完成。Phase 3 数据接入与 Dify integration 已完成阶段收尾，P3-D1 到 P3-D14 已完成。Phase 4 schema hardening 与 multi-asset fixture expansion 已完成阶段收尾，P4-D1 到 P4-D13 已完成。当前不是足球系统，也不是 BTC-only。BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。
当前能力：raw market input schema、schema error catalog、market input pipeline schema integration、local_market_input_api、dify_http_adapter、dify_response_templates、Dify HTTP adapter smoke runner、Dify integration smoke、multi-asset fixture、multi-asset Dify success smoke、multi-asset Dify error smoke 均已完成。
当前验证：python main.py 输出 events_recorded: 8；python scripts/run_dify_http_adapter_smoke.py 输出 status completed；python scripts/run_dify_integration_smoke.py 输出 status completed；python scripts/run_multi_asset_dify_smoke.py 输出 status completed；python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed；python -m pytest -q 预计显示 127 passed。
安全边界：Dify 不作为底层交易内核，不直接接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，只调用受控 API wrapper / pipeline，不把 pipeline 成功伪装成真实交易成功。
next_action: 进入 P5-D1：Paper-only sandbox execution boundary plan。新增 paper-only sandbox execution boundary 文档，明确 paper order 与 real order 的区别、Dify 不可触达真实执行器、sandbox execution 只能产生模拟事件并进入 EventStore / Replay。不接真实交易所 API，不真实下单，不破坏测试。
要求：全程中文一步步指挥；命令必须是可直接复制的 Git Bash 格式；多行 cat 必须包含完整 EOF；每次重要更新都 commit 并 push，并更新新的续聊话术。


## P5-D1 完成记录

P5-D1：Paper-only sandbox execution boundary plan 已完成。

新增文件：

- docs/37_p5_paper_sandbox_execution_boundary_plan.md

完成内容：

- 明确 paper order 定义
- 明确 real order 定义
- 明确 sandbox execution 定义
- 明确 Dify 与执行边界
- 明确建议事件类型
- 明确建议模块边界
- 明确 stable response dict 要求
- 明确 Replay 要求
- 明确审计要求
- 明确用户可见说明
- 明确 P5-D2 下一步方向

当前安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核
- 不把 sandbox execution 伪装成真实成交

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 127 passed

下一步：

进入 P5-D2：paper order schema module。

建议新增：

- fcf/paper/__init__.py
- fcf/paper/paper_order_schema.py
- tests/test_paper_order_schema.py

P5-D2 目标：

- 定义 paper order required fields
- 定义 side normalization
- 定义 order_type normalization
- 定义 quantity positive check
- 定义 price optional positive check
- 明确 real_order false
- 明确 execution_mode paper
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P5-D2 完成记录

P5-D2：paper order schema module 已完成。

新增文件：

- docs/38_p5_paper_order_schema_module.md
- fcf/paper/__init__.py
- fcf/paper/paper_order_schema.py
- tests/test_paper_order_schema.py

完成内容：

- 定义 paper order required fields
- 实现 describe_paper_order_schema
- 实现 check_required_fields
- 实现 normalize_side
- 实现 normalize_order_type
- 实现 normalize_time_in_force
- 实现 normalize_paper_order
- 实现 validate_paper_order
- 实现 quantity positive check
- 实现 price optional positive check
- 强制 execution_mode = paper
- 强制 real_order = false
- 强制 real_exchange_api = false
- 强制 real_money_impact = false
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 141 passed

下一步：

进入 P5-D3：sandbox execution engine skeleton。

建议新增：

- fcf/paper/sandbox_execution_engine.py
- tests/test_sandbox_execution_engine.py

P5-D3 目标：

- 接收 normalized paper order
- 生成 sandbox execution summary
- 支持 simulated_fill
- 支持 simulated_reject
- 明确 real_order false
- 明确 real_execution false
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P5-D3 完成记录

P5-D3：sandbox execution engine skeleton 已完成。

新增文件：

- docs/39_p5_sandbox_execution_engine_skeleton.md
- fcf/paper/sandbox_execution_engine.py
- tests/test_sandbox_execution_engine.py

完成内容：

- 新增 describe_sandbox_execution_engine
- 新增 execute_sandbox_order
- 支持 simulated_fill
- 支持 simulated_reject
- 支持 full fill
- 支持 partial fill
- 支持 stable response dict
- 错误时返回 ok false / error / data null
- 强制 execution_mode = paper
- 强制 real_order = false
- 强制 real_execution = false
- 强制 real_exchange_api = false
- 强制 real_money_impact = false
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 151 passed

下一步：

进入 P5-D4：sandbox execution EventStore and Replay integration。

建议目标：

- sandbox execution summary 写入 EventStore
- 生成 sandbox execution event
- ReplayEngine 回放 sandbox execution event
- 增加测试
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P5-D4 完成记录

P5-D4：sandbox execution EventStore and Replay integration 已完成。

新增文件：

- docs/40_p5_sandbox_execution_eventstore_replay.md
- tests/test_sandbox_execution_eventstore_replay.py

修改文件：

- fcf/paper/sandbox_execution_engine.py

完成内容：

- 新增 execute_sandbox_order_with_eventstore
- sandbox execution success 写入 EventStore
- full fill event 可 Replay
- partial fill event 可 Replay
- reject event 可 Replay
- 可选 output_path 持久化 JSONL
- bad paper order 仍返回 ok=false
- 保持 stable response dict
- 保持安全边界字段

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 156 passed

下一步：

进入 P5-D5：paper execution API wrapper。

建议目标：

- 新增 fcf/api/paper_execution_api.py
- 包装 execute_sandbox_order_with_eventstore
- 返回稳定 response dict
- 支持 simulated_fill / simulated_reject
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P5-D5 完成记录

P5-D5：paper execution API wrapper 已完成。

新增文件：

- docs/41_p5_paper_execution_api_wrapper.md
- fcf/api/paper_execution_api.py
- tests/test_paper_execution_api.py

完成内容：

- 新增 describe_paper_execution_api
- 新增 handle_paper_execution
- 包装 execute_sandbox_order_with_eventstore
- 支持 simulated_fill
- 支持 simulated_reject
- 支持 full fill
- 支持 partial fill
- 支持 stable response dict
- 支持可选 JSONL 持久化
- 错误时返回 ok false / error / data null
- 强制 execution_mode = paper
- 强制 real_order = false
- 强制 real_execution = false
- 强制 real_exchange_api = false
- 强制 real_money_impact = false
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 163 passed

下一步：

进入 P5-D6：Dify paper execution contract and local adapter planning。

建议目标：

- 新增 Dify paper execution API contract 文档
- 明确 paper execution 输入 JSON
- 明确 paper execution 输出 JSON
- 明确 Dify 禁止 real execution
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P5-D6 完成记录

P5-D6：Dify paper execution contract and local adapter planning 已完成。

新增文件：

- docs/42_p5_dify_paper_execution_contract.md

完成内容：

- 明确 Dify simulated_fill 输入 JSON
- 明确 Dify simulated_reject 输入 JSON
- 明确 paper execution 成功输出 JSON
- 明确 paper execution 错误输出 JSON
- 明确 Dify workflow 推荐节点
- 明确 Dify 字段映射
- 明确 Dify 必须拒绝的 intent
- 明确用户可见 success 文案要求
- 明确 Dify paper execution local adapter 规划

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 163 passed

下一步：

进入 P5-D7：Dify paper execution local adapter。

建议新增：

- fcf/api/dify_paper_execution_adapter.py
- tests/test_dify_paper_execution_adapter.py

目标：

- 支持 GET /api/v1/paper-execution/contract
- 支持 POST /api/v1/paper-execution/execute
- 只调用 paper_execution_api
- 返回 http-style response dict
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P5-D7 完成记录

P5-D7：Dify paper execution local adapter 已完成。

新增文件：

- docs/43_p5_dify_paper_execution_local_adapter.md
- fcf/api/dify_paper_execution_adapter.py
- tests/test_dify_paper_execution_adapter.py

完成内容：

- 新增 route_dify_paper_execution_request
- 新增 describe_routes
- 支持 GET /api/v1/paper-execution/contract
- 支持 POST /api/v1/paper-execution/execute
- 支持 simulated_fill
- 支持 simulated_reject
- 支持 partial fill
- 支持 bad order 422
- 支持 bad simulation_mode 422
- 支持 unknown route 404
- 支持 method not allowed 405
- 支持 bad request 400
- 支持可选 JSONL 持久化
- 只调用 paper_execution_api
- 不接真实交易所 API
- 不真实下单

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 172 passed

下一步：

进入 P5-D8：Dify paper execution smoke runner。

建议目标：

- 新增 scripts/run_dify_paper_execution_smoke.py
- 调用 Dify paper execution adapter
- 覆盖 contract / fill / reject / error
- 输出稳定 summary
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

