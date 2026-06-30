# P3-D7 - Dify API Contract / Example Payload

## 1. 目的

本文档定义 Dify 调用 FCF 本地受控 API wrapper 的输入、输出、错误格式、workflow 字段传递方式和安全边界。

当前阶段只做文档契约。

不接真实交易所 API。
不保存真实 API key。
不真实下单。
Dify 不作为底层交易内核。
Dify 只调用 FCF 受控 API wrapper / pipeline。

## 2. 当前可调用 Wrapper

文件：

- fcf/api/local_market_input_api.py

可调用函数：

- handle_single_market_input
- handle_batch_market_input
- describe_api_contract

稳定返回字段：

- ok
- api
- api_version
- error
- data

## 3. Single Input 请求示例

```json
{
  "handler": "handle_single_market_input",
  "correlation_id": "dify-single-001",
  "output_path": "runtime/events/dify_single.jsonl",
  "raw": {
    "asset_class": "crypto",
    "symbol": "BTCUSDT",
    "venue": "binance",
    "market_type": "perp",
    "timestamp": "2026-06-30T00:00:00Z",
    "timeframe": "1m",
    "source": "dify_user_input",
    "source_type": "mock",
    "open": "60000",
    "high": "60100",
    "low": "59900",
    "close": "60050",
    "last_price": "60050",
    "volume": "120.5",
    "quote_volume": "7230000",
    "best_bid": "60049.5",
    "best_ask": "60050.5",
    "bid_depth": "100",
    "ask_depth": "80"
  }
}

# 先退出上一个没结束的 cat 后再执行本段

git status --short
git pull --ff-only

mkdir -p docs

cat > docs/17_dify_api_contract_examples.md <<'EOF'
# P3-D7 - Dify API Contract / Example Payload

## 1. 目的

本文档定义 Dify 调用 FCF 本地受控 API wrapper 的输入、输出、错误格式、workflow 字段传递方式和安全边界。

当前阶段只做文档契约。

不接真实交易所 API。
不保存真实 API key。
不真实下单。
Dify 不作为底层交易内核。
Dify 只调用 FCF 受控 API wrapper / pipeline。

## 2. 当前可调用 Wrapper

文件：

- fcf/api/local_market_input_api.py

可调用函数：

- handle_single_market_input
- handle_batch_market_input
- describe_api_contract

稳定返回字段：

- ok
- api
- api_version
- error
- data

## 3. Single Input 请求示例

{
  "handler": "handle_single_market_input",
  "correlation_id": "dify-single-001",
  "output_path": "runtime/events/dify_single.jsonl",
  "raw": {
    "asset_class": "crypto",
    "symbol": "BTCUSDT",
    "venue": "binance",
    "market_type": "perp",
    "timestamp": "2026-06-30T00:00:00Z",
    "timeframe": "1m",
    "source": "dify_user_input",
    "source_type": "mock",
    "open": "60000",
    "high": "60100",
    "low": "59900",
    "close": "60050",
    "last_price": "60050",
    "volume": "120.5",
    "quote_volume": "7230000",
    "best_bid": "60049.5",
    "best_ask": "60050.5",
    "bid_depth": "100",
    "ask_depth": "80"
  }
}

## 4. Single Input 成功响应示例

{
  "ok": true,
  "api": "local_market_input_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {
    "status": "completed",
    "pipeline": "market_input_pipeline",
    "symbol": "BTCUSDT",
    "market_type": "perpetual",
    "event_count": 1,
    "persisted": true,
    "output_path": "runtime/events/dify_single.jsonl",
    "replay": {
      "status": "completed",
      "event_count": 1
    }
  }
}

## 5. Batch Input 请求示例

{
  "handler": "handle_batch_market_input",
  "correlation_id": "dify-batch-001",
  "output_path": "runtime/events/dify_batch.jsonl",
  "rows": [
    {
      "asset_class": "crypto",
      "symbol": "BTCUSDT",
      "venue": "binance",
      "market_type": "perp",
      "timestamp": "2026-06-30T00:00:00Z",
      "timeframe": "1m",
      "source": "dify_user_input",
      "source_type": "mock",
      "open": "60000",
      "high": "60100",
      "low": "59900",
      "close": "60050",
      "last_price": "60050",
      "volume": "120.5",
      "quote_volume": "7230000",
      "best_bid": "60049.5",
      "best_ask": "60050.5",
      "bid_depth": "100",
      "ask_depth": "80"
    },
    {
      "asset_class": "crypto",
      "symbol": "ETHUSDT",
      "venue": "binance",
      "market_type": "spot",
      "timestamp": "2026-06-30T00:01:00Z",
      "timeframe": "1m",
      "source": "dify_user_input",
      "source_type": "mock",
      "open": "3300",
      "high": "3310",
      "low": "3290",
      "close": "3305",
      "last_price": "3305",
      "volume": "900.25",
      "quote_volume": "2975626.25",
      "best_bid": "3304.9",
      "best_ask": "3305.1",
      "bid_depth": "500",
      "ask_depth": "450"
    }
  ]
}

## 6. Batch Input 成功响应示例

{
  "ok": true,
  "api": "local_market_input_api",
  "api_version": "0.1.0",
  "error": null,
  "data": {
    "status": "completed",
    "pipeline": "market_input_pipeline",
    "event_count": 2,
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "persisted": true,
    "output_path": "runtime/events/dify_batch.jsonl",
    "replay": {
      "status": "completed",
      "event_count": 2
    }
  }
}

## 7. 错误响应格式

{
  "ok": false,
  "api": "local_market_input_api",
  "api_version": "0.1.0",
  "error": {
    "type": "ValueError",
    "message": "last_price must be a valid number"
  },
  "data": null
}

Dify 遇到 ok=false 时必须进入错误分支，不得继续假装成功。

## 8. Dify Workflow 节点建议

建议节点顺序：

1. Start
2. User Input Parser
3. Field Validation
4. FCF API Call
5. IF response.ok
6. Success Summary
7. Error Summary

字段映射：

- asset_class -> raw.asset_class
- symbol -> raw.symbol
- venue -> raw.venue
- market_type -> raw.market_type
- timestamp -> raw.timestamp
- timeframe -> raw.timeframe
- open -> raw.open
- high -> raw.high
- low -> raw.low
- close -> raw.close
- last_price -> raw.last_price
- volume -> raw.volume
- quote_volume -> raw.quote_volume
- best_bid -> raw.best_bid
- best_ask -> raw.best_ask
- bid_depth -> raw.bid_depth
- ask_depth -> raw.ask_depth
- workflow_run_id -> correlation_id
- output_path -> output_path

## 9. 安全边界

Dify 允许：

- 收集用户输入
- 整理结构化 JSON
- 调用受控 wrapper
- 展示 FCF 返回的 summary
- 在字段错误时提示用户修正

Dify 禁止：

- 直接连接真实交易所
- 保存真实 API key
- 读取钱包私钥
- 真实下单
- 绕过风控
- 绕过 EventStore
- 绕过 ReplayEngine
- 把 LLM 判断直接变成实盘执行

## 10. P3-D7 验收标准

- 文档已新增
- 输入 JSON 已明确
- 输出 JSON 已明确
- 错误响应格式已明确
- workflow 字段传递方式已明确
- 安全边界已明确
- python main.py 仍输出 events_recorded: 8
- python -m pytest -q 仍通过

