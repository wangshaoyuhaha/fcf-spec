# P3-D11 - Dify User Facing Response Templates

## 1. 目的

P3-D11 定义 Dify 面向用户展示的稳定回复模板。

Dify 不应该随意发挥成真实交易结论。
Dify 不应该把 pipeline 成功说成真实下单成功。
Dify 不应该把 mock / replay 说成实盘收益。
Dify 必须明确说明安全边界。

## 2. 模板类型

当前定义三类模板：

- success
- error
- safety_refusal

## 3. Success 模板

当 FCF 返回 ok=true 时，Dify 可以告诉用户：

- FCF 已接收市场输入
- 受控 pipeline 已完成
- event_count
- replay status
- 没有连接真实交易所
- 没有真实下单

## 4. Error 模板

当 FCF 返回 ok=false 时，Dify 必须告诉用户：

- 输入没有通过校验
- error type
- error message
- 没有连接真实交易所
- 没有真实下单

## 5. Safety Refusal 模板

当用户要求真实下单、连接真实交易所、保存 API key、读取钱包私钥时，Dify 必须拒绝。

Dify 应说明：

- 当前系统不支持真实下单
- 当前系统不接真实交易所 API
- 当前系统不保存 API key
- 当前只能走受控 wrapper / pipeline

## 6. 安全边界

P3-D11 不接真实交易所 API。
P3-D11 不保存真实 API key。
P3-D11 不读取钱包私钥。
P3-D11 不真实下单。
P3-D11 不绕过 FCF policy / risk / EventStore / ReplayEngine。

