# P3-D5 - Dify Workflow 接入规划

## 1. 目的

P3-D5 的目标是规划 Dify 如何作为上层 workflow / 对话入口 / 编排层接入 FCF 系统。

Dify 不作为底层交易内核。

Dify 不直接接真实交易所 API。

Dify 不真实下单。

Dify 只调用 FCF 暴露的受控 pipeline，并接收 summary dict 作为输出。

## 2. 当前基础

当前已经完成：

- Phase 1 Build Spine
- Phase 2 多资产 MarketContext 基础层
- P3-D1 数据接入边界规划
- P3-D2 mock market data adapter
- P3-D3 replayable raw market fixture
- P3-D4 market input pipeline

当前可用本地入口：

- fcf/pipelines/market_input_pipeline.py

当前 pipeline 能力：

- 输入 raw market dict
- 调用 mock_market_data_adapter
- 生成 fcf.market.raw_received 事件
- 保存到 EventStore
- 调用 ReplayEngine 回放
- 输出 summary dict

当前验证结果：

- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 52 passed

## 3. Dify 的定位

Dify 的角色是：

- 用户交互入口
- workflow 编排层
- 参数收集层
- 结果展示层
- 人工确认层

Dify 不是：

- 交易内核
- 风控内核
- 事件存储
- 回放系统
- 真实下单系统
- 交易所 API 连接器

## 4. Dify 不允许做的事情

Dify 初期不允许：

- 不直接保存交易所 API key
- 不直接调用真实交易所 API
- 不真实下单
- 不绕过 risk_guardian
- 不绕过 EventStore
- 不绕过 ReplayEngine
- 不直接修改核心事件链
- 不执行自动重仓策略

## 5. Dify 初期输入字段规划

Dify workflow 初期可以收集以下字段：

- asset_class
- symbol
- venue
- market_type
- timestamp
- timeframe
- source
- source_type
- open
- high
- low
- close
- last_price
- volume
- quote_volume
- best_bid
- best_ask
- bid_depth
- ask_depth

这些字段会组成 raw market dict。

## 6. Dify 调用边界

Dify 不直接调用内部模块。

Dify 后续应调用一个受控入口。

当前本地候选入口：

- process_raw_market_input
- process_raw_market_batch

来源：

- fcf.pipelines.market_input_pipeline

后续如需要暴露 API，应新增 API wrapper，而不是让 Dify 直接碰内部模块。

## 7. Dify 输出 summary 规划

Dify 应展示 pipeline 返回的 summary dict。

核心输出包括：

- status
- pipeline
- correlation_id
- persisted
- event_count
- event_name
- event_id
- asset_class
- symbol
- venue
- market_type
- timeframe
- last_price
- source
- source_type
- replay.status
- replay.event_count
- replay.event_names
- replay.is_sequence_ordered
- replay.mismatch_count

## 8. 初版 Dify Workflow 节点规划

建议第一版 workflow 节点：

1. 用户输入节点
2. 字段校验节点
3. raw market dict 构造节点
4. 调用 FCF pipeline 节点
5. 展示 summary 节点
6. 人工确认节点
7. 结束节点

初版不包含真实交易所 API。

初版不包含真实下单。

## 9. 后续 API Wrapper 规划

为了让 Dify 调用更稳定，后续可以新增本地 API wrapper。

建议后续新增：

- fcf/api/local_market_input_api.py
- tests/test_local_market_input_api.py

该 wrapper 只包装 pipeline，不增加交易逻辑。

## 10. P3-D5 验收标准

P3-D5 完成需要满足：

- docs/16_dify_workflow_integration_plan.md 已创建
- 明确 Dify 不作为底层交易内核
- 明确 Dify 不直接接真实交易所 API
- 明确 Dify 不真实下单
- 明确 Dify 只调用受控 pipeline
- 明确 Dify 输入字段
- 明确 Dify 输出 summary
- 明确 Dify workflow 节点结构
- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 52 passed

## 11. 下一步

P3-D5 完成后，进入 P3-D6。

建议 P3-D6：

创建本地 API wrapper，为 Dify 后续调用做准备。

建议新增：

- fcf/api/local_market_input_api.py
- tests/test_local_market_input_api.py

P3-D6 仍然不接真实交易所 API，不真实下单。
