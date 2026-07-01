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

