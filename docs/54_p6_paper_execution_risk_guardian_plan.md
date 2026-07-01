# P6-D6 - Paper Execution Risk Guardian Module Plan

## 1. 目的

P6-D6 规划 paper execution risk guardian module。

P6-D2 到 P6-D5 已经完成 policy gate 与 policy deny response。

下一步需要新增 risk guardian，用于在 policy gate 通过之后、sandbox execution engine 之前，做 paper / sandbox 风控拒绝判断。

P6-D6 只做规划，不实现代码模块。

P6-D6 不接真实交易所 API。
P6-D6 不保存真实 API key。
P6-D6 不读取钱包私钥。
P6-D6 不真实下单。

## 2. 当前执行顺序

建议执行顺序：

1. Dify safety refusal
2. schema validation
3. policy gate
4. risk guardian
5. sandbox execution
6. EventStore
7. ReplayEngine
8. user-facing response templates

说明：

- safety refusal 处理明显危险的用户意图
- schema validation 处理输入结构错误
- policy gate 处理系统政策禁止事项
- risk guardian 处理 paper / sandbox 风控规则
- sandbox execution 只能在全部通过后执行

## 3. Risk Deny 的定义

risk deny 是风控拒绝。

risk deny 不是 schema error。
risk deny 不是 policy deny。
risk deny 不是 Dify safety refusal。
risk deny 不是交易所真实拒单。
risk deny 不代表真实账户、真实资金、真实仓位发生变化。

risk deny 表示：

- 输入结构合法
- policy 未拒绝
- 但 paper / sandbox 风控规则不允许进入模拟执行

## 4. 建议新增模块

P6-D7 建议新增：

- fcf/risk/paper_execution_risk_guardian.py
- tests/test_paper_execution_risk_guardian.py

建议函数：

- describe_paper_execution_risk_guardian
- evaluate_paper_execution_risk

建议稳定 response dict：

{
  "ok": true,
  "guardian": "paper_execution_risk_guardian",
  "guardian_version": "0.1.0",
  "decision": "allowed",
  "error": null,
  "data": {}
}

拒绝时：

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

## 5. 建议 risk_context

建议 risk_context 字段：

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

## 6. 建议拒绝规则

P6-D7 第一批建议实现：

- missing risk_context
- quantity > max_quantity
- quantity * price > max_notional
- symbol in blocked_symbols
- asset_class in blocked_asset_classes
- leverage requested
- margin requested
- duplicated order key
- high risk flag present

## 7. missing risk_context

建议规则：

如果 request 缺少 risk_context，并且 allow_missing_risk_context 不是 true，则拒绝。

原因：

paper execution 虽然不真实下单，但也应走风险上下文。
后续 Dify 不应直接绕过 risk guardian。

## 8. max_quantity

建议规则：

如果 raw_order.quantity > risk_context.max_quantity，则拒绝。

示例：

quantity = 10
max_quantity = 1

拒绝信息：

quantity exceeds paper sandbox max_quantity

## 9. max_notional

建议规则：

notional = quantity * price

如果 notional > risk_context.max_notional，则拒绝。

示例：

quantity = 2
price = 60050
max_notional = 10000

拒绝信息：

notional exceeds paper sandbox max_notional

## 10. duplicated order

建议规则：

构造 order_key：

asset_class:symbol:side:order_type:correlation_id

如果 order_key 出现在 risk_context.duplicate_order_keys 中，则拒绝。

说明：

这是 paper / sandbox duplicate order 防护，不是真实交易所去重。

## 11. blocked symbol / asset class

建议规则：

如果 symbol 出现在 blocked_symbols 中，则拒绝。

如果 asset_class 出现在 blocked_asset_classes 中，则拒绝。

说明：

这用于后续阶段模拟交易禁用名单。

## 12. leverage / margin

建议规则：

如果 raw_order 或 metadata 中出现：

- leverage
- leverage_requested
- margin
- margin_mode
- margin_requested

并且 risk_context.allow_leverage 或 risk_context.allow_margin 不允许，则拒绝。

P6 阶段不实现真实杠杆。
P6 阶段不实现真实保证金。
P6 阶段不接真实交易所。

## 13. high risk flags

建议规则：

如果 risk_context.high_risk_flags 非空，则拒绝。

示例：

- high_uncertainty
- abnormal_spread
- liquidity_risk
- duplicate_order_risk
- missing_market_context

## 14. 与 policy deny 的区别

policy deny 拒绝系统禁止事项：

- 真实下单
- 连接交易所
- 保存 API key
- 读取私钥
- 绕过风控
- 强制执行
- paper 转 real

risk deny 拒绝风控不允许的 paper order：

- 数量过大
- 名义金额过大
- 缺少风险上下文
- 重复订单
- blocked symbol
- leverage / margin
- high risk flags

## 15. 用户可见文案要求

RiskDeny 用户可见文案必须说明：

- paper / sandbox 风控拒绝了该模拟执行
- 这不是交易所真实拒单
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化
- 需要降低 quantity / notional 或补充 risk_context 后重试

## 16. 后续集成计划

P6-D7：

- 新增 paper execution risk guardian module
- 增加单元测试
- 不接入 paper_execution_api

P6-D8：

- 将 risk guardian 接入 paper_execution_api
- 执行顺序变为 policy gate -> risk guardian -> sandbox execution
- RiskDeny 不进入 sandbox execution engine
- 增加 integration tests

P6-D9：

- 扩展 user-facing response templates
- 新增 paper_risk_deny response
- 明确 risk deny 不是交易所真实拒单

P6-D10：

- 更新 Dify response smoke
- 增加 risk_deny case
- 明确 policy_deny / risk_deny / execution_error / safety_refusal 区别

## 17. P6-D6 验收标准

P6-D6 完成需要满足：

- 新增 docs/54_p6_paper_execution_risk_guardian_plan.md
- README 更新 P6-D6 状态
- PROJECT_STATE 更新 P6-D6 状态
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

