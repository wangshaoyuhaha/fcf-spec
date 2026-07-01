# P4-D11 - Multi-asset Error Fixture and Negative Smoke

## 1. 目的

P4-D11 增加 multi-asset negative smoke。

P4-D10 已经验证多资产 fixture 可以成功通过 Dify batch route，并转成 user-facing success response。

P4-D11 验证多资产错误输入能稳定失败，并转成 user-facing error response。

## 2. 覆盖错误场景

P4-D11 覆盖：

- equities bad market_type
- fx bad spread
- commodities missing last_price

## 3. 预期行为

每个错误场景都应该满足：

- Dify batch route 返回 http_status 422
- body.ok 为 false
- body.error.type 为 ValueError
- body.error.message 包含对应字段
- render_dify_user_response 返回 response_type error
- user-facing response 保留安全边界
- 不产生真实交易
- 不连接真实交易所

## 4. Batch 错误策略

继续沿用 P4-D7 的策略：

batch 中任意一行 schema 校验失败，整个 batch 失败。

当前不做部分成功。
当前不写入部分成功事件。
当前不把部分校验通过伪装成整体成功。

## 5. 安全边界

P4-D11 不接真实交易所 API。
P4-D11 不保存真实 API key。
P4-D11 不读取钱包私钥。
P4-D11 不真实下单。
P4-D11 不让 Dify 成为底层交易内核。
P4-D11 不把 pipeline 成功伪装成真实交易成功。

## 6. 验收标准

P4-D11 完成需要满足：

- 新增 docs/34_p4_multi_asset_error_negative_smoke.md
- 新增 scripts/run_multi_asset_error_dify_smoke.py
- 新增 tests/test_multi_asset_error_dify_smoke.py
- equities bad market_type 返回 422
- fx bad spread 返回 422
- commodities missing last_price 返回 422
- user-facing response 均为 error
- python main.py 输出 events_recorded: 8
- python scripts/run_dify_http_adapter_smoke.py 输出 status completed
- python scripts/run_dify_integration_smoke.py 输出 status completed
- python scripts/run_multi_asset_dify_smoke.py 输出 status completed
- python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed
- python -m pytest -q 通过

