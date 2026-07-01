# FCF Spec

FCF Spec 是一个全金融市场 / 多资产交易系统的最小事件骨架项目。

## 当前定位

本项目不是足球系统。

本项目也不是只做 BTC。

当前目标是构建一个可以逐步适配全金融市场的事件驱动交易系统骨架。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

Phase 2 多资产市场上下文基础层已完成阶段验收。

Phase 3 已启动，当前重点是数据接入边界、mock 数据接入、可回放输入、本地外部调用边界、Dify workflow 接入规划和本地 API wrapper。

Dify 后续会作为上层 workflow / 对话入口 / 编排层接入，不作为底层交易内核。

## 当前阶段

- Phase 1 Build Spine 已完成稳定收尾
- D1-D11 已完成
- Phase 2 多资产市场上下文基础层已完成阶段验收
- P2-D1 到 P2-D10 已完成
- Phase 3 已启动
- P3-D1：真实数据接入边界规划已完成
- P3-D2：mock market data adapter 已完成
- P3-D3：replayable raw market fixture 已完成
- P3-D4：本地 system input pipeline / 外部调用边界已完成
- P3-D5：Dify workflow 接入规划已完成
- P3-D6：本地 API wrapper 已完成

## 当前能力

当前系统已经具备一条最小交易事件链：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

当前已经完成：

- FCFEvent 事件契约
- EventBus
- EventStore
- ReplayEngine
- 数据标准化模块
- regime 检测模块
- decision proposer
- policy engine
- risk guardian
- executor
- shadow simulator
- JSONL 事件持久化
- JSONL 事件读取
- ReplayEngine 回放一致性测试
- Phase 1 骨架验收
- Phase 2 多资产市场上下文基础层
- Phase 3 数据接入边界规划
- mock market data adapter
- replayable raw market fixture
- market input pipeline
- 外部调用 summary dict
- Dify workflow 接入规划
- local_market_input_api wrapper

## 当前验证方式

运行最小主流程：

python main.py

预期输出包含：

- FCF minimal spine executed.
- events_recorded: 8

运行测试：

python -m pytest -q

预期输出：

- 58 passed

## 当前关键代码

- fcf/modules/mock_market_data_adapter.py
- fcf/pipelines/market_input_pipeline.py
- fcf/api/local_market_input_api.py
- tests/test_mock_market_data_adapter.py
- tests/test_raw_market_fixture_replay.py
- tests/test_market_input_pipeline.py
- tests/test_local_market_input_api.py

## 当前关键数据

- fixtures/raw_market_data_crypto.json

## 当前关键文档

- docs/14_phase2_market_context_acceptance.md
- docs/15_phase3_data_ingestion_boundary.md
- docs/16_dify_workflow_integration_plan.md

## Dify 接入边界

Dify 不是底层交易内核。

Dify 不直接接真实交易所 API。

Dify 不真实下单。

Dify 只调用 FCF 暴露的受控 API wrapper / pipeline，并接收 summary dict 作为输出。

## 下一步

进入 P3-D7：

Dify API contract / example payload 文档。

建议新增：

- docs/17_dify_api_contract_examples.md

P3-D7 目标：

- 明确 Dify 调用 local_market_input_api 的输入 JSON
- 明确 Dify 收到的输出 JSON
- 明确错误响应格式
- 明确 workflow 节点怎么传字段
- 明确不能真实下单
- 明确不能接真实交易所 API key
- 保持当前测试通过

## P3-D7：Dify API Contract Examples

P3-D7 已新增：

- docs/17_dify_api_contract_examples.md

该文档明确：

- Dify 输入 JSON
- FCF 输出 JSON
- 错误响应格式
- workflow 节点字段传递方式
- 安全边界

Dify 仍然只作为上层 workflow / 对话入口 / 编排层。
Dify 不作为底层交易内核。
Dify 不直接接真实交易所 API。
Dify 不真实下单。
Dify 只调用受控 API wrapper / pipeline。


## P3-D8：Dify Workflow HTTP/API Node Mapping

P3-D8 已新增：

- docs/18_dify_workflow_http_api_node_mapping.md

该文档明确：

- Dify workflow 推荐节点顺序
- 每个节点职责
- 字段如何从 Dify 传给 FCF
- FCF API Call Node 的边界
- response.ok 分支处理方式
- success summary 输出方式
- error summary 输出方式
- 禁止真实交易所 API
- 禁止真实下单

P3-D8 仍然只做文档和边界设计。
不接真实交易所 API。
不真实下单。


## P3-D9：Dify Local HTTP Adapter

P3-D9 新增：

- docs/19_dify_local_http_adapter.md
- fcf/api/dify_http_adapter.py
- tests/test_dify_http_adapter.py

当前 adapter 提供本地 HTTP 风格路由函数：

- GET /api/v1/contract
- POST /api/v1/market-input/single
- POST /api/v1/market-input/batch

P3-D9 不引入外部 Web 框架。
P3-D9 不接真实交易所 API。
P3-D9 不保存真实 API key。
P3-D9 不真实下单。
P3-D9 只把 Dify HTTP/API 节点请求映射到受控 local_market_input_api wrapper。


## P3-D10：Dify HTTP Adapter Smoke Runner

P3-D10 新增：

- docs/20_dify_http_adapter_smoke_runner.md
- scripts/run_dify_http_adapter_smoke.py
- tests/test_dify_http_adapter_smoke_runner.py

当前 smoke runner 用本地样例请求调用：

- GET /api/v1/contract
- POST /api/v1/market-input/single
- POST /api/v1/market-input/batch
- bad input example
- unknown route example

P3-D10 不启动真实 HTTP server。
P3-D10 不接真实 Dify。
P3-D10 不接真实交易所 API。
P3-D10 不真实下单。


## P3-D11：Dify User Facing Response Templates

P3-D11 新增：

- docs/21_dify_user_facing_response_templates.md
- fcf/api/dify_response_templates.py
- tests/test_dify_response_templates.py

当前模板覆盖：

- success
- error
- safety_refusal

Dify 面向用户输出时必须保留安全边界：
不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单。


## P3-D12：Dify Adapter Response Integration Smoke

P3-D12 新增：

- docs/22_dify_adapter_response_integration_smoke.md
- scripts/run_dify_integration_smoke.py
- tests/test_dify_integration_smoke.py

当前 integration smoke 把本地 HTTP adapter response 接入用户可见 response templates。

覆盖场景：

- single success -> user success
- bad input -> user error
- forbidden intent -> safety refusal

P3-D12 不启动真实 HTTP server。
P3-D12 不接真实 Dify。
P3-D12 不接真实交易所 API。
P3-D12 不真实下单。


## P3-D13：Phase 3 Dify Integration Acceptance

P3-D13 新增：

- docs/23_phase3_dify_integration_acceptance.md

该文档汇总验收 P3-D5 到 P3-D12 的 Dify integration 工作：

- workflow integration plan
- local API wrapper
- API contract examples
- workflow HTTP/API node mapping
- local HTTP adapter
- HTTP adapter smoke runner
- user-facing response templates
- adapter + response templates integration smoke

Phase 3 Dify integration 当前仍然保持安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核


## P3-D14：Phase 3 Closeout

P3-D14 新增：

- docs/24_phase3_closeout_project_state.md

Phase 3 当前已完成阶段收尾。

当前完成范围：

- 数据接入边界
- mock market data adapter
- replayable raw market fixture
- local system input pipeline
- Dify workflow integration plan
- local API wrapper
- Dify API contract examples
- Dify workflow node mapping
- Dify local HTTP adapter
- Dify smoke runner
- Dify user-facing response templates
- Dify integration smoke
- Phase 3 Dify integration acceptance
- Phase 3 closeout / project state consolidation

当前验证：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 73 passed

安全边界继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核


## P4-D1：Schema Hardening Plan

P4-D1 新增：

- docs/25_p4_schema_hardening_plan.md

P4-D1 开始 Phase 4。

Phase 4 第一目标是强化 raw market input 的 schema 边界，明确：

- 必填字段
- 可选字段
- 类型转换规则
- market_type 归一化规则
- asset_class 多资产兼容策略
- 错误响应要求
- Dify 接入安全边界

P4-D1 只做规划文档。
不接真实交易所 API。
不保存真实 API key。
不读取钱包私钥。
不真实下单。


## P4-D2：Raw Market Input Schema Module

P4-D2 新增：

- fcf/schemas/__init__.py
- fcf/schemas/raw_market_input_schema.py
- tests/test_raw_market_input_schema.py

当前 schema module 实现：

- required field check
- optional number field normalization
- number conversion
- market_type normalization
- asset_class normalization
- last_price 正数校验
- volume / depth 非负校验
- best_bid <= best_ask 校验
- stable schema description

P4-D2 仍然不接真实交易所 API。
P4-D2 不保存真实 API key。
P4-D2 不读取钱包私钥。
P4-D2 不真实下单。


## P4-D3：Schema Integration Into Market Input Pipeline

P4-D3 新增：

- docs/26_p4_schema_pipeline_integration.md
- tests/test_market_input_pipeline_schema_integration.py

P4-D3 修改：

- fcf/pipelines/market_input_pipeline.py

当前 market_input_pipeline 已在入口调用 normalize_raw_market_input。

当前能力：

- single input 进入 pipeline 前先做 schema normalization
- batch input 进入 pipeline 前先做 schema normalization
- schema 错误直接抛出 ValueError
- local_market_input_api 继续把错误包装成稳定 response dict
- 不接真实交易所 API
- 不真实下单


## P4-D4：Schema-aware Dify Adapter and Response Tests

P4-D4 新增：

- docs/27_p4_schema_aware_dify_adapter_response_tests.md
- tests/test_schema_aware_dify_adapter_response.py

当前测试覆盖：

- schema normalized success
- missing required field
- bad market_type
- bad spread
- bad asset_class
- schema error to user-facing error response

P4-D4 不接真实交易所 API。
P4-D4 不保存真实 API key。
P4-D4 不读取钱包私钥。
P4-D4 不真实下单。


## P4-D5：Schema Error Catalog

P4-D5 新增：

- docs/28_p4_schema_error_catalog.md
- fcf/schemas/schema_error_catalog.py
- tests/test_schema_error_catalog.py

当前 schema error catalog 定义：

- MissingField
- InvalidEnumValue
- InvalidNumber
- InvalidPositiveNumber
- InvalidNonNegativeNumber
- InvalidSpread
- InvalidPayloadType

P4-D5 固化 schema error message builder。
P4-D5 不接真实交易所 API。
P4-D5 不保存真实 API key。
P4-D5 不读取钱包私钥。
P4-D5 不真实下单。


## P4-D6：Integrate Schema Error Catalog

P4-D6 新增：

- docs/29_p4_integrate_schema_error_catalog.md
- tests/test_raw_market_input_schema_error_catalog_integration.py

P4-D6 修改：

- fcf/schemas/raw_market_input_schema.py

当前 raw_market_input_schema 已使用 schema_error_catalog 的稳定 message builder。

保持兼容：

- Dify adapter 422 行为不变
- response templates error 行为不变
- 现有错误 message 不变
- 不接真实交易所 API
- 不真实下单


## P4-D7：Schema Batch Error Behavior

P4-D7 新增：

- docs/30_p4_schema_batch_error_behavior.md
- tests/test_schema_batch_dify_adapter_errors.py

当前 batch schema error 策略：

- batch 中任意一行 schema 校验失败，整个 batch 失败
- 不做部分成功
- 不写入部分成功事件
- Dify HTTP adapter 返回 422
- local_market_input_api 返回 ok false
- response templates 转成 user-facing error response

P4-D7 覆盖：

- batch success schema normalization
- batch missing required field
- batch bad market_type
- batch bad spread
- batch bad asset_class
- batch bad number

P4-D7 不接真实交易所 API。
P4-D7 不保存真实 API key。
P4-D7 不读取钱包私钥。
P4-D7 不真实下单。


## P4-D8：Schema Hardening Midpoint Acceptance

P4-D8 新增：

- docs/31_p4_schema_hardening_midpoint_acceptance.md

P4-D8 汇总 P4-D1 到 P4-D7 的 schema hardening 成果：

- raw market input schema module
- schema integration into market input pipeline
- schema-aware Dify adapter tests
- schema error catalog
- schema error catalog integration
- batch schema error behavior
- Dify batch error tests

当前验证：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 116 passed

P4-D8 不接真实交易所 API。
P4-D8 不保存真实 API key。
P4-D8 不读取钱包私钥。
P4-D8 不真实下单。


## P4-D9：Multi-asset Fixture Expansion

P4-D9 新增：

- docs/32_p4_multi_asset_fixture_expansion_plan.md
- fixtures/raw_market_data_multi_asset.json
- tests/test_multi_asset_fixture_schema.py

当前多资产 fixture 覆盖：

- crypto / BTCUSDT / perpetual
- equities / AAPL / spot
- fx / EURUSD / spot
- commodities / XAUUSD / futures

当前测试确认：

- fixture 可以加载
- 每一行都能通过 raw market input schema
- market_input_pipeline 可以处理多资产 batch
- Dify HTTP batch adapter 可以处理多资产 batch

P4-D9 不接真实交易所 API。
P4-D9 不保存真实 API key。
P4-D9 不读取钱包私钥。
P4-D9 不真实下单。


## P4-D10：Multi-asset Dify Response Smoke

P4-D10 新增：

- docs/33_p4_multi_asset_dify_response_smoke.md
- scripts/run_multi_asset_dify_smoke.py
- tests/test_multi_asset_dify_smoke.py

当前 smoke runner 会读取：

- fixtures/raw_market_data_multi_asset.json

并调用：

- POST /api/v1/market-input/batch

然后接入：

- render_dify_user_response

当前覆盖：

- crypto / BTCUSDT
- equities / AAPL
- fx / EURUSD
- commodities / XAUUSD

P4-D10 不接真实交易所 API。
P4-D10 不保存真实 API key。
P4-D10 不读取钱包私钥。
P4-D10 不真实下单。


## P4-D11：Multi-asset Error Dify Smoke

P4-D11 新增：

- docs/34_p4_multi_asset_error_negative_smoke.md
- scripts/run_multi_asset_error_dify_smoke.py
- tests/test_multi_asset_error_dify_smoke.py

当前 negative smoke 覆盖：

- equities bad market_type
- fx bad spread
- commodities missing last_price

当前预期行为：

- Dify batch route 返回 422
- local_market_input_api 返回 ok false
- response templates 转成 user-facing error response
- batch 中任意一行 schema 错误则整体失败
- 不做部分成功

P4-D11 不接真实交易所 API。
P4-D11 不保存真实 API key。
P4-D11 不读取钱包私钥。
P4-D11 不真实下单。


## P4-D12：Phase 4 Multi-asset Schema Acceptance

P4-D12 新增：

- docs/35_p4_multi_asset_schema_acceptance.md

P4-D12 汇总验收：

- multi-asset fixture
- multi-asset Dify success smoke
- multi-asset Dify negative smoke
- batch schema error 整体失败策略
- user-facing success response
- user-facing error response

当前多资产覆盖：

- crypto / BTCUSDT
- equities / AAPL
- fx / EURUSD
- commodities / XAUUSD

P4-D12 不接真实交易所 API。
P4-D12 不保存真实 API key。
P4-D12 不读取钱包私钥。
P4-D12 不真实下单。


## P4-D13：Phase 4 Closeout

P4-D13 新增：

- docs/36_p4_closeout_project_state.md

Phase 4 已完成阶段收尾。

当前完成范围：

- schema hardening
- schema error catalog
- schema pipeline integration
- Dify schema-aware tests
- batch schema error behavior
- multi-asset fixture
- multi-asset success smoke
- multi-asset negative smoke
- Phase 4 multi-asset schema acceptance

当前验证：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 显示 127 passed

下一步建议：

- P5-D1：Paper-only sandbox execution boundary plan


## P5-D1：Paper-only Sandbox Execution Boundary Plan

P5-D1 新增：

- docs/37_p5_paper_sandbox_execution_boundary_plan.md

P5-D1 开始 Phase 5。

Phase 5 第一目标是定义 paper-only sandbox execution boundary。

P5-D1 明确：

- paper order 与 real order 的区别
- sandbox execution 只能模拟执行
- sandbox execution 必须进入 EventStore
- sandbox execution 必须可 Replay
- Dify 不可触达真实执行器
- Dify 不可真实下单
- sandbox execution 不能伪装成真实成交

P5-D1 不接真实交易所 API。
P5-D1 不保存真实 API key。
P5-D1 不读取钱包私钥。
P5-D1 不真实下单。


## P5-D2：Paper Order Schema Module

P5-D2 新增：

- fcf/paper/__init__.py
- fcf/paper/paper_order_schema.py
- tests/test_paper_order_schema.py
- docs/38_p5_paper_order_schema_module.md

当前 paper order schema 实现：

- required field check
- side normalization
- order_type normalization
- time_in_force normalization
- quantity positive check
- price optional positive check
- metadata dict check
- execution_mode 强制为 paper
- real_order 强制为 false
- real_exchange_api 强制为 false
- real_money_impact 强制为 false

P5-D2 不接真实交易所 API。
P5-D2 不保存真实 API key。
P5-D2 不读取钱包私钥。
P5-D2 不真实下单。


## P5-D3：Sandbox Execution Engine Skeleton

P5-D3 新增：

- docs/39_p5_sandbox_execution_engine_skeleton.md
- fcf/paper/sandbox_execution_engine.py
- tests/test_sandbox_execution_engine.py

当前 sandbox execution engine 支持：

- simulated_fill
- simulated_reject
- full fill
- partial fill
- stable response dict
- safe boundary fields

当前强制：

- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

P5-D3 不接真实交易所 API。
P5-D3 不保存真实 API key。
P5-D3 不读取钱包私钥。
P5-D3 不真实下单。


## P5-D4：Sandbox Execution EventStore and Replay Integration

P5-D4 新增：

- docs/40_p5_sandbox_execution_eventstore_replay.md
- tests/test_sandbox_execution_eventstore_replay.py

P5-D4 修改：

- fcf/paper/sandbox_execution_engine.py

当前新增能力：

- execute_sandbox_order_with_eventstore
- sandbox execution event 写入 EventStore
- ReplayEngine 回放 sandbox execution event
- 可选 JSONL 持久化
- full fill / partial fill / reject 均可 Replay

P5-D4 不接真实交易所 API。
P5-D4 不保存真实 API key。
P5-D4 不读取钱包私钥。
P5-D4 不真实下单。


## P5-D5：Paper Execution API Wrapper

P5-D5 新增：

- docs/41_p5_paper_execution_api_wrapper.md
- fcf/api/paper_execution_api.py
- tests/test_paper_execution_api.py

当前 paper execution API wrapper 支持：

- describe_paper_execution_api
- handle_paper_execution
- simulated_fill
- simulated_reject
- stable response dict
- EventStore / ReplayEngine integration
- 可选 JSONL 持久化

当前强制安全边界：

- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

P5-D5 不接真实交易所 API。
P5-D5 不保存真实 API key。
P5-D5 不读取钱包私钥。
P5-D5 不真实下单。


## P5-D6：Dify Paper Execution Contract

P5-D6 新增：

- docs/42_p5_dify_paper_execution_contract.md

P5-D6 明确：

- Dify paper execution 输入 JSON
- Dify paper execution 输出 JSON
- simulated_fill 请求格式
- simulated_reject 请求格式
- 错误响应格式
- Dify workflow 推荐节点
- Dify 字段映射
- Dify 必须拒绝的 real execution intent
- 用户可见 success / error / safety 文案边界
- 后续 Dify paper execution adapter 规划

P5-D6 不接真实交易所 API。
P5-D6 不保存真实 API key。
P5-D6 不读取钱包私钥。
P5-D6 不真实下单。


## P5-D7：Dify Paper Execution Local Adapter

P5-D7 新增：

- docs/43_p5_dify_paper_execution_local_adapter.md
- fcf/api/dify_paper_execution_adapter.py
- tests/test_dify_paper_execution_adapter.py

当前支持路由：

- GET /api/v1/paper-execution/contract
- POST /api/v1/paper-execution/execute

当前能力：

- contract route
- simulated_fill
- simulated_reject
- partial fill
- bad order 422
- bad simulation_mode 422
- unknown route 404
- method not allowed 405
- bad request 400
- 可选 JSONL 持久化

P5-D7 只调用 paper_execution_api。
P5-D7 不接真实交易所 API。
P5-D7 不保存真实 API key。
P5-D7 不读取钱包私钥。
P5-D7 不真实下单。


## P5-D8：Dify Paper Execution Smoke Runner

P5-D8 新增：

- docs/44_p5_dify_paper_execution_smoke_runner.md
- scripts/run_dify_paper_execution_smoke.py
- tests/test_dify_paper_execution_smoke.py

当前 smoke runner 覆盖：

- contract
- simulated_fill
- simulated_reject
- bad_order_error
- bad_simulation_mode_error
- missing_raw_order_error

当前安全边界：

- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

P5-D8 不接真实交易所 API。
P5-D8 不保存真实 API key。
P5-D8 不读取钱包私钥。
P5-D8 不真实下单。


## P5-D9：Paper Execution User-facing Response Templates

P5-D9 新增：

- docs/45_p5_paper_execution_user_facing_response_templates.md
- fcf/api/paper_execution_response_templates.py
- tests/test_paper_execution_response_templates.py

当前模板覆盖：

- paper_fill_success
- paper_reject_success
- paper_execution_error
- paper_safety_refusal

P5-D9 强制用户可见边界：

- paper fill 不是实盘成交
- paper reject 不是交易所真实拒单
- error 不是实盘下单失败
- safety refusal 必须拒绝真实执行 intent

P5-D9 不接真实交易所 API。
P5-D9 不保存真实 API key。
P5-D9 不读取钱包私钥。
P5-D9 不真实下单。


## P5-D10：Dify Paper Execution Response Integration Smoke

P5-D10 新增：

- docs/46_p5_dify_paper_execution_response_smoke.md
- scripts/run_dify_paper_execution_response_smoke.py
- tests/test_dify_paper_execution_response_smoke.py

当前 integration smoke 覆盖：

- fill -> paper_fill_success
- reject -> paper_reject_success
- bad order -> paper_execution_error
- real execution intent -> paper_safety_refusal

P5-D10 不接真实交易所 API。
P5-D10 不保存真实 API key。
P5-D10 不读取钱包私钥。
P5-D10 不真实下单。
P5-D10 不把 paper execution 伪装成 real execution。


## P5-D11：Phase 5 Paper Execution Acceptance

P5-D11 新增：

- docs/47_p5_paper_execution_acceptance.md

P5-D11 汇总验收 Phase 5 paper-only sandbox execution 成果：

- paper order schema
- sandbox execution engine
- EventStore / ReplayEngine integration
- paper execution API wrapper
- Dify paper execution local adapter
- Dify paper execution smoke runner
- paper execution user-facing response templates
- Dify paper execution response integration smoke

当前验证：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 186 passed


## P5-D12：Phase 5 Closeout

P5-D12 新增：

- docs/48_p5_closeout_project_state.md

Phase 5 已完成阶段收尾。

当前完成范围：

- paper-only sandbox execution boundary
- paper order schema
- sandbox execution engine
- EventStore / ReplayEngine integration
- paper execution API wrapper
- Dify paper execution local adapter
- Dify paper execution smoke runner
- paper execution user-facing response templates
- Dify paper execution response integration smoke

下一步建议：

- P6-D1：Policy and risk deny case hardening plan

继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不把 paper execution 伪装成 real execution


## P6-D1：Policy and Risk Deny Case Hardening Plan

P6-D1 新增：

- docs/49_p6_policy_risk_deny_case_hardening_plan.md

P6-D1 开始 Phase 6。

Phase 6 第一目标是强化 policy / risk deny case。

P6-D1 明确：

- schema error、policy deny、risk deny、Dify safety refusal 的区别
- paper execution 也不能绕过 policy / risk
- deny case 的建议执行顺序
- 后续 policy deny 候选规则
- 后续 risk deny 候选规则
- Dify 用户可见要求
- 后续测试规划

P6-D1 不接真实交易所 API。
P6-D1 不保存真实 API key。
P6-D1 不读取钱包私钥。
P6-D1 不真实下单。


## P6-D2：Paper Execution Policy Gate Module

P6-D2 新增：

- docs/50_p6_paper_execution_policy_gate.md
- fcf/policy/paper_execution_policy.py
- tests/test_paper_execution_policy.py

当前 policy gate 支持：

- evaluate_paper_execution_policy
- describe_paper_execution_policy
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

P6-D2 不接真实交易所 API。
P6-D2 不保存真实 API key。
P6-D2 不读取钱包私钥。
P6-D2 不真实下单。


## P6-D3：Integrate Policy Gate Into Paper Execution API

P6-D3 新增：

- docs/51_p6_integrate_policy_gate_into_paper_execution_api.md
- tests/test_paper_execution_api_policy_integration.py

P6-D3 修改：

- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py
- 部分 tests / scripts 中的 safe sample，移除 real_order=true 等危险字段

当前能力：

- handle_paper_execution 会先调用 evaluate_paper_execution_policy
- policy denied 时直接返回 ok=false
- policy denied 时不进入 sandbox execution engine
- Dify adapter 会把 body 作为 policy_context 传入
- top-level dangerous intent 会被拒绝

P6-D3 不接真实交易所 API。
P6-D3 不保存真实 API key。
P6-D3 不读取钱包私钥。
P6-D3 不真实下单。


## P6-D4：Paper Execution Policy Deny Response Templates

P6-D4 新增：

- docs/52_p6_paper_execution_policy_deny_response_templates.md
- tests/test_paper_execution_policy_deny_response_templates.py

P6-D4 修改：

- fcf/api/paper_execution_response_templates.py

当前新增：

- render_paper_policy_deny_response
- PolicyDeny 自动渲染为 paper_policy_deny

当前用户可见边界：

- policy deny 不是交易所真实拒单
- policy deny 不是真实下单失败
- policy deny 没有连接真实交易所
- policy deny 没有真实下单
- policy deny 没有真实资金变化
- policy deny 没有真实仓位变化

P6-D4 不接真实交易所 API。
P6-D4 不保存真实 API key。
P6-D4 不读取钱包私钥。
P6-D4 不真实下单。


## P6-D5：Dify Paper Execution Response Smoke Includes Policy Deny

P6-D5 新增：

- docs/53_p6_dify_paper_execution_response_smoke_policy_deny.md

P6-D5 修改：

- scripts/run_dify_paper_execution_response_smoke.py
- tests/test_dify_paper_execution_response_smoke.py

当前 response smoke 覆盖：

- fill -> paper_fill_success
- reject -> paper_reject_success
- policy deny -> paper_policy_deny
- bad order -> paper_execution_error
- real execution intent -> paper_safety_refusal

P6-D5 明确区分：

- policy_deny 不是交易所真实拒单
- execution_error 不是实盘下单失败
- safety_refusal 不调用 adapter

P6-D5 不接真实交易所 API。
P6-D5 不保存真实 API key。
P6-D5 不读取钱包私钥。
P6-D5 不真实下单。


## P6-D6：Paper Execution Risk Guardian Module Plan

P6-D6 新增：

- docs/54_p6_paper_execution_risk_guardian_plan.md

P6-D6 明确：

- risk deny 的定义
- risk deny 与 schema error / policy deny / safety refusal 的区别
- 后续 paper execution risk guardian 模块规划
- 建议 risk_context
- 建议 max_quantity 规则
- 建议 max_notional 规则
- 建议 duplicate order 规则
- 建议 blocked symbol / blocked asset class 规则
- 建议 leverage / margin 拒绝规则
- 建议 high risk flags 拒绝规则
- RiskDeny 用户可见文案要求
- 后续 P6-D7 到 P6-D10 集成路径

P6-D6 不接真实交易所 API。
P6-D6 不保存真实 API key。
P6-D6 不读取钱包私钥。
P6-D6 不真实下单。


## P6-D7：Paper Execution Risk Guardian Module

P6-D7 新增：

- docs/55_p6_paper_execution_risk_guardian_module.md
- fcf/risk/paper_execution_risk_guardian.py
- tests/test_paper_execution_risk_guardian.py

当前新增函数：

- describe_paper_execution_risk_guardian
- evaluate_paper_execution_risk

当前 RiskDeny 覆盖：

- request must be dict
- raw_order must be dict
- missing risk_context
- quantity > max_quantity
- notional > max_notional
- duplicate order key
- blocked symbol
- blocked asset class
- leverage request
- margin request
- high risk flags

P6-D7 不接真实交易所 API。
P6-D7 不保存真实 API key。
P6-D7 不读取钱包私钥。
P6-D7 不真实下单。


## P6-D8：Integrate Risk Guardian Into Paper Execution API

P6-D8 新增：

- docs/56_p6_integrate_risk_guardian_into_paper_execution_api.md
- tests/test_paper_execution_api_risk_integration.py

P6-D8 修改：

- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

当前执行顺序：

- policy gate
- risk guardian
- sandbox execution

当前能力：

- RiskDeny 直接返回 ok=false
- RiskDeny 不进入 sandbox execution engine
- RiskDeny 不生成 sandbox execution event
- Dify adapter 传入 risk_context
- max_quantity / max_notional / blocked symbol 等 risk deny 可在 API 层拦截

P6-D8 不接真实交易所 API。
P6-D8 不保存真实 API key。
P6-D8 不读取钱包私钥。
P6-D8 不真实下单。


## P6-D9：Paper Execution Risk Deny Response Templates

P6-D9 新增：

- docs/57_p6_paper_execution_risk_deny_response_templates.md
- tests/test_paper_execution_risk_deny_response_templates.py

P6-D9 修改：

- fcf/api/paper_execution_response_templates.py

当前新增：

- render_paper_risk_deny_response
- RiskDeny 自动渲染为 paper_risk_deny

当前用户可见边界：

- risk deny 不是交易所真实拒单
- risk deny 不是真实下单失败
- risk deny 没有连接真实交易所
- risk deny 没有真实下单
- risk deny 没有真实资金变化
- risk deny 没有真实仓位变化

P6-D9 不接真实交易所 API。
P6-D9 不保存真实 API key。
P6-D9 不读取钱包私钥。
P6-D9 不真实下单。


## P6-D10：Dify Paper Execution Response Smoke Includes Risk Deny

P6-D10 新增：

- docs/58_p6_dify_paper_execution_response_smoke_risk_deny.md

P6-D10 修改：

- scripts/run_dify_paper_execution_response_smoke.py
- tests/test_dify_paper_execution_response_smoke.py

当前 response smoke 覆盖：

- fill -> paper_fill_success
- reject -> paper_reject_success
- policy deny -> paper_policy_deny
- risk deny -> paper_risk_deny
- bad order -> paper_execution_error
- real execution intent -> paper_safety_refusal

P6-D10 明确区分：

- policy_deny 不是交易所真实拒单
- risk_deny 不是交易所真实拒单
- execution_error 不是实盘下单失败
- safety_refusal 不调用 adapter

P6-D10 不接真实交易所 API。
P6-D10 不保存真实 API key。
P6-D10 不读取钱包私钥。
P6-D10 不真实下单。


## P6-D11：Phase 6 Policy / Risk Deny Acceptance

P6-D11 新增：

- docs/59_p6_policy_risk_deny_acceptance.md

P6-D11 汇总验收 Phase 6 policy / risk deny hardening 成果：

- policy gate
- policy gate API integration
- paper_policy_deny user-facing response
- policy deny smoke coverage
- risk guardian
- risk guardian API integration
- paper_risk_deny user-facing response
- risk deny smoke coverage
- Dify response smoke 全分支覆盖

当前 Dify response smoke 覆盖：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny
- paper_execution_error
- paper_safety_refusal

当前验证：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 235 passed


## P6-D12：Phase 6 Closeout

P6-D12 新增：

- docs/60_p6_closeout_project_state.md

Phase 6 已完成阶段收尾。

当前完成范围：

- policy / risk deny case hardening
- paper execution policy gate
- policy gate API integration
- paper_policy_deny user-facing response
- Dify response smoke policy deny coverage
- paper execution risk guardian
- risk guardian API integration
- paper_risk_deny user-facing response
- Dify response smoke risk deny coverage
- Dify response smoke 全分支覆盖

当前 Dify response smoke 覆盖：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny
- paper_execution_error
- paper_safety_refusal

当前验证：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_smoke.py 输出 status completed
- python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed
- python -m pytest -q 显示 235 passed

下一步建议：

- P7-D1：Multi-asset guarded paper execution fixture plan

继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不允许 Dify 绕过 policy / risk
- 不把 paper execution 伪装成 real execution


## P7-D1：Multi-asset Guarded Paper Execution Fixture Plan

P7-D1 新增：

- docs/61_p7_multi_asset_guarded_paper_execution_fixture_plan.md

P7-D1 开始 Phase 7。

Phase 7 目标：

- 将 guarded paper execution 扩展到 multi-asset fixture
- 覆盖 crypto / equities / fx / commodities
- 明确 raw_order 样例
- 明确 risk_context 样例
- 明确 fill success / sandbox reject / policy deny / risk deny 分支
- 为后续 multi-asset guarded paper execution smoke 做准备

P7-D1 不接真实交易所 API。
P7-D1 不保存真实 API key。
P7-D1 不读取钱包私钥。
P7-D1 不真实下单。


## P7-D2：Multi-asset Guarded Paper Execution Fixture

P7-D2 新增：

- docs/62_p7_multi_asset_guarded_paper_execution_fixture.md
- fixtures/paper_orders_multi_asset_guarded.json
- tests/test_multi_asset_guarded_paper_fixture.py

当前 fixture 覆盖：

- crypto
- equities
- fx
- commodities

每个资产类别覆盖：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

P7-D2 明确：

- fill_success 会进入 sandbox execution 并生成 sandbox event
- sandbox_reject 会进入 sandbox execution 并生成 sandbox rejected event
- policy_deny 不进入 sandbox execution，不生成 sandbox event
- risk_deny 不进入 sandbox execution，不生成 sandbox event
- sandbox reject 不是交易所真实拒单
- policy deny / risk deny 不是交易所真实拒单
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单


## P7-D3：Multi-asset Guarded Paper Execution Smoke Runner

P7-D3 新增：

- docs/63_p7_multi_asset_guarded_paper_execution_smoke_runner.md
- scripts/run_multi_asset_guarded_paper_execution_smoke.py
- tests/test_multi_asset_guarded_paper_execution_smoke_runner.py

当前 smoke runner 会读取：

- fixtures/paper_orders_multi_asset_guarded.json

并逐条调用：

- handle_paper_execution

覆盖：

- crypto / equities / fx / commodities
- fill_success / sandbox_reject / policy_deny / risk_deny

P7-D3 明确：

- runner 输出 status completed
- fixture 共 16 个 case
- 16 个 case 必须全部 passed
- policy_deny / risk_deny 不生成 sandbox execution event
- sandbox reject 不是交易所真实拒单
- policy deny / risk deny 不是交易所真实拒单
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单


## P7-D4：Dify Response Integration for Guarded Paper Fixture Smoke

P7-D4 新增：

- docs/64_p7_guarded_paper_execution_dify_response_smoke.md
- scripts/run_multi_asset_guarded_paper_execution_response_smoke.py
- tests/test_multi_asset_guarded_paper_execution_response_smoke.py

当前 smoke runner 会读取：

- fixtures/paper_orders_multi_asset_guarded.json

并通过 Dify paper execution adapter 调用：

- route_dify_paper_execution_request
- ROUTE_EXECUTE

然后使用：

- render_paper_execution_user_response

把结果转成用户可见响应。

覆盖：

- crypto / equities / fx / commodities
- fill_success / sandbox_reject / policy_deny / risk_deny

P7-D4 明确：

- fill_success 转成 paper_fill_success
- sandbox_reject 转成 paper_reject_success
- policy_deny 转成 paper_policy_deny
- risk_deny 转成 paper_risk_deny
- 所有用户响应都不能声称真实成交
- sandbox reject 不是交易所真实拒单
- policy deny / risk deny 不是交易所真实拒单
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单


## P7-D5：Guarded Paper Execution Phase Acceptance

P7-D5 新增：

- docs/65_p7_guarded_paper_execution_acceptance.md
- tests/test_p7_guarded_paper_execution_acceptance.py

P7-D5 汇总验收：

- P7-D1 multi-asset guarded paper fixture plan
- P7-D2 multi-asset guarded paper execution fixture
- P7-D3 multi-asset guarded paper execution smoke runner
- P7-D4 Dify response integration for guarded paper fixture smoke

当前覆盖：

- crypto / equities / fx / commodities
- fill_success / sandbox_reject / policy_deny / risk_deny
- paper_fill_success / paper_reject_success / paper_policy_deny / paper_risk_deny

P7-D5 明确：

- policy deny / risk deny 不进入 sandbox execution
- policy deny / risk deny 不生成 sandbox execution event
- sandbox fill 不是真实成交
- sandbox reject 不是交易所真实拒单
- PolicyDeny / RiskDeny 不是交易所真实拒单
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单


## P7-D6：Guarded Paper Execution Acceptance Smoke Runner

P7-D6 新增：

- docs/66_p7_guarded_paper_execution_acceptance_smoke_runner.md
- scripts/run_p7_guarded_paper_execution_acceptance_smoke.py
- tests/test_p7_guarded_paper_execution_acceptance_smoke.py

P7-D6 汇总验收：

- P7-D2 multi-asset guarded paper execution fixture
- P7-D3 multi-asset guarded paper execution smoke runner
- P7-D4 Dify response integration for guarded paper fixture smoke
- P7-D5 guarded paper execution phase acceptance

当前 runner 输出：

- status
- acceptance_summary
- artifact_checks
- execution_smoke_summary
- response_smoke_summary
- safe_boundary

P7-D6 明确：

- status 必须为 completed
- 16 个 fixture case 必须全部通过
- crypto / equities / fx / commodities 覆盖完整
- fill_success / sandbox_reject / policy_deny / risk_deny 覆盖完整
- paper_fill_success / paper_reject_success / paper_policy_deny / paper_risk_deny 覆盖完整
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单


## P7-D7：Phase 7 Closeout

P7-D7 新增：

- docs/67_p7_closeout_project_state.md
- tests/test_p7_closeout_project_state.py

P7-D7 汇总：

- P7-D1 multi-asset guarded paper fixture plan
- P7-D2 multi-asset guarded paper execution fixture
- P7-D3 multi-asset guarded paper execution smoke runner
- P7-D4 Dify response integration for guarded paper fixture smoke
- P7-D5 guarded paper execution phase acceptance
- P7-D6 guarded paper execution acceptance smoke runner

Phase 7 guarded paper execution 第一轮已完成阶段收尾。

当前覆盖：

- crypto / equities / fx / commodities
- fill_success / sandbox_reject / policy_deny / risk_deny
- paper_fill_success / paper_reject_success / paper_policy_deny / paper_risk_deny

当前安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不允许绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- sandbox fill 不是真实成交
- sandbox reject 不是交易所真实拒单
- PolicyDeny / RiskDeny 不是交易所真实拒单


## P7-D8：Post-closeout Guarded Paper Execution Regression Summary

P7-D8 新增：

- docs/68_p7_guarded_paper_execution_regression_summary.md
- scripts/run_p7_guarded_paper_execution_regression_summary.py
- tests/test_p7_guarded_paper_execution_regression_summary.py

P7-D8 汇总当前所有 smoke runner：

- Dify HTTP adapter smoke
- Dify integration smoke
- multi-asset Dify smoke
- multi-asset Dify error smoke
- Dify paper execution smoke
- Dify paper execution response smoke
- multi-asset guarded paper execution smoke
- multi-asset guarded paper execution response smoke
- P7 guarded paper execution acceptance smoke

当前 regression summary 输出：

- status
- smoke_count
- completed_count
- failed_count
- smoke_results
- guarded_summary
- regression_summary
- safe_boundary

P7-D8 明确：

- 9 个 smoke runner 必须全部 completed
- guarded execution 16 个 case 必须全部通过
- guarded response 16 个 case 必须全部通过
- Phase 7 第一轮回归通过后可进入 Phase 8 规划
- 不接真实交易所 API
- 不真实下单
- 不把 paper execution 伪装成 real execution


## P7-D9：Phase 7 to Phase 8 Bridge Plan

P7-D9 新增：

- docs/69_p7_to_p8_bridge_plan.md
- tests/test_p7_to_p8_bridge_plan.py

P7-D9 完成 Phase 7 到 Phase 8 的桥接规划。

Phase 8 建议主题：

- Portfolio-level guarded paper execution

Phase 8 候选方向：

- portfolio-level guarded paper execution
- cross-asset exposure checks
- portfolio-level user-facing response
- regression CI entrypoint

P7-D9 建议下一步：

- P8-D1：Portfolio-level guarded paper execution plan

P7-D9 明确：

- Phase 8 第一轮仍不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响


## P8-D1：Portfolio-level Guarded Paper Execution Plan

P8-D1 新增：

- docs/70_p8_portfolio_guarded_paper_execution_plan.md
- tests/test_p8_portfolio_guarded_paper_execution_plan.py

P8-D1 启动 Phase 8。

Phase 8 建议主题：

- Portfolio-level guarded paper execution

P8-D1 明确：

- portfolio 输入结构
- portfolio 输出结构
- portfolio 分支规划
- portfolio-level policy 候选规则
- portfolio-level risk 候选规则
- cross-asset exposure checks
- portfolio user-facing response 规划
- regression / CI 入口规划
- Phase 8 第一轮安全边界

P8-D1 只做规划文档。
不改核心执行逻辑。
不接真实交易所 API。
不真实下单。


## P8-D2：Portfolio Paper Order Fixture

P8-D2 新增：

- docs/71_p8_portfolio_paper_order_fixture.md
- fixtures/paper_order_portfolios_multi_asset.json
- tests/test_portfolio_paper_order_fixture.py

当前 portfolio fixture 覆盖：

- portfolio_all_fill
- portfolio_mixed_results
- portfolio_policy_deny
- portfolio_risk_deny

当前资产类别覆盖：

- crypto
- equities
- fx
- commodities

当前 order 分支覆盖：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny
- blocked_by_portfolio_policy
- blocked_by_portfolio_risk

P8-D2 只新增 fixture 和 fixture schema 测试。
不接真实交易所 API。
不真实下单。


## P8-D3：Portfolio Paper Execution API Wrapper

P8-D3 新增：

- docs/72_p8_portfolio_paper_execution_api_wrapper.md
- fcf/api/portfolio_paper_execution_api.py
- tests/test_portfolio_paper_execution_api.py

新增 API 入口：

- handle_portfolio_paper_execution

当前能力：

- 读取 portfolio request
- portfolio-level policy deny
- portfolio-level risk deny
- 逐笔调用 handle_paper_execution
- 汇总 filled_count
- 汇总 sandbox_rejected_count
- 汇总 policy_denied_count
- 汇总 risk_denied_count
- 汇总 asset_class_counts
- 汇总 branch_counts
- 汇总 total_notional
- 汇总 notional_by_asset_class
- 返回稳定 response dict

P8-D3 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实资金影响


## P8-D4：Portfolio-level Risk Exposure Checks

P8-D4 新增：

- docs/73_p8_portfolio_risk_guardian.md
- fcf/policy/portfolio_risk_guardian.py
- tests/test_portfolio_risk_guardian.py

新增入口：

- evaluate_portfolio_risk_guardian

当前覆盖：

- max_order_count
- max_total_notional
- max_asset_class_notional
- blocked_asset_classes
- blocked_symbols
- duplicate_order_keys
- max_same_side_count
- max_single_order_notional

P8-D4 同时让 portfolio_paper_execution_api 使用独立 portfolio risk guardian。

P8-D4 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实资金影响


## P8-D5：Portfolio Paper Execution User-facing Response Templates

P8-D5 新增：

- docs/74_p8_portfolio_paper_execution_response_templates.md
- fcf/api/portfolio_paper_execution_response_templates.py
- tests/test_portfolio_paper_execution_response_templates.py

新增入口：

- render_portfolio_paper_execution_user_response

当前覆盖用户响应：

- portfolio_paper_success
- portfolio_paper_partial_success
- portfolio_policy_deny
- portfolio_risk_deny
- portfolio_schema_error

P8-D5 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不声明真实成交或真实资金影响。


## P8-D6：Portfolio Guarded Paper Execution Smoke Runner

P8-D6 新增：

- docs/75_p8_portfolio_guarded_paper_execution_smoke_runner.md
- scripts/run_portfolio_guarded_paper_execution_smoke.py
- tests/test_portfolio_guarded_paper_execution_smoke.py

runner 读取 fixtures/paper_order_portfolios_multi_asset.json，调用 handle_portfolio_paper_execution 和 render_portfolio_paper_execution_user_response。

当前覆盖：

- portfolio_all_fill
- portfolio_mixed_results
- portfolio_policy_deny
- portfolio_risk_deny

P8-D6 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。


## P8-D7：Portfolio Guarded Paper Execution Acceptance

P8-D7 新增：

- docs/76_p8_portfolio_guarded_paper_execution_acceptance.md
- tests/test_p8_portfolio_guarded_paper_execution_acceptance.py

P8-D7 汇总验收 P8-D1 到 P8-D6。

当前 portfolio smoke 输出 status completed，覆盖 portfolio_all_fill、portfolio_mixed_results、portfolio_policy_deny、portfolio_risk_deny。

P8-D7 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。


## P8-D8：Phase 8 Closeout

P8-D8 新增：

- docs/77_p8_closeout_project_state.md
- tests/test_p8_closeout_project_state.py

P8-D8 完成 Phase 8 portfolio guarded paper execution 第一轮阶段收尾。

当前覆盖：

- portfolio_all_fill
- portfolio_mixed_results
- portfolio_policy_deny
- portfolio_risk_deny
- portfolio_paper_success
- portfolio_paper_partial_success
- portfolio_policy_deny
- portfolio_risk_deny

P8-D8 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。


## P8-D9：Post-closeout Portfolio Guarded Paper Regression Summary

P8-D9 新增：

- docs/78_p8_portfolio_guarded_paper_regression_summary.md
- scripts/run_p8_portfolio_guarded_paper_regression_summary.py
- tests/test_p8_portfolio_guarded_paper_regression_summary.py

P8-D9 汇总 P7 regression 与 P8 portfolio smoke，并输出 ready_for_phase9_planning。

P8-D9 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。


## P8-D10：Phase 8 to Phase 9 Bridge Plan

P8-D10 新增：

- docs/79_p8_to_p9_bridge_plan.md
- tests/test_p8_to_p9_bridge_plan.py

P8-D10 完成 Phase 8 到 Phase 9 的桥接规划。

Phase 9 建议主题：

- Global paper-only regression suite and CI-safe operational readiness

Phase 9 候选方向：

- 统一 smoke / regression 入口
- P7 regression summary
- P8 portfolio regression summary
- 全局 safe_boundary 校验
- machine-readable regression report
- CI-safe entrypoint
- 项目状态一致性检查

P8-D10 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

## P9-D1：Global Regression Suite Plan

P9-D1 新增：

- docs/80_p9_global_regression_suite_plan.md
- tests/test_p9_global_regression_suite_plan.py

P9-D1 启动 Phase 9。

Phase 9 建议主题：

- Global paper-only regression suite and CI-safe operational readiness

Phase 9 第一轮目标：

- 统一 smoke / regression 入口
- 汇总 P7 regression summary
- 汇总 P8 portfolio regression summary
- machine-readable regression report
- 全局 safe_boundary checker
- PROJECT_STATE / README consistency checker
- CI-safe regression command document

P9-D1 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

## P9-D2：run_all_smokes Entrypoint

P9-D2 新增：

- docs/81_p9_run_all_smokes_entrypoint.md
- scripts/run_all_smokes.py
- tests/test_p9_run_all_smokes_entrypoint.py

新增命令：

- python scripts/run_all_smokes.py

当前汇总：

- P7 guarded paper execution regression summary
- P8 portfolio guarded paper regression summary

输出 status、suites、counts、readiness、safe_boundary。

P9-D2 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

## P9-D3：Global Regression Report Schema

P9-D3 新增：

- docs/82_p9_global_regression_report_schema.md
- fcf/regression/__init__.py
- fcf/regression/global_regression_report_schema.py
- tests/test_p9_global_regression_report_schema.py

新增入口：

- build_global_regression_report

该入口把 python scripts/run_all_smokes.py 的输出转成 machine-readable global regression report。

输出字段：

- report_version
- generated_by
- phase
- status
- source_runner
- suites
- counts
- readiness
- safe_boundary
- report_path
- next_action

P9-D3 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

## P9-D4：Global Safe Boundary Checker

P9-D4 新增：

- docs/83_p9_global_safe_boundary_checker.md
- fcf/regression/global_safe_boundary_checker.py
- tests/test_p9_global_safe_boundary_checker.py

新增入口：

- check_global_safe_boundary

该入口验证 global regression report 或 safe_boundary dict 是否保持 paper-only 安全边界。

P9-D4 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

## P9-D5：PROJECT_STATE / README Consistency Checker

P9-D5 新增：

- docs/84_p9_project_state_consistency_checker.md
- fcf/regression/project_state_consistency_checker.py
- tests/test_p9_project_state_consistency_checker.py

新增入口：

- check_project_state_consistency

该入口验证 README.md 与 PROJECT_STATE.md 的阶段记录、安全边界、下一步记录是否一致。

当前要求 README.md 与 PROJECT_STATE.md 均包含：

- P9-D1 到 P9-D5
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响
- 下一步 P9-D6：CI-safe regression command document

P9-D5 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

## P9-D6：CI-safe Regression Command Document

P9-D6 新增：

- docs/85_p9_ci_safe_regression_command_document.md
- tests/test_p9_ci_safe_regression_command_document.py

当前本地推荐命令：

- python main.py
- python scripts/run_all_smokes.py
- python -m pytest -q

当前 CI 推荐命令：

- python scripts/run_all_smokes.py
- python -m pytest -q

CI 不需要 exchange API key、wallet private key、real account credentials、real broker credentials、CI secret 或 production deployment permission。

P9-D6 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响。

下一步：

P9-D7：Phase 9 acceptance smoke。

## P9-D7：Phase 9 Acceptance Smoke

P9-D7 新增：

- docs/86_p9_acceptance_smoke.md
- scripts/run_p9_acceptance_smoke.py
- tests/test_p9_acceptance_smoke.py

新增命令：

- python scripts/run_p9_acceptance_smoke.py

P9-D7 汇总验证 run_all_smokes、build_global_regression_report、check_global_safe_boundary、check_project_state_consistency。

验收输出 ready_for_p9_d8_closeout=true。

P9-D7 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响。

下一步：

P9-D8：Phase 9 closeout。

## P9-D8：Phase 9 Closeout

P9-D8 新增：

- docs/87_p9_closeout_project_state.md
- tests/test_p9_closeout_project_state.py

P9-D8 完成 Phase 9：Global paper-only regression suite and CI-safe operational readiness 第一轮阶段收尾。

当前全局命令：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_acceptance_smoke.py
- python -m pytest -q

P9-D8 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响。

下一步：

P9-D9：post-closeout global regression summary，或者进入 Phase 10 规划。

## P9-D9：Post-closeout Global Regression Summary

P9-D9 新增：

- docs/88_p9_post_closeout_global_regression_summary.md
- scripts/run_p9_global_regression_summary.py
- tests/test_p9_global_regression_summary.py

新增命令：

- python scripts/run_p9_global_regression_summary.py

P9-D9 汇总 run_all_smokes、run_p9_acceptance_smoke、build_global_regression_report、check_global_safe_boundary、check_project_state_consistency 和 P9 closeout doc。

验收输出 ready_for_phase10_planning=true。

P9-D9 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响。

下一步：

P9-D10：Phase 9 to Phase 10 bridge plan。

## P9-D10：Phase 9 to Phase 10 Bridge Plan

P9-D10 新增：

- docs/89_p9_to_p10_bridge_plan.md
- tests/test_p9_to_p10_bridge_plan.py

P9-D10 完成 Phase 9 到 Phase 10 的桥接规划。

Phase 10 建议主题：

- Dify-safe paper operations packaging and operator review readiness

Phase 10 候选方向：

- Dify-safe global regression adapter
- paper-only operator runbook
- response templates for global regression status
- operator review checklist
- failure triage guide
- Dify workflow node contract
- handoff package for non-production paper-only use
- Phase 10 acceptance smoke

P9-D10 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单。

下一步：

P10-D1：Dify-safe paper operations plan。

## P10-D1：Dify-safe Paper Operations Plan

P10-D1 新增：

- docs/90_p10_dify_safe_paper_operations_plan.md
- tests/test_p10_dify_safe_paper_operations_plan.py

P10-D1 启动 Phase 10。

Phase 10 主题：

- Dify-safe paper operations packaging and operator review readiness

Phase 10 第一轮目标：

- Dify-safe global regression adapter
- operator review response templates
- paper-only operator runbook
- failure triage guide
- Dify workflow node contract document
- handoff package for non-production paper-only use
- Phase 10 acceptance smoke

P10-D1 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D2：global regression Dify adapter contract。

## P10-D2：Global Regression Dify Adapter Contract

P10-D2 新增：

- docs/91_p10_global_regression_dify_adapter_contract.md
- fcf/api/dify_global_regression_api.py
- tests/test_p10_global_regression_dify_adapter_contract.py

新增入口：

- handle_dify_global_regression_request

该入口是 Dify-safe global regression adapter，只允许调用现有 paper-only regression runner。

P10-D2 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D3：operator review response templates。

## P10-D3：Operator Review Response Templates

P10-D3 新增：

- docs/92_p10_operator_review_response_templates.md
- fcf/api/operator_review_response_templates.py
- tests/test_p10_operator_review_response_templates.py

新增入口：

- render_operator_review_response

覆盖 response_type：

- global_regression_passed
- global_regression_failed
- safe_boundary_failed
- project_state_inconsistent
- operator_review_required

所有响应明确这是 paper-only / non-production 响应，不是真实交易信号，不是真实下单结果，不是真实成交结果，需要人工复核。

P10-D3 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D4：paper-only operator runbook。

## P10-D4：Paper-only Operator Runbook

P10-D4 新增：

- docs/93_p10_paper_only_operator_runbook.md
- tests/test_p10_paper_only_operator_runbook.py

runbook 明确 operator 如何运行：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_acceptance_smoke.py
- python scripts/run_p9_global_regression_summary.py
- python -m pytest -q

runbook 明确 status、safe_boundary、operator_review_required 和 failed 处理规则。

P10-D4 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D5：failure triage guide。

## P10-D5：Failure Triage Guide

P10-D5 新增：

- docs/94_p10_failure_triage_guide.md
- tests/test_p10_failure_triage_guide.py

failure triage guide 覆盖：

- pytest failed
- smoke failed
- safe_boundary failed
- project state consistency failed
- Dify adapter input invalid
- response template mismatch

所有 failed 都必须停止继续操作，不进入下一阶段，不解释为交易信号，不连接真实交易所，不配置 API key，不读取钱包私钥，不尝试真实下单。

P10-D5 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D6：Dify workflow node contract document。

## P10-D6：Dify Workflow Node Contract Document

P10-D6 新增：

- docs/95_p10_dify_workflow_node_contract.md
- tests/test_p10_dify_workflow_node_contract.py

Dify workflow 建议节点：

- Input validation node
- Global regression API node
- Safe boundary review node
- Operator response template node
- Human review node
- Final non-production output node

P10-D6 明确 Dify workflow 只允许 paper-only / non-production / operator review / safe boundary review，不允许真实交易所 API、真实下单、真实账户读取、真实仓位读取、自动实盘交易、自动绕过人工复核、绕过 policy / risk / safe_boundary。

下一步：

P10-D7：Phase 10 acceptance smoke。

## P10-D7：Phase 10 Acceptance Smoke

P10-D7 新增：

- docs/96_p10_acceptance_smoke.md
- scripts/run_p10_acceptance_smoke.py
- tests/test_p10_acceptance_smoke.py

新增命令：

- python scripts/run_p10_acceptance_smoke.py

P10-D7 汇总 P9 global regression summary、Dify global regression adapter、operator review response templates、P10 docs readiness 和 safe_boundary。

验收输出 ready_for_p10_d8_closeout=true。

P10-D7 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D8：Phase 10 closeout。

## P10-D8：Phase 10 Closeout

P10-D8 新增：

- docs/97_p10_closeout_project_state.md
- tests/test_p10_closeout_project_state.py

P10-D8 完成 Phase 10：Dify-safe paper operations packaging and operator review readiness 第一轮阶段收尾。

当前完成能力：

- Dify-safe global regression adapter
- operator review response templates
- paper-only operator runbook
- failure triage guide
- Dify workflow node contract document
- Phase 10 acceptance smoke

当前全局命令：

- python main.py
- python scripts/run_all_smokes.py
- python scripts/run_p9_global_regression_summary.py
- python scripts/run_p10_acceptance_smoke.py
- python -m pytest -q

P10-D8 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D9：post-closeout Dify-safe paper operations package summary，或者 P10-D10：Phase 10 to Phase 11 bridge plan。

## P10-D9：Post-closeout Dify-safe Paper Operations Package Summary

P10-D9 新增：

- docs/98_p10_post_closeout_dify_safe_package_summary.md
- scripts/run_p10_dify_safe_package_summary.py
- tests/test_p10_dify_safe_package_summary.py

新增命令：

- python scripts/run_p10_dify_safe_package_summary.py

P10-D9 汇总 P10 closeout、P10 acceptance smoke、Dify-safe global regression adapter、operator review response templates、paper-only operator runbook、failure triage guide、Dify workflow node contract 和 paper-only safe boundary。

验收输出 ready_for_p10_d10_bridge_plan=true。

P10-D9 继续保持 paper-only 安全边界：不接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，不读取真实账户余额，不读取真实仓位，不声明真实成交，不声明真实资金影响，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P10-D10：Phase 10 to Phase 11 bridge plan。

## P10-D10：Phase 10 to Phase 11 Bridge Plan

P10-D10 新增：

- docs/99_p10_to_p11_bridge_plan.md
- tests/test_p10_to_p11_bridge_plan.py

P10-D10 完成 Phase 10 到 Phase 11 的桥接规划。

Phase 11 建议主题：

- Release readiness, operator handoff package, and long-term maintainability

Phase 11 候选方向：

- release readiness plan
- operator handoff package
- versioned run commands document
- artifact inventory
- maintenance checklist
- regression stability gate
- long-term safety boundary checklist
- Phase 11 acceptance smoke

P10-D10 继续保持 paper-only 安全边界，不接真实交易所 API，不真实下单，不自动绕过人工复核，不绕过 policy / risk / safe_boundary。

下一步：

P11-D1：Release readiness plan。
