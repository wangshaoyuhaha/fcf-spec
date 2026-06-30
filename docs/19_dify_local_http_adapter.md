# P3-D9 - Dify Local HTTP Adapter

## 1. 目的

P3-D9 增加一个本地 Dify HTTP Adapter 最小路由层。

这个 adapter 的目的不是接真实交易所。
这个 adapter 的目的不是下单。
这个 adapter 只是把未来 Dify HTTP/API Node 的请求格式，映射到 FCF 已有的受控 API wrapper。

当前受控 wrapper：

- fcf/api/local_market_input_api.py
- handle_single_market_input
- handle_batch_market_input
- describe_api_contract

## 2. 当前安全边界

P3-D9 不做：

- 不连接真实交易所 API
- 不保存真实交易所 API key
- 不读取钱包私钥
- 不真实下单
- 不绕过 policy
- 不绕过 risk
- 不绕过 EventStore
- 不绕过 ReplayEngine
- 不引入外部 Web 框架依赖

P3-D9 只做：

- 定义本地 HTTP 风格路由函数
- 接收 method、path、body
- 校验请求字段
- 调用受控 local_market_input_api
- 返回稳定 http-style response dict

## 3. 支持的最小路由

当前支持：

- GET /api/v1/contract
- POST /api/v1/market-input/single
- POST /api/v1/market-input/batch

## 4. 统一返回结构

Adapter 返回：

{
  "http_status": 200,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "ok": true,
    "api": "local_market_input_api",
    "api_version": "0.1.0",
    "error": null,
    "data": {}
  }
}

## 5. 错误返回

未知路由：

{
  "http_status": 404,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "ok": false,
    "api": "dify_http_adapter",
    "api_version": "0.1.0",
    "error": {
      "type": "NotFound",
      "message": "route not found"
    },
    "data": null
  }
}

方法不允许：

{
  "http_status": 405,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "ok": false,
    "api": "dify_http_adapter",
    "api_version": "0.1.0",
    "error": {
      "type": "MethodNotAllowed",
      "message": "method not allowed"
    },
    "data": null
  }
}

字段缺失：

{
  "http_status": 400,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "ok": false,
    "api": "dify_http_adapter",
    "api_version": "0.1.0",
    "error": {
      "type": "BadRequest",
      "message": "raw must be provided as object"
    },
    "data": null
  }
}

FCF wrapper 校验失败：

{
  "http_status": 422,
  "headers": {
    "content-type": "application/json"
  },
  "body": {
    "ok": false,
    "api": "local_market_input_api",
    "api_version": "0.1.0",
    "error": {
      "type": "ValueError",
      "message": "last_price must be a valid number"
    },
    "data": null
  }
}

## 6. P3-D9 验收标准

P3-D9 完成需要满足：

- 新增 fcf/api/dify_http_adapter.py
- 新增 tests/test_dify_http_adapter.py
- 支持 contract route
- 支持 single input route
- 支持 batch input route
- 支持 unknown route 错误
- 支持 method not allowed 错误
- 支持 missing field 错误
- 支持 wrapper validation error 映射
- python main.py 仍输出 events_recorded: 8
- python -m pytest -q 通过

