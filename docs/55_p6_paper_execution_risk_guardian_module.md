# P6-D7 - Paper Execution Risk Guardian Module

## 1. 目的

P6-D7 新增 paper execution risk guardian module。

该模块用于在 policy gate 通过之后、sandbox execution engine 之前，判断 paper / sandbox order 是否应被风控拒绝。

P6-D7 只新增独立 risk guardian 模块。
P6-D7 不接入 paper_execution_api。
P6-D7 不接真实交易所 API。
P6-D7 不保存真实 API key。
P6-D7 不读取钱包私钥。
P6-D7 不真实下单。

## 2. 新增模块

新增文件：

- fcf/risk/paper_execution_risk_guardian.py

新增测试：

- tests/test_paper_execution_risk_guardian.py

## 3. 新增函数

新增函数：

- describe_paper_execution_risk_guardian
- evaluate_paper_execution_risk

## 4. Risk Guardian 输入

建议输入：

{
  "raw_order": {},
  "risk_context": {}
}

raw_order 来自 paper order request。

risk_context 示例：

{
  "max_quantity": 1.0,
  "max_notional": 100000.0,
  "allow_missing_risk_context": false,
  "allow_leverage": false,
  "allow_margin": false,
  "duplicate_order_keys": [],
  "blocked_symbols": [],
  "blocked_asset_classes": [],
  "high_risk_flags": []
}

## 5. Stable Decision Dict

允许时返回：

{
  "ok": true,
  "guardian": "paper_execution_risk_guardian",
  "guardian_version": "0.1.0",
  "decision": "allowed",
  "error": null,
  "data": {}
}

拒绝时返回：

{
  "ok": false,
  "guardian": "paper_execution_risk_guardian",
  "guardian_version": "0.1.0",
  "decision": "denied",
  "error": {
    "type": "RiskDeny",
    "message": "notional exceeds paper sandbox max_notional"
  },
  "data": null
}

## 6. 当前拒绝规则

P6-D7 当前实现：

- request must be dict
- raw_order must be dict
- missing risk_context
- quantity > max_quantity
- quantity * price > max_notional
- duplicated order key
- symbol in blocked_symbols
- asset_class in blocked_asset_classes
- leverage requested
- margin requested
- high risk flags present

## 7. 当前 order_key

当前 duplicate order key：

asset_class:symbol:side:order_type:correlation_id

示例：

crypto:BTCUSDT:buy:limit:p6-d7-risk

## 8. RiskDeny 用户可见边界

RiskDeny 必须解释为：

- paper / sandbox 风控拒绝
- 不是交易所真实拒单
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化

## 9. 安全边界

P6-D7 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不允许绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- 不把 RiskDeny 伪装成交易所真实拒单

## 10. 下一步建议

下一步进入 P6-D8：integrate risk guardian into paper execution API。

建议目标：

- 在 paper_execution_api.handle_paper_execution 中接入 evaluate_paper_execution_risk
- 执行顺序为 policy gate -> risk guardian -> sandbox execution
- RiskDeny 直接返回 ok=false
- RiskDeny 不进入 sandbox execution engine
- RiskDeny 不生成 sandbox execution event
- Dify adapter 传入 risk_context
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

