# P6-D12 - Phase 6 Closeout / Project State Consolidation

## 1. 目的

P6-D12 用于完成 Phase 6 的阶段收尾，并统一 README、PROJECT_STATE 和新聊天续接信息。

Phase 6 的重点是：

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

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。

当前系统仍然是本地安全受控开发版本。
当前系统不接真实交易所 API。
当前系统不保存真实 API key。
当前系统不读取钱包私钥。
当前系统不真实下单。

## 3. Phase 6 已完成范围

Phase 6 已完成：

- P6-D1：Policy and risk deny case hardening plan
- P6-D2：paper execution policy gate module
- P6-D3：integrate paper execution policy gate into paper execution API
- P6-D4：paper execution policy deny response templates
- P6-D5：Dify paper execution response smoke includes policy deny
- P6-D6：paper execution risk guardian module plan
- P6-D7：paper execution risk guardian module
- P6-D8：integrate risk guardian into paper execution API
- P6-D9：paper execution risk deny response templates
- P6-D10：Dify paper execution response smoke includes risk deny
- P6-D11：Phase 6 policy / risk deny acceptance
- P6-D12：Phase 6 closeout / project state consolidation

## 4. 当前核心执行顺序

当前 paper execution API 执行顺序：

1. policy gate
2. risk guardian
3. sandbox execution
4. EventStore
5. ReplayEngine
6. user-facing response templates

PolicyDeny 时：

- 返回 ok=false
- error.type=PolicyDeny
- 不进入 risk guardian
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 不真实下单

RiskDeny 时：

- 返回 ok=false
- error.type=RiskDeny
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 不真实下单

## 5. 当前关键代码

当前关键代码：

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
- fcf/policy/paper_execution_policy.py
- fcf/risk/paper_execution_risk_guardian.py

## 6. 当前关键 smoke runner

当前关键 smoke runner：

- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py
- scripts/run_multi_asset_dify_smoke.py
- scripts/run_multi_asset_error_dify_smoke.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

## 7. 当前 Dify response smoke 分支

当前 Dify paper execution response smoke 覆盖：

- fill_to_user_paper_fill_success
- reject_to_user_paper_reject_success
- policy_deny_to_user_paper_policy_deny
- risk_deny_to_user_paper_risk_deny
- bad_order_to_user_paper_execution_error
- real_execution_intent_to_safety_refusal

对应 response_type：

- paper_fill_success
- paper_reject_success
- paper_policy_deny
- paper_risk_deny
- paper_execution_error
- paper_safety_refusal

## 8. 当前测试覆盖

当前测试覆盖：

- raw market input schema
- schema error catalog
- market input pipeline schema integration
- local market input API
- Dify market input HTTP adapter
- multi-asset success smoke
- multi-asset error smoke
- paper order schema
- sandbox execution engine
- sandbox execution EventStore / Replay
- paper execution API wrapper
- Dify paper execution adapter
- Dify paper execution smoke
- paper execution response templates
- Dify paper execution response smoke
- paper execution policy gate
- policy gate API integration
- paper_policy_deny response templates
- paper execution risk guardian
- risk guardian API integration
- paper_risk_deny response templates

## 9. 当前验证命令

当前验证命令：

python main.py

python scripts/run_dify_http_adapter_smoke.py

python scripts/run_dify_integration_smoke.py

python scripts/run_multi_asset_dify_smoke.py

python scripts/run_multi_asset_error_dify_smoke.py

python scripts/run_dify_paper_execution_smoke.py

python scripts/run_dify_paper_execution_response_smoke.py

python -m pytest -q

当前预期：

- events_recorded: 8
- status completed
- 235 passed

## 10. 当前安全边界

当前系统保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不展示真实收益
- Dify 不作为底层交易内核
- Dify 不直接接真实交易所 API
- Dify 只调用受控 API wrapper / pipeline
- 不允许 Dify 绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交
- 不把 sandbox reject 伪装成交易所真实拒单
- 不把 PolicyDeny 伪装成交易所真实拒单
- 不把 RiskDeny 伪装成交易所真实拒单

## 11. Phase 7 候选方向

Phase 7 建议方向：

1. Multi-asset guarded paper execution fixtures
   - 扩展 crypto / equities / fx / commodities paper order fixture
   - 覆盖 policy gate
   - 覆盖 risk guardian
   - 覆盖 paper execution adapter
   - 输出 multi-asset guarded smoke

2. Paper execution audit report
   - 汇总 EventStore 中 paper execution event
   - 输出 replay report
   - 输出 audit summary
   - 区分 fill / reject / policy deny / risk deny

3. Dify workflow export template
   - 输出 Dify workflow 节点模板
   - 明确每个节点输入输出字段
   - 明确 error branch
   - 明确 policy deny branch
   - 明确 risk deny branch
   - 明确 safety refusal branch
   - 不包含真实 API key

## 12. 推荐下一步

建议进入：

P7-D1：Multi-asset guarded paper execution fixture plan

目标：

- 新增 multi-asset guarded paper execution fixture 规划文档
- 覆盖 crypto / equities / fx / commodities
- 明确每个资产类别的 raw_order 样例
- 明确每个资产类别的 risk_context 样例
- 明确 policy deny / risk deny 分支样例
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

