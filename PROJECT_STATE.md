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

