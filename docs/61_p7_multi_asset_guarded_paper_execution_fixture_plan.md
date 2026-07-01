# P7-D1 - Multi-asset Guarded Paper Execution Fixture Plan

## 1. 目的

P7-D1 开始进入 Phase 7。

Phase 7 的目标是把 guarded paper execution 从单一 crypto / BTC 样例，扩展为多资产 paper execution fixture 与 smoke。

当前系统已经具备：

- paper order schema
- sandbox execution engine
- paper execution API wrapper
- Dify paper execution adapter
- policy gate
- risk guardian
- paper_policy_deny response
- paper_risk_deny response
- Dify paper execution response smoke

P7-D1 只做规划文档，不改核心代码。

P7-D1 不接真实交易所 API。
P7-D1 不保存真实 API key。
P7-D1 不读取钱包私钥。
P7-D1 不真实下单。

## 2. Phase 7 目标

Phase 7 建议目标：

- 新增 multi-asset guarded paper order fixture
- 覆盖 crypto / equities / fx / commodities
- 每个资产类别都有 raw_order 样例
- 每个资产类别都有 risk_context 样例
- 每个资产类别都可以走 policy gate
- 每个资产类别都可以走 risk guardian
- 每个资产类别都可以进入 sandbox execution
- 覆盖 success / reject / policy deny / risk deny 分支
- 输出 multi-asset guarded paper execution smoke summary

## 3. 推荐新增 fixture

建议新增文件：

- fixtures/paper_orders_multi_asset_guarded.json

建议结构：

{
  "schema": "fcf.paper.multi_asset_guarded_orders",
  "schema_version": "0.1.0",
  "cases": []
}

每个 case 建议字段：

- name
- expected_branch
- raw_order
- simulation_mode
- risk_context
- policy_context
- expected_http_status
- expected_response_type

## 4. 资产覆盖范围

第一批建议覆盖：

- crypto: BTCUSDT perpetual
- equities: AAPL spot
- fx: EURUSD spot
- commodities: XAUUSD futures

后续可扩展：

- rates
- index
- futures
- options

## 5. Crypto raw_order 样例

crypto / BTCUSDT / perpetual：

{
  "asset_class": "crypto",
  "symbol": "BTCUSDT",
  "venue": "binance",
  "market_type": "perp",
  "side": "buy",
  "order_type": "limit",
  "quantity": "0.25",
  "price": "60050.5",
  "time_in_force": "gtc",
  "source": "multi_asset_guarded_fixture",
  "correlation_id": "p7-crypto-btcusdt"
}

建议 risk_context：

{
  "max_quantity": 1.0,
  "max_notional": 100000.0,
  "allow_leverage": false,
  "allow_margin": false,
  "duplicate_order_keys": [],
  "blocked_symbols": [],
  "blocked_asset_classes": [],
  "high_risk_flags": []
}

## 6. Equities raw_order 样例

equities / AAPL / spot：

{
  "asset_class": "equities",
  "symbol": "AAPL",
  "venue": "nasdaq",
  "market_type": "spot",
  "side": "buy",
  "order_type": "limit",
  "quantity": "10",
  "price": "195.50",
  "time_in_force": "day",
  "source": "multi_asset_guarded_fixture",
  "correlation_id": "p7-equities-aapl"
}

建议 risk_context：

{
  "max_quantity": 100.0,
  "max_notional": 25000.0,
  "allow_leverage": false,
  "allow_margin": false,
  "duplicate_order_keys": [],
  "blocked_symbols": [],
  "blocked_asset_classes": [],
  "high_risk_flags": []
}

## 7. FX raw_order 样例

fx / EURUSD / spot：

{
  "asset_class": "fx",
  "symbol": "EURUSD",
  "venue": "oanda",
  "market_type": "spot",
  "side": "buy",
  "order_type": "limit",
  "quantity": "10000",
  "price": "1.0850",
  "time_in_force": "gtc",
  "source": "multi_asset_guarded_fixture",
  "correlation_id": "p7-fx-eurusd"
}

建议 risk_context：

{
  "max_quantity": 50000.0,
  "max_notional": 75000.0,
  "allow_leverage": false,
  "allow_margin": false,
  "duplicate_order_keys": [],
  "blocked_symbols": [],
  "blocked_asset_classes": [],
  "high_risk_flags": []
}

## 8. Commodities raw_order 样例

commodities / XAUUSD / futures：

{
  "asset_class": "commodities",
  "symbol": "XAUUSD",
  "venue": "cme",
  "market_type": "futures",
  "side": "buy",
  "order_type": "limit",
  "quantity": "1",
  "price": "2350.0",
  "time_in_force": "day",
  "source": "multi_asset_guarded_fixture",
  "correlation_id": "p7-commodities-xauusd"
}

建议 risk_context：

{
  "max_quantity": 5.0,
  "max_notional": 25000.0,
  "allow_leverage": false,
  "allow_margin": false,
  "duplicate_order_keys": [],
  "blocked_symbols": [],
  "blocked_asset_classes": [],
  "high_risk_flags": []
}

## 9. Success 分支规划

success case 应覆盖：

- crypto_fill_success
- equities_fill_success
- fx_fill_success
- commodities_fill_success

预期：

- adapter http_status = 200
- body.ok = true
- execution_status = filled 或 partial_filled
- user response_type = paper_fill_success
- real_order = false
- real_execution = false
- real_exchange_api = false
- real_money_impact = false

## 10. Sandbox Reject 分支规划

reject case 应覆盖：

- crypto_sandbox_reject
- equities_sandbox_reject
- fx_sandbox_reject
- commodities_sandbox_reject

预期：

- adapter http_status = 200
- body.ok = true
- execution_status = rejected
- user response_type = paper_reject_success
- 不是交易所真实拒单
- 没有真实下单

## 11. Policy Deny 分支规划

policy deny case 可覆盖：

- crypto_policy_deny_bypass_risk
- equities_policy_deny_real_order
- fx_policy_deny_connect_exchange
- commodities_policy_deny_force_execute

触发字段示例：

- bypass_risk_requested = true
- real_order = true
- connect_exchange_requested = true
- force_execute_requested = true

预期：

- adapter http_status = 422
- body.ok = false
- error.type = PolicyDeny
- user response_type = paper_policy_deny
- 不进入 sandbox execution
- 不是交易所真实拒单
- 没有真实下单

## 12. Risk Deny 分支规划

risk deny case 可覆盖：

- crypto_risk_deny_max_notional
- equities_risk_deny_max_quantity
- fx_risk_deny_blocked_symbol
- commodities_risk_deny_high_risk_flags

触发方式示例：

- max_notional 过低
- max_quantity 过低
- blocked_symbols 包含 symbol
- high_risk_flags 非空

预期：

- adapter http_status = 422
- body.ok = false
- error.type = RiskDeny
- user response_type = paper_risk_deny
- 不进入 sandbox execution
- 不是交易所真实拒单
- 没有真实下单

## 13. 推荐 smoke runner

建议 P7-D3 或 P7-D4 新增：

- scripts/run_multi_asset_guarded_paper_execution_smoke.py
- tests/test_multi_asset_guarded_paper_execution_smoke.py

该 smoke runner 应：

- 读取 fixtures/paper_orders_multi_asset_guarded.json
- 调用 Dify paper execution adapter
- 接入 paper_execution_response_templates
- 输出每个 case 的 summary
- 汇总 branch_count
- 汇总 asset_class_count
- 汇总 safe_boundary

## 14. 推荐 summary 字段

建议 smoke summary：

{
  "status": "completed",
  "runner": "multi_asset_guarded_paper_execution_smoke",
  "case_count": 16,
  "asset_classes": ["crypto", "equities", "fx", "commodities"],
  "branches": [
    "paper_fill_success",
    "paper_reject_success",
    "paper_policy_deny",
    "paper_risk_deny"
  ],
  "cases": [],
  "safe_boundary": {}
}

每个 case：

- name
- asset_class
- symbol
- expected_branch
- adapter_http_status
- adapter_ok
- adapter_error_type
- user_response_type
- real_order
- real_execution
- real_exchange_api
- real_money_impact
- not_exchange_reject

## 15. 安全边界

P7-D1 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不展示真实收益
- Dify 不作为底层交易内核
- Dify 只调用受控 API wrapper / pipeline
- 不允许 Dify 绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交
- 不把 sandbox reject 伪装成交易所真实拒单
- 不把 PolicyDeny 伪装成交易所真实拒单
- 不把 RiskDeny 伪装成交易所真实拒单

## 16. P7-D1 验收标准

P7-D1 完成需要满足：

- 新增 docs/61_p7_multi_asset_guarded_paper_execution_fixture_plan.md
- README 更新 P7-D1 状态
- PROJECT_STATE 更新 P7-D1 状态
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

## 17. 下一步建议

下一步进入 P7-D2：multi-asset guarded paper execution fixture。

建议新增：

- fixtures/paper_orders_multi_asset_guarded.json
- tests/test_multi_asset_guarded_paper_fixture.py

P7-D2 目标：

- 新增 crypto / equities / fx / commodities fixture
- 每个资产类别覆盖 fill success
- 每个资产类别覆盖 sandbox reject
- 每个资产类别覆盖 policy deny
- 每个资产类别覆盖 risk deny
- 验证 fixture schema
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

