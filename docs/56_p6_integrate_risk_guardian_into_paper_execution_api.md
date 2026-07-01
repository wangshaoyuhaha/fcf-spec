# P6-D8 - Integrate Risk Guardian Into Paper Execution API

## 1. 目的

P6-D8 将 P6-D7 的 paper execution risk guardian 接入 paper_execution_api。

目标：

- paper execution API 不能绕过 risk guardian
- Dify paper execution adapter 不能绕过 risk guardian
- 执行顺序固定为 policy gate -> risk guardian -> sandbox execution
- RiskDeny 时直接返回 ok=false
- RiskDeny 时不进入 sandbox execution engine
- RiskDeny 时不生成 sandbox execution event
- RiskDeny 不是交易所真实拒单

P6-D8 不接真实交易所 API。
P6-D8 不保存真实 API key。
P6-D8 不读取钱包私钥。
P6-D8 不真实下单。

## 2. 修改文件

修改：

- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

新增：

- tests/test_paper_execution_api_risk_integration.py

## 3. 当前调用链

Dify style request
-> route_dify_paper_execution_request
-> handle_paper_execution
-> evaluate_paper_execution_policy
-> evaluate_paper_execution_risk
-> execute_sandbox_order_with_eventstore
-> EventStore
-> ReplayEngine

## 4. RiskDeny 行为

当 risk guardian 返回 denied：

paper_execution_api 返回：

{
  "ok": false,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": {
    "type": "RiskDeny",
    "message": "..."
  },
  "data": null
}

该情况下：

- 不进入 sandbox execution engine
- 不生成 sandbox fill
- 不生成 sandbox reject
- 不写入 sandbox execution event
- 不真实下单

## 5. risk_context

handle_paper_execution 新增可选参数：

- risk_context

Dify paper execution adapter 会把 body.risk_context 传入。

safe request 建议提供：

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

## 6. 兼容性说明

为了不破坏历史 direct API 调用，handle_paper_execution 在 risk_context 缺失时会以兼容模式允许缺失风险上下文。

但 Dify / workflow safe sample 会逐步显式传入 risk_context。

后续阶段可以再收紧为强制 risk_context。

## 7. 安全边界

P6-D8 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不允许 Dify 绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- 不把 RiskDeny 伪装成交易所真实拒单

## 8. 验收标准

P6-D8 完成需要满足：

- paper_execution_api 调用 evaluate_paper_execution_policy
- paper_execution_api 调用 evaluate_paper_execution_risk
- safe paper execution 仍返回 ok true
- max_quantity risk deny 返回 ok false / RiskDeny
- max_notional risk deny 返回 ok false / RiskDeny
- Dify adapter 传入 risk_context
- Dify adapter risk deny 返回 422 / RiskDeny
- Dify safe request 仍返回 200
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

