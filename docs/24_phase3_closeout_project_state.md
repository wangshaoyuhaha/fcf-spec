# P3-D14 - Phase 3 Closeout / Project State Consolidation

## 1. 目的

P3-D14 用于收尾 Phase 3，并统一 README、PROJECT_STATE 和新聊天续接信息。

Phase 3 当前重点是：

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
- Dify response templates
- Dify integration smoke
- Phase 3 acceptance

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。

## 3. Phase 3 已完成范围

Phase 3 已完成：

- P3-D1：真实数据接入边界规划
- P3-D2：mock market data adapter
- P3-D3：replayable raw market fixture
- P3-D4：本地 system input pipeline / 外部调用边界
- P3-D5：Dify workflow integration plan
- P3-D6：local_market_input_api wrapper
- P3-D7：Dify API contract examples
- P3-D8：Dify workflow HTTP/API node mapping
- P3-D9：Dify local HTTP adapter
- P3-D10：Dify HTTP adapter smoke runner
- P3-D11：Dify user-facing response templates
- P3-D12：Dify adapter response integration smoke
- P3-D13：Phase 3 Dify integration acceptance
- P3-D13 fix：smoke runner direct script import fix
- P3-D14：Phase 3 closeout / project state consolidation

## 4. 当前代码能力

当前代码能力包括：

- FCFEvent
- EventStore
- ReplayEngine
- main.py 最小事件链
- 多资产 MarketContext 基础层
- mock market data adapter
- raw market fixture replay
- market input pipeline
- local_market_input_api
- dify_http_adapter
- dify_response_templates
- Dify smoke runner
- Dify integration smoke

## 5. 当前安全边界

当前系统保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不让 Dify 成为底层交易内核
- 不绕过 policy
- 不绕过 risk
- 不绕过 EventStore
- 不绕过 ReplayEngine
- 不把 pipeline 成功伪装成真实交易成功

## 6. 当前验收命令

当前主流程：

python main.py

预期：

events_recorded: 8

当前 Dify HTTP adapter smoke：

python scripts/run_dify_http_adapter_smoke.py

预期：

status completed

当前 Dify integration smoke：

python scripts/run_dify_integration_smoke.py

预期：

status completed

当前测试：

python -m pytest -q

预期：

73 passed

## 7. Phase 4 候选方向

Phase 4 建议候选方向：

1. Schema hardening
   - 为 raw market input 增加更严格 schema
   - 固化字段类型、必填字段、可选字段
   - 增加跨资产字段兼容规则

2. Multi-asset fixture expansion
   - 增加 equities fixture
   - 增加 fx fixture
   - 增加 commodities fixture
   - 增加 index fixture

3. Paper-only sandbox execution boundary
   - 只做 paper / sandbox
   - 不接真实交易所
   - 不真实下单
   - 明确 order proposal 与 execution boundary

4. Dify workflow export template
   - 设计 Dify workflow 节点配置模板
   - 仍只指向本地受控 adapter
   - 不接真实交易所 API key

5. Stronger risk / policy test cases
   - 增加拒绝交易样例
   - 增加异常市场输入样例
   - 增加 replay consistency 样例

## 8. P3-D14 验收结论

P3-D14 完成后，Phase 3 可以视为完成阶段性收尾。

当前系统仍是安全本地受控版本。
当前系统没有真实交易所连接。
当前系统没有真实下单能力。
当前 Dify integration 只是 workflow / API wrapper / response template 的安全接入骨架。

