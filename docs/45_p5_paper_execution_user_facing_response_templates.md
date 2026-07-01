# P5-D9 - Paper Execution User-facing Response Templates

## 1. 目的

P5-D9 新增 paper execution 用户可见回复模板。

当前系统已经支持：

- paper order schema
- sandbox execution engine
- EventStore / Replay integration
- paper execution API wrapper
- Dify paper execution local adapter
- Dify paper execution smoke runner

P5-D9 的目标是让 Dify 面向用户展示 paper execution 结果时，保持稳定、清晰、安全的文案边界。

## 2. 模板类型

当前定义四类模板：

- paper_fill_success
- paper_reject_success
- paper_execution_error
- paper_safety_refusal

## 3. Paper Fill Success

当 paper execution 返回：

- ok = true
- execution_status = filled 或 partial_filled

Dify 可以告诉用户：

- 纸面模拟执行已完成
- 这是 paper / sandbox 结果
- 没有连接真实交易所
- 没有真实下单
- 没有真实资金变化
- 没有真实仓位变化
- event_count
- replay_status
- filled_quantity
- remaining_quantity
- fill_price
- notional

禁止说法：

- 已真实买入
- 已真实卖出
- 已真实成交
- 已产生真实收益
- 已修改真实仓位

## 4. Paper Reject Success

当 paper execution 返回：

- ok = true
- execution_status = rejected

Dify 可以告诉用户：

- 纸面模拟拒单已完成
- 这是 sandbox reject
- 不是交易所真实拒单
- 没有连接真实交易所
- 没有真实下单
- reject_reason
- event_count
- replay_status

## 5. Paper Execution Error

当 paper execution 返回：

- ok = false

Dify 必须告诉用户：

- paper execution 输入没有通过校验
- error type
- error message
- 没有连接真实交易所
- 没有真实下单

## 6. Paper Safety Refusal

当用户要求真实下单、连接真实交易所、保存 API key、读取钱包私钥、把 paper order 转成 real order 时，Dify 必须拒绝。

拒绝说明必须包含：

- 当前只支持 paper / sandbox execution
- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不支持把 paper execution 伪装成 real execution

## 7. 安全边界

P5-D9 不接真实交易所 API。
P5-D9 不保存真实 API key。
P5-D9 不读取钱包私钥。
P5-D9 不真实下单。
P5-D9 不把 paper execution 伪装成 real execution。
P5-D9 不把 sandbox fill 伪装成真实成交。

## 8. 验收标准

P5-D9 完成需要满足：

- 新增 docs/45_p5_paper_execution_user_facing_response_templates.md
- 新增 fcf/api/paper_execution_response_templates.py
- 新增 tests/test_paper_execution_response_templates.py
- 覆盖 paper fill success
- 覆盖 paper partial fill success
- 覆盖 paper reject success
- 覆盖 paper execution error
- 覆盖 paper safety refusal
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

