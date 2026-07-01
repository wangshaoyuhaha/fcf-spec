# P6-D2 - Paper Execution Policy Gate Module

## 1. 目的

P6-D2 新增 paper execution policy gate module。

该模块用于在 paper execution 进入 sandbox execution engine 前，先做 policy gate 判断。

目标是确保：

- paper execution 不能绕过 policy
- Dify 不能绕过 policy
- 用户不能把 paper order 转成 real order
- 用户不能要求保存 API key
- 用户不能要求读取钱包私钥
- 用户不能要求真实执行
- 用户不能要求绕过 risk
- 用户不能强制执行交易

P6-D2 不接真实交易所 API。
P6-D2 不保存真实 API key。
P6-D2 不读取钱包私钥。
P6-D2 不真实下单。

## 2. 新增模块

新增文件：

- fcf/policy/paper_execution_policy.py

新增测试：

- tests/test_paper_execution_policy.py

## 3. 当前拒绝字段

当前 policy gate 拒绝以下字段为 true 的请求：

- real_execution_requested
- real_order
- real_exchange_api
- save_api_key_requested
- read_private_key_requested
- bypass_risk_requested
- force_execute_requested
- convert_paper_to_real_requested
- place_real_order_requested
- connect_exchange_requested

## 4. 支持嵌套检查

policy gate 会检查：

- request 顶层字段
- request.raw_order 字段
- request.metadata 字段
- request.raw_order.metadata 字段

只要任意位置出现危险字段为 true，就返回 denied。

## 5. 稳定 decision dict

允许时返回：

{
  "ok": true,
  "gate": "paper_execution_policy",
  "gate_version": "0.1.0",
  "decision": "allowed",
  "error": null,
  "data": {}
}

拒绝时返回：

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

## 6. 安全边界

P6-D2 继续保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不修改真实账户
- 不修改真实仓位
- 不产生真实成交
- 不允许 Dify 绕过 policy
- 不把 paper execution 伪装成 real execution

## 7. 下一步建议

下一步进入 P6-D3：integrate paper execution policy gate into paper execution API。

建议目标：

- 在 paper_execution_api.handle_paper_execution 前调用 evaluate_paper_execution_policy
- policy denied 时直接返回 ok=false
- 不进入 sandbox execution engine
- 保持现有成功路径不变
- 增加 API integration tests
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

