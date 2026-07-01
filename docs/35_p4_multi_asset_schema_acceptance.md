# P4-D12 - Phase 4 Multi-asset Schema Acceptance

## 1. 目的

P4-D12 用于验收 Phase 4 中 multi-asset schema 相关成果。

P4-D9 到 P4-D11 已经完成：

- multi-asset fixture expansion
- multi-asset Dify response smoke
- multi-asset error Dify smoke

P4-D12 汇总这些成果，并明确当前多资产 schema 的验收边界。

## 2. 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。

## 3. 当前多资产 fixture

当前多资产 fixture 文件：

- fixtures/raw_market_data_multi_asset.json

当前覆盖资产：

- crypto / BTCUSDT / perpetual
- equities / AAPL / spot
- fx / EURUSD / spot
- commodities / XAUUSD / futures

## 4. 当前多资产成功链路

当前成功链路：

fixtures/raw_market_data_multi_asset.json
-> Dify batch route
-> local_market_input_api
-> market_input_pipeline
-> raw_market_input_schema
-> EventStore
-> ReplayEngine
-> render_dify_user_response
-> user-facing success response

当前成功 smoke：

- scripts/run_multi_asset_dify_smoke.py

预期输出：

- status completed
- adapter_http_status 200
- adapter_ok true
- event_count 4
- replay_status completed
- replay_event_count 4
- user_response_type success

## 5. 当前多资产失败链路

当前失败链路：

multi-asset error rows
-> Dify batch route
-> local_market_input_api
-> market_input_pipeline
-> raw_market_input_schema
-> schema error
-> adapter http_status 422
-> render_dify_user_response
-> user-facing error response

当前 negative smoke：

- scripts/run_multi_asset_error_dify_smoke.py

覆盖错误：

- equities bad market_type
- fx bad spread
- commodities missing last_price

预期输出：

- status completed
- adapter_http_status 422
- adapter_ok false
- adapter_error_type ValueError
- user_response_type error

## 6. Batch 错误策略验收

当前 batch 错误策略：

batch 中任意一行 schema 错误，整个 batch 失败。

当前不做部分成功。
当前不写入部分成功事件。
当前不把部分成功伪装成整体成功。

原因：

- 保护 EventStore 审计一致性
- 保护 ReplayEngine 回放一致性
- 降低 Dify workflow 分支复杂度
- 避免用户误解为全部成功

## 7. 当前 schema 能力

当前 raw market input schema 支持：

- required field check
- optional number field normalization
- asset_class normalization
- market_type normalization
- symbol normalization
- venue normalization
- last_price positive check
- volume non-negative check
- quote_volume non-negative check
- bid_depth non-negative check
- ask_depth non-negative check
- best_bid <= best_ask check
- stable error message builder
- schema error catalog

## 8. 当前 schema error catalog

当前错误类型：

- MissingField
- InvalidEnumValue
- InvalidNumber
- InvalidPositiveNumber
- InvalidNonNegativeNumber
- InvalidSpread
- InvalidPayloadType

## 9. 当前验证命令

主流程：

python main.py

Dify 基础 smoke：

python scripts/run_dify_http_adapter_smoke.py

Dify integration smoke：

python scripts/run_dify_integration_smoke.py

Multi-asset success smoke：

python scripts/run_multi_asset_dify_smoke.py

Multi-asset negative smoke：

python scripts/run_multi_asset_error_dify_smoke.py

完整测试：

python -m pytest -q

当前预期：

- events_recorded: 8
- status completed
- 127 passed

## 10. 安全边界

P4-D12 不接真实交易所 API。
P4-D12 不保存真实 API key。
P4-D12 不读取钱包私钥。
P4-D12 不真实下单。
P4-D12 不让 Dify 成为底层交易内核。
P4-D12 不把 pipeline 成功伪装成真实交易成功。

## 11. 验收结论

P4-D12 完成后，Phase 4 的 multi-asset schema 能力达到阶段验收点。

当前系统已经具备：

- 多资产 fixture
- 多资产 schema normalization
- 多资产 pipeline batch
- 多资产 Dify batch success smoke
- 多资产 Dify batch error smoke
- 稳定 user-facing success response
- 稳定 user-facing error response

当前仍然是 mock / fixture。
当前不接真实数据源。
当前不接真实交易所 API。
当前不真实下单。

