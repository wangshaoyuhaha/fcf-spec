# P5-D5 - Paper Execution API Wrapper

## 1. 目的

P5-D5 新增 paper execution API wrapper。

该 wrapper 只包装 sandbox execution engine。

调用链：

paper order input
-> fcf.api.paper_execution_api
-> fcf.paper.sandbox_execution_engine.execute_sandbox_order_with_eventstore
-> EventStore
-> ReplayEngine
-> stable response dict

P5-D5 不接真实交易所 API。
P5-D5 不保存真实 API key。
P5-D5 不读取钱包私钥。
P5-D5 不真实下单。

## 2. 当前 API

新增文件：

- fcf/api/paper_execution_api.py

新增函数：

- describe_paper_execution_api
- handle_paper_execution

## 3. Stable Response Dict

成功返回：

{
  "ok": true,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {}
}

失败返回：

{
  "ok": false,
  "api": "paper_execution_api",
  "api_version": "0.1.0",
  "error": {
    "type": "ValueError",
    "message": "error detail"
  },
  "data": null
}

## 4. 支持 simulation_mode

当前支持：

- simulated_fill
- simulated_reject

## 5. 安全边界

P5-D5 API wrapper 必须保持：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 只调用 sandbox execution engine
- 不把 paper execution 伪装成 real execution

## 6. 验收标准

P5-D5 完成需要满足：

- 新增 docs/41_p5_paper_execution_api_wrapper.md
- 新增 fcf/api/paper_execution_api.py
- 新增 tests/test_paper_execution_api.py
- simulated_fill 返回 ok true
- simulated_reject 返回 ok true
- bad order 返回 ok false
- bad simulation_mode 返回 ok false
- wrapper response 字段稳定
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 继续通过
- python -m pytest -q 通过

