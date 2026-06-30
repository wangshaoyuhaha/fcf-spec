# P3-D13 - Phase 3 Dify Integration Acceptance

## 1. 阶段目的

本文档用于验收 Phase 3 中 Dify integration 相关工作。

P3-D13 汇总 P3-D5 到 P3-D12 的成果：

- Dify workflow integration plan
- local API wrapper
- Dify API contract examples
- Dify workflow HTTP/API node mapping
- Dify local HTTP adapter
- Dify HTTP adapter smoke runner
- Dify user-facing response templates
- Dify adapter + response templates integration smoke

## 2. 项目定位确认

FCF Spec 当前定位为：

全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。

Dify 的定位是：

- 上层 workflow
- 对话入口
- 字段收集器
- 字段校验器
- 受控 API wrapper 调用方
- 用户可见 summary 展示层

Dify 不是：

- 底层交易内核
- 真实交易所连接器
- 真实订单执行器
- API key 存储器
- 风控绕过器

## 3. 已完成文档

Phase 3 Dify integration 已完成以下文档：

- docs/16_dify_workflow_integration_plan.md
- docs/17_dify_api_contract_examples.md
- docs/18_dify_workflow_http_api_node_mapping.md
- docs/19_dify_local_http_adapter.md
- docs/20_dify_http_adapter_smoke_runner.md
- docs/21_dify_user_facing_response_templates.md
- docs/22_dify_adapter_response_integration_smoke.md
- docs/23_phase3_dify_integration_acceptance.md

## 4. 已完成代码

Phase 3 Dify integration 已完成以下代码：

- fcf/api/local_market_input_api.py
- fcf/api/dify_http_adapter.py
- fcf/api/dify_response_templates.py
- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py

## 5. 已完成测试

Phase 3 Dify integration 已完成以下测试：

- tests/test_local_market_input_api.py
- tests/test_dify_http_adapter.py
- tests/test_dify_http_adapter_smoke_runner.py
- tests/test_dify_response_templates.py
- tests/test_dify_integration_smoke.py

## 6. 当前能力验收

当前已经具备：

- local_market_input_api 返回稳定 response dict
- response dict 包含 ok、api、api_version、error、data
- dify_http_adapter 返回稳定 http-style response dict
- 支持 GET /api/v1/contract
- 支持 POST /api/v1/market-input/single
- 支持 POST /api/v1/market-input/batch
- 支持 400 BadRequest
- 支持 404 NotFound
- 支持 405 MethodNotAllowed
- 支持 422 wrapper validation error
- smoke runner 可本地运行
- integration smoke 可本地运行
- 用户可见 response templates 已固化
- success / error / safety_refusal 已覆盖

## 7. 安全边界验收

Phase 3 Dify integration 明确禁止：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不把 pipeline 成功伪装成真实交易成功
- 不绕过 policy
- 不绕过 risk
- 不绕过 EventStore
- 不绕过 ReplayEngine
- 不让 Dify 成为底层交易内核

## 8. 当前验证命令

当前验收命令：

python main.py

预期：

events_recorded: 8

当前 smoke runner：

python scripts/run_dify_http_adapter_smoke.py
python scripts/run_dify_integration_smoke.py

预期：

status completed

当前测试：

python -m pytest -q

预期：

73 passed

## 9. P3-D13 验收结论

P3-D13 完成后，Phase 3 Dify integration 文档、wrapper、adapter、smoke runner、response templates、integration smoke 已形成最小闭环。

该闭环仍然是安全的本地受控链路。

它没有连接真实交易所。
它没有保存真实 API key。
它没有真实下单。
它没有改变底层交易执行边界。

## 10. 下一步建议

下一步进入 P3-D14：Phase 3 closeout / project state consolidation。

建议目标：

- 更新 README 当前阶段总结
- 更新 PROJECT_STATE 当前阶段总结
- 明确 Phase 3 已完成范围
- 明确 Phase 4 候选方向
- 保持 python main.py 通过
- 保持 python -m pytest -q 通过

