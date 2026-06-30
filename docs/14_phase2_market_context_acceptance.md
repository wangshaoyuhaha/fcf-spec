# P2-D10 - Phase 2 多资产市场上下文阶段验收与收尾

## 1. 目的

P2-D10 的目标是对 Phase 2 当前已经完成的多资产市场上下文基础层做一次阶段验收。

本阶段不继续无限加功能。

本阶段重点是确认：

- Phase 1 主事件链仍然稳定
- Phase 2 MarketContext 基础层已经形成
- BTCMarketContext 作为第一实现可以工作
- BaseMarketContext 作为通用上下文契约可以工作
- market_constants 已经提供多资产标准化基础
- market_context_adapter 已经完成 BTC 到 Base 的轻量兼容桥
- EventStore / ReplayEngine 可以处理 market context 事件
- 当前测试稳定通过

## 2. 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

系统未来需要逐步适配：

- crypto
- FX
- equities
- futures
- commodities
- rates / bonds
- index

## 3. Phase 1 当前状态

Phase 1 Build Spine 已完成稳定收尾。

当前主事件链仍为 8 个事件：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

当前运行：

python main.py

预期输出：

- FCF minimal spine executed.
- events_recorded: 8

## 4. Phase 2 已完成内容

### P2-D1：BTC Market Context 规划

新增：

- docs/12_phase2_btc_market_context.md

完成：

- 规划 BTCMarketContext 第一版字段
- 明确 Phase 2 初期不真实下单
- 明确 BTC 是第一市场样板
- 明确不破坏 Phase 1 主事件链

### P2-D2：BTCMarketContext 契约

新增：

- fcf/contracts/market_context.py
- tests/test_market_context.py

完成：

- 定义 BTCMarketContext 数据结构
- 支持 to_dict
- 支持 market_context_from_dict
- 增加最小测试

### P2-D3：BTCMarketContext 最小标准化模块

新增：

- fcf/modules/market_context_builder.py
- tests/test_market_context_builder.py

完成：

- 输入原始 BTC market dict
- 输出 BTCMarketContext
- 自动计算 spread
- 自动计算 orderbook_imbalance
- 自动标记 data_quality_level
- 支持字符串数值转 float
- 对关键必填数字字段做 ValueError 校验

### P2-D4：market context 事件化测试

新增：

- tests/test_market_context_event_flow.py

完成：

- BTCMarketContext 可以进入 FCFEvent payload
- EventStore 可以保存包含 MarketContext 的事件
- EventStore 可以从 JSONL 读取该事件
- ReplayEngine 可以回放相关事件

### P2-D5：多资产 MarketContext 泛化层规划

新增：

- docs/13_multi_asset_market_context.md

完成：

- 明确项目是全金融市场 / 多资产交易事件系统
- 明确 BTCMarketContext 是第一实现，不是终点
- 规划通用 MarketContext 字段
- 规划不同资产类别扩展边界

### P2-D6：BaseMarketContext 通用契约

新增：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

完成：

- 定义 BaseMarketContext
- 支持 asset_class
- 支持 symbol
- 支持 venue
- 支持 market_type
- 支持 timestamp
- 支持 timeframe
- 支持 to_dict
- 支持 base_market_context_from_dict

### P2-D7：BTCMarketContext 到 BaseMarketContext 兼容桥

新增：

- fcf/modules/market_context_adapter.py
- tests/test_market_context_adapter.py

完成：

- BTCMarketContext 可以转换为 BaseMarketContext
- 自动推断 crypto symbol 的 currency / quote_currency
- 转换后的 BaseMarketContext 可以进入 FCFEvent payload
- EventStore / ReplayEngine 可以处理转换后的 market context 事件

### P2-D8：market constants

新增：

- fcf/contracts/market_constants.py
- tests/test_market_constants.py

完成：

- 定义统一 asset_class 常量
- 定义统一 market_type 常量
- 支持 normalize_asset_class
- 支持 normalize_market_type
- 支持 validate_asset_class
- 支持 validate_market_type

### P2-D9：BaseMarketContext 标准化

修改：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

完成：

- BaseMarketContext 使用 market_constants.normalize_asset_class
- BaseMarketContext 使用 market_constants.normalize_market_type
- BaseMarketContext.to_dict 输出标准化 asset_class
- BaseMarketContext.to_dict 输出标准化 market_type
- base_market_context_from_dict 标准化 asset_class 和 market_type

## 5. 当前测试验收

当前运行：

python -m pytest -q

预期输出：

- 37 passed

## 6. 当前架构成果

当前已经形成：

- 事件契约层：FCFEvent
- 事件记录层：EventStore
- 回放验证层：ReplayEngine
- 市场上下文第一实现：BTCMarketContext
- 通用市场上下文契约：BaseMarketContext
- 多资产标准常量：market_constants
- 市场上下文 adapter：market_context_adapter
- market context 事件化测试

## 7. 当前不做的事情

P2-D10 不做：

- 不接真实交易所 API
- 不配置真实 API 密钥
- 不真实下单
- 不做复杂黑箱策略
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不强行重命名已通过测试的文件
- 不破坏 main.py 主事件链

## 8. P2-D10 验收标准

P2-D10 完成需要满足：

- docs/14_phase2_market_context_acceptance.md 已创建
- README.md 已更新
- PROJECT_STATE.md 已更新
- python main.py 输出 events_recorded: 8
- python -m pytest -q 显示 37 passed
- 所有变更提交并 push 到 GitHub

## 9. 下一阶段方向

P2-D10 完成后，Phase 2 多资产市场上下文基础层进入阶段稳定状态。

下一阶段建议进入 Phase 3：真实数据接入边界规划。

Phase 3 仍然不应直接接真实交易所 API 密钥。

Phase 3 第一阶段建议只做：

- 数据源边界文档
- mock data adapter
- raw market data schema
- replayable input fixture
- 不真实下单
- 不接真实账户
