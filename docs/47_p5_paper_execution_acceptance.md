# P5-D11 - Phase 5 Paper Execution Acceptance

## 1. 目的

P5-D11 用于验收 Phase 5 的 paper-only sandbox execution 成果。

Phase 5 的核心目标是：

- 只支持 paper / sandbox execution
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不把 paper execution 伪装成 real execution
- 所有 sandbox execution 必须可审计、可回放

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。

## 3. P5-D1 到 P5-D10 完成范围

Phase 5 当前已完成：

- P5-D1：Paper-only sandbox execution boundary plan
- P5-D2：paper order schema module
- P5-D3：sandbox execution engine skeleton
- P5-D4：sandbox execution EventStore and Replay integration
- P5-D5：paper execution API wrapper
- P5-D6：Dify paper execution contract
- P5-D7：Dify paper execution local adapter
- P5-D8：Dify paper execution smoke runner
- P5-D9：paper execution user-facing response templates
- P5-D10：Dify paper execution response integration smoke
- P5-D11：Phase 5 paper execution acceptance

## 4. 当前 paper order schema 能力

当前 paper order schema 支持：

- required field check
- asset_class normalization
- market_type normalization
- symbol normalization
- venue normalization
- side normalization
- order_type normalization
- time_in_force normalization
- quantity positive check
- price optional positive check
- metadata dict check

强制安全字段：

- execution_mode = paper
- real_order = false
- real_exchange_api = false
- real_money_impact = false

## 5. 当前 sandbox execution engine 能力

当前 sandbox execution engine 支持：

- simulated_fill
- simulated_reject
- full fill
- partial fill
- reject reason
- stable response dict
- EventStore integration
- ReplayEngine integration
- optional JSONL persistence

强制安全字段：

- execution_mode = paper
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

## 6. 当前 paper execution API wrapper 能力

当前 wrapper：

- fcf/api/paper_execution_api.py

当前函数：

- describe_paper_execution_api
- handle_paper_execution

当前能力：

- 包装 execute_sandbox_order_with_eventstore
- 返回稳定 response dict
- 支持 simulated_fill
- 支持 simulated_reject
- 支持 full fill
- 支持 partial fill
- 支持 error response
- 支持 optional JSONL persistence

## 7. 当前 Dify paper execution adapter 能力

当前 adapter：

- fcf/api/dify_paper_execution_adapter.py

当前 route：

- GET /api/v1/paper-execution/contract
- POST /api/v1/paper-execution/execute

当前能力：

- contract route 返回 200
- execute route 支持 simulated_fill
- execute route 支持 simulated_reject
- bad order 返回 422
- bad simulation_mode 返回 422
- missing raw_order 返回 400
- wrong method 返回 405
- unknown route 返回 404

该 adapter 只调用：

- paper_execution_api

该 adapter 不调用：

- 真实交易所 API
- 真实经纪商 API
- 真实执行器

## 8. 当前 user-facing response templates

当前模板：

- paper_fill_success
- paper_reject_success
- paper_execution_error
- paper_safety_refusal

当前要求：

paper fill success 必须说明：

- 这是 paper / sandbox execution
- 不是实盘成交
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化

paper reject success 必须说明：

- 这是 sandbox reject
- 不是交易所真实拒单
- 没有连接真实交易所
- 没有真实下单

paper execution error 必须说明：

- 输入没有通过校验
- 没有连接真实交易所
- 没有真实下单

paper safety refusal 必须拒绝：

- place_real_order
- connect_exchange
- save_api_key
- read_wallet_private_key
- real_execution
- bypass_risk
- force_execute_trade
- convert_paper_to_real_order

## 9. 当前 smoke runner

当前 Phase 5 相关 smoke runner：

- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

当前全局 smoke runner：

- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py
- scripts/run_multi_asset_dify_smoke.py
- scripts/run_multi_asset_error_dify_smoke.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

## 10. 当前验证命令

当前验收命令：

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
- 186 passed

## 11. 安全边界验收

Phase 5 当前明确保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不展示真实收益
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交
- 不把 sandbox reject 伪装成交易所真实拒单

## 12. P5-D11 验收结论

P5-D11 完成后，Phase 5 paper-only sandbox execution 达到阶段验收点。

当前系统已经具备：

- paper order schema
- sandbox execution engine
- EventStore / ReplayEngine integration
- paper execution API wrapper
- Dify paper execution local adapter
- Dify paper execution smoke runner
- paper execution user-facing response templates
- Dify paper execution response integration smoke

当前仍然只支持 paper / sandbox。
当前不接真实交易所。
当前不真实下单。

