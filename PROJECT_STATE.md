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

## Phase 3 已完成范围

P3-D1：真实数据接入边界规划，已完成。
P3-D2：mock market data adapter，已完成。
P3-D3：replayable raw market fixture，已完成。
P3-D4：本地 system input pipeline / 外部调用边界，已完成。
P3-D5：Dify workflow integration plan，已完成。
P3-D6：local_market_input_api wrapper，已完成。
P3-D7：Dify API contract examples，已完成。
P3-D8：Dify workflow HTTP/API node mapping，已完成。
P3-D9：Dify local HTTP adapter，已完成。
P3-D10：Dify HTTP adapter smoke runner，已完成。
P3-D11：Dify user-facing response templates，已完成。
P3-D12：Dify adapter response integration smoke，已完成。
P3-D13：Phase 3 Dify integration acceptance，已完成。
P3-D13 fix：smoke runner direct script import fix，已完成。
P3-D14：Phase 3 closeout / project state consolidation，已完成。

## 当前关键代码

- fcf/api/local_market_input_api.py
- fcf/api/dify_http_adapter.py
- fcf/api/dify_response_templates.py
- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py

## 当前关键测试

- tests/test_local_market_input_api.py
- tests/test_dify_http_adapter.py
- tests/test_dify_http_adapter_smoke_runner.py
- tests/test_dify_response_templates.py
- tests/test_dify_integration_smoke.py

## 当前关键文档

- docs/16_dify_workflow_integration_plan.md
- docs/17_dify_api_contract_examples.md
- docs/18_dify_workflow_http_api_node_mapping.md
- docs/19_dify_local_http_adapter.md
- docs/20_dify_http_adapter_smoke_runner.md
- docs/21_dify_user_facing_response_templates.md
- docs/22_dify_adapter_response_integration_smoke.md
- docs/23_phase3_dify_integration_acceptance.md
- docs/24_phase3_closeout_project_state.md

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

python -m pytest -q

预期输出：

- 73 passed

## 安全边界

Dify 不作为底层交易内核。
Dify 不直接接真实交易所 API。
Dify 不保存真实 API key。
Dify 不读取钱包私钥。
Dify 不真实下单。
Dify 只调用受控 API wrapper / pipeline。
Dify 不把 pipeline 成功伪装成真实交易成功。

## Phase 4 候选方向

Phase 4 可以从以下方向选择：

1. Schema hardening
2. Multi-asset fixture expansion
3. Paper-only sandbox execution boundary
4. Dify workflow export template
5. Stronger risk / policy test cases

建议下一步进入：

P4-D1：Schema hardening plan。

目标：

- 新增 schema hardening 文档
- 明确 raw market input 的必填字段
- 明确可选字段
- 明确类型转换规则
- 明确多资产字段兼容策略
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 执行 git rev-parse --short HEAD 后填写
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成，D1-D11 已完成。Phase 2 多资产 MarketContext 基础层已完成，P2-D1 到 P2-D10 已完成。Phase 3 数据接入与 Dify integration 已完成阶段收尾，P3-D1 到 P3-D14 已完成。当前不是足球系统，也不是 BTC-only。BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。
当前能力：local_market_input_api、dify_http_adapter、dify_response_templates、Dify HTTP adapter smoke runner、Dify integration smoke 均已完成。当前验证：python main.py 输出 events_recorded: 8；python scripts/run_dify_http_adapter_smoke.py 输出 status completed；python scripts/run_dify_integration_smoke.py 输出 status completed；python -m pytest -q 预计显示 73 passed。
安全边界：Dify 不作为底层交易内核，不直接接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，只调用受控 API wrapper / pipeline，不把 pipeline 成功伪装成真实交易成功。
next_action: 进入 P4-D1：Schema hardening plan。新增 schema hardening 文档，明确 raw market input 的必填字段、可选字段、类型转换规则、多资产字段兼容策略。不接真实交易所 API，不真实下单，不破坏现有测试。
要求：全程中文一步步指挥；命令必须是可直接复制的 Git Bash 格式；多行 cat 必须包含完整 EOF；每次重要更新都 commit 并 push，并更新新的续聊话术。


## P4-D1 完成记录

P4-D1：Schema hardening plan 已完成。

新增文件：

- docs/25_p4_schema_hardening_plan.md

完成内容：

- 明确 raw market input 必填字段
- 明确 raw market input 可选字段
- 明确类型转换规则
- 明确 market_type 归一化规则
- 明确 asset_class 多资产兼容策略
- 明确错误响应要求
- 明确 Dify 接入安全边界
- 明确 P4-D2 下一步实现方向

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 73 passed

下一步：

进入 P4-D2：raw market input schema module。

建议新增：

- fcf/schemas/raw_market_input_schema.py
- tests/test_raw_market_input_schema.py

P4-D2 目标：

- 实现 required field check
- 实现 optional field normalize
- 实现 number conversion
- 实现 market_type normalization
- 实现 asset_class normalization
- 保持 local_market_input_api 返回稳定 response dict
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P4-D2 完成记录

P4-D2：raw market input schema module 已完成。

新增文件：

- fcf/schemas/__init__.py
- fcf/schemas/raw_market_input_schema.py
- tests/test_raw_market_input_schema.py

完成内容：

- 实现 describe_schema
- 实现 check_required_fields
- 实现 normalize_asset_class
- 实现 normalize_market_type
- 实现 to_float_field
- 实现 normalize_raw_market_input
- 实现 validate_raw_market_input
- 增加 pytest 覆盖

当前 schema 能力：

- 必填字段检查
- 字符串字段归一化
- 数字字段转换
- market_type 归一化
- asset_class 归一化
- last_price 正数校验
- volume / quote_volume / depth 非负校验
- best_bid <= best_ask 校验

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 84 passed

下一步：

进入 P4-D3：integrate raw market input schema into market input pipeline。

建议目标：

- 在 market_input_pipeline 或 mock adapter 边界调用 normalize_raw_market_input
- 保持 local_market_input_api 的稳定 response dict
- 增加 integration tests
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P4-D3 完成记录

P4-D3：integrate raw market input schema into market input pipeline 已完成。

新增文件：

- docs/26_p4_schema_pipeline_integration.md
- tests/test_market_input_pipeline_schema_integration.py

修改文件：

- fcf/pipelines/market_input_pipeline.py

完成内容：

- process_raw_market_input 调用 normalize_raw_market_input
- process_raw_market_batch 调用 normalize_raw_market_input
- pipeline 返回 schema 和 schema_version
- single input 支持 schema normalization
- batch input 支持 schema normalization
- schema 错误保持 ValueError
- local_market_input_api 继续包装为稳定 response dict

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 87 passed

下一步：

进入 P4-D4：schema-aware Dify adapter and response tests。

建议目标：

- 增加 Dify HTTP adapter 对 schema error 的测试
- 增加 Dify response templates 对 schema error 的测试
- 确认 bad spread / missing required / bad market_type 均能稳定返回
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P4-D4 完成记录

P4-D4：schema-aware Dify adapter and response tests 已完成。

新增文件：

- docs/27_p4_schema_aware_dify_adapter_response_tests.md
- tests/test_schema_aware_dify_adapter_response.py

完成内容：

- 增加 Dify adapter schema success 测试
- 增加 missing required field 422 测试
- 增加 bad market_type 422 测试
- 增加 bad spread 422 测试
- 增加 bad asset_class 422 测试
- 增加 schema error 到 user-facing error response 的测试

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 92 passed

下一步：

进入 P4-D5：schema error catalog and stable error messages。

建议目标：

- 增加 schema error catalog 文档
- 明确 missing field / invalid enum / invalid number / invalid price / invalid spread 的稳定错误格式
- 可考虑新增轻量错误类型常量
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P4-D5 完成记录

P4-D5：schema error catalog and stable error messages 已完成。

新增文件：

- docs/28_p4_schema_error_catalog.md
- fcf/schemas/schema_error_catalog.py
- tests/test_schema_error_catalog.py

完成内容：

- 新增 schema error catalog
- 新增 MissingField
- 新增 InvalidEnumValue
- 新增 InvalidNumber
- 新增 InvalidPositiveNumber
- 新增 InvalidNonNegativeNumber
- 新增 InvalidSpread
- 新增 InvalidPayloadType
- 新增稳定 error message builder
- 增加 pytest 覆盖

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 102 passed

下一步：

进入 P4-D6：integrate schema error catalog into raw market input schema。

建议目标：

- raw_market_input_schema 使用 schema_error_catalog 的 message builder
- 保持现有错误 message 兼容
- 保持 Dify adapter 422 行为
- 保持 response templates error 行为
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P4-D6 完成记录

P4-D6：integrate schema error catalog into raw market input schema 已完成。

新增文件：

- docs/29_p4_integrate_schema_error_catalog.md
- tests/test_raw_market_input_schema_error_catalog_integration.py

修改文件：

- fcf/schemas/raw_market_input_schema.py

完成内容：

- raw_market_input_schema 使用 schema_error_catalog message builder
- missing required field 使用 missing_fields_message
- invalid enum 使用 invalid_enum_message
- invalid number 使用 invalid_number_message
- invalid positive number 使用 invalid_positive_number_message
- invalid non-negative number 使用 invalid_non_negative_number_message
- invalid spread 使用 invalid_spread_message
- invalid payload type 使用 invalid_payload_type_message
- 保持现有错误 message 兼容
- 保持 Dify adapter 422 行为

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 110 passed

下一步：

进入 P4-D7：schema batch error behavior and Dify batch tests。

建议目标：

- 增加 batch 中单行 schema error 的测试
- 明确 batch 遇到错误时整体失败还是部分成功
- 当前建议整体失败并返回稳定 422
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试


## P4-D7 完成记录

P4-D7：schema batch error behavior and Dify batch tests 已完成。

新增文件：

- docs/30_p4_schema_batch_error_behavior.md
- tests/test_schema_batch_dify_adapter_errors.py

完成内容：

- 明确 batch 中任意一行 schema 错误则整体失败
- 明确不做部分成功
- 明确 batch schema error 返回 422
- 明确 batch schema error 可转成 user-facing error response
- 增加 batch success schema normalization 测试
- 增加 batch missing required field 测试
- 增加 batch bad market_type 测试
- 增加 batch bad spread 测试
- 增加 batch bad asset_class 测试
- 增加 batch bad number 测试

当前验证预期：

- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python -m pytest -q 显示 116 passed

下一步：

进入 P4-D8：schema hardening closeout and Phase 4 midpoint acceptance。

建议目标：

- 汇总 P4-D1 到 P4-D7 的 schema hardening 成果
- 明确当前 raw market input schema 能力
- 明确 Dify adapter schema error 行为
- 明确 batch error 行为
- 更新 README 和 PROJECT_STATE
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

