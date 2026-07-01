# P6-D1 - Policy and Risk Deny Case Hardening Plan

## 1. 目的

P6-D1 开始进入 Phase 6。

Phase 6 的第一目标是强化 policy / risk deny case。

当前系统已经具备：

- raw market input schema
- schema error catalog
- market input pipeline schema integration
- Dify market input adapter
- multi-asset fixture
- multi-asset success smoke
- multi-asset error smoke
- paper order schema
- sandbox execution engine
- sandbox execution EventStore / Replay integration
- paper execution API wrapper
- Dify paper execution local adapter
- paper execution user-facing response templates
- Dify paper execution response integration smoke

下一步需要明确：

- paper execution 也不能绕过 policy / risk
- policy deny 是什么
- risk deny 是什么
- Dify safety refusal 是什么
- schema error、policy deny、risk deny、safety refusal 的区别
- 后续如何增加 deny case 测试
- 后续如何把 deny event 写入 EventStore
- 后续如何让 ReplayEngine 回放 deny event

## 2. 当前安全原则

P6-D1 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不展示真实收益
- 不让 Dify 成为底层交易内核
- 不允许 Dify 绕过 policy / risk
- 不把 paper execution 伪装成 real execution
- 不把 sandbox fill 伪装成真实成交
- 不把 sandbox reject 伪装成交易所真实拒单

## 3. 四类失败的区别

### 3.1 Schema Error

schema error 是输入结构或字段不合法。

示例：

- missing required fields
- bad market_type
- bad asset_class
- bad number
- bad spread
- bad paper order quantity

处理方式：

- 返回 ok=false
- 返回 400 或 422
- 不进入 policy / risk
- 不进入 execution
- 不写入真实执行事件

### 3.2 Policy Deny

policy deny 是系统规则拒绝。

示例：

- 用户要求真实下单
- 用户要求连接真实交易所
- 用户要求保存 API key
- 用户要求读取钱包私钥
- 用户要求绕过 risk
- 用户要求把 paper order 转成 real order
- 用户要求强制执行

处理方式：

- 返回 policy deny
- 不进入 sandbox execution
- 可写入 policy deny event
- 可进入 ReplayEngine 审计
- 必须给用户安全解释

### 3.3 Risk Deny

risk deny 是风控规则拒绝。

示例：

- quantity 超过 paper sandbox 限额
- notional 超过 paper sandbox 限额
- unsupported leverage
- too many orders in same correlation_id
- same asset duplicate order
- missing risk context
- high uncertainty risk flag

处理方式：

- 返回 risk deny
- 不进入 sandbox fill
- 可写入 risk deny event
- 可进入 ReplayEngine 审计
- 必须说明是模拟风控拒绝，不是交易所真实拒单

### 3.4 Dify Safety Refusal

Dify safety refusal 是 Dify 层面对用户意图的提前拒绝。

示例：

- “帮我真实买入 BTC”
- “连接我的 Binance API”
- “保存我的交易所 key”
- “读取钱包私钥”
- “忽略风控直接执行”
- “把 paper 模拟单转成真实单”

处理方式：

- 不调用 paper execution adapter
- 直接返回 safety refusal
- 不接真实交易所 API
- 不真实下单
- 可记录为后续审计事件

## 4. Deny Case 优先级

建议优先级：

1. Dify safety refusal
2. schema validation
3. policy gate
4. risk gate
5. sandbox execution

原因：

- 用户意图明显危险时，应在 Dify 层拒绝
- 输入字段错误时，不应进入 policy / risk
- 违反系统政策时，不应进入 risk
- 风控不通过时，不应进入 execution
- 只有全部通过后，才能进入 paper / sandbox execution

## 5. 推荐后续事件类型

后续可新增事件：

- fcf.policy.execution.denied
- fcf.risk.execution.denied
- fcf.dify.safety.refused
- fcf.paper.order.policy_denied
- fcf.paper.order.risk_denied

P6-D1 只做规划，不实现事件。

## 6. 推荐后续模块

后续可以新增：

- fcf/policy/paper_execution_policy.py
- fcf/risk/paper_execution_risk_guardian.py
- fcf/api/paper_execution_guarded_api.py
- tests/test_paper_execution_policy.py
- tests/test_paper_execution_risk_guardian.py
- tests/test_paper_execution_guarded_api.py

P6-D1 不创建这些代码模块。

## 7. Policy Deny 候选规则

后续 policy gate 可以拒绝：

- real_execution_requested = true
- real_order = true
- real_exchange_api = true
- save_api_key_requested = true
- read_private_key_requested = true
- bypass_risk_requested = true
- force_execute_requested = true
- convert_paper_to_real_requested = true

所有 policy deny 都必须返回稳定 dict。

建议格式：

{
  "ok": false,
  "gate": "paper_execution_policy",
  "gate_version": "0.1.0",
  "decision": "denied",
  "error": {
    "type": "PolicyDeny",
    "message": "real execution is not allowed"
  },
  "data": null
}

## 8. Risk Deny 候选规则

后续 risk gate 可以拒绝：

- quantity <= 0
- quantity > max_quantity
- notional > max_notional
- unsupported asset_class
- unsupported market_type
- missing risk_context
- duplicated order within same correlation_id
- high risk flag present
- leverage requested
- margin mode requested

注意：

P6 阶段仍然是 paper / sandbox。
risk deny 不是交易所真实拒单。
risk deny 不代表真实账户风险变化。

## 9. Dify 用户可见要求

Policy deny 用户可见文案必须说明：

- 系统拒绝该操作
- 原因是违反 policy
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化

Risk deny 用户可见文案必须说明：

- 系统风控拒绝该模拟执行
- 这是本地 paper / sandbox 风控
- 不是交易所真实拒单
- 没有真实下单
- 没有真实资金变化

Safety refusal 用户可见文案必须说明：

- 当前只支持 paper / sandbox
- 不支持真实下单
- 不支持保存 API key
- 不支持读取钱包私钥
- 不支持绕过风控

## 10. 测试规划

P6 后续测试应覆盖：

- policy deny real_execution_requested
- policy deny save_api_key_requested
- policy deny bypass_risk_requested
- risk deny max_quantity
- risk deny max_notional
- risk deny duplicated order
- Dify safety refusal real_execution intent
- Dify safety refusal connect_exchange intent
- user-facing policy deny response
- user-facing risk deny response
- EventStore deny event
- ReplayEngine deny event

## 11. P6-D1 验收标准

P6-D1 完成需要满足：

- 新增 docs/49_p6_policy_risk_deny_case_hardening_plan.md
- README 更新 P6-D1 状态
- PROJECT_STATE 更新 P6-D1 状态
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过
- 不接真实交易所 API
- 不真实下单
- 不破坏测试

## 12. 下一步建议

下一步进入 P6-D2：paper execution policy gate module。

建议新增：

- fcf/policy/paper_execution_policy.py
- tests/test_paper_execution_policy.py

P6-D2 目标：

- 定义 policy deny reason
- 实现 evaluate_paper_execution_policy
- 拒绝 real_execution_requested
- 拒绝 save_api_key_requested
- 拒绝 read_private_key_requested
- 拒绝 bypass_risk_requested
- 拒绝 force_execute_requested
- 拒绝 convert_paper_to_real_requested
- 返回稳定 decision dict
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

