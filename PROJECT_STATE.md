# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTC 是 Phase 2 的第一个市场样板和第一类 MarketContext 实现。

系统未来需要逐步适配：

- crypto: BTC, ETH, SOL 等
- FX: EURUSD, USDJPY 等
- equities: AAPL, TSLA, SPY 等
- futures: ES, NQ, CL, GC 等
- commodities: oil, gold 等
- rates / bonds: 利率、国债、收益率相关市场

系统核心目标是：

- 用统一事件契约记录交易链路
- 用 EventStore 保存事件
- 用 ReplayEngine 回放验证
- 用 risk_guardian 控制风险
- 用 executor / shadow_simulator 区分执行与影子模拟
- 先用 BTCMarketContext 跑通第一个市场上下文
- 后续逐步抽象为通用 MarketContext / AssetMarketContext

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 已启动。

当前完成到：

P2-D3：BTCMarketContext 最小标准化模块已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1: BTC Market Context 规划，已完成。

P2-D2: BTCMarketContext 契约，已完成。

P2-D3: BTCMarketContext 最小标准化模块，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 15 passed

## 当前关键提交

- 197c893 add P2 BTC market context plan
- 88ef746 update state for P2 BTC market context
- 21e7218 add P2 BTC market context contract
- 8143ec7 update state after P2 BTC market context contract
- 5d11c7c add P2 BTC market context builder
- 185e448 update state after P2 BTC market context builder

## 重要定位纠偏

项目不是 BTC-only。

当前 BTCMarketContext 是第一版 crypto/BTC 市场上下文实现。

后续需要逐步泛化为：

- 通用 MarketContext
- AssetMarketContext
- CryptoMarketContext
- EquityMarketContext
- FuturesMarketContext
- FXMarketContext

现阶段不急着重命名已有文件，避免破坏已经通过的测试。

P2-D4 之后再规划泛化层。

## P2-D3 完成内容

新增文件：

- fcf/modules/market_context_builder.py
- tests/test_market_context_builder.py

完成能力：

- 输入原始 BTC market dict
- 输出 BTCMarketContext
- 自动计算 spread
- 自动计算 orderbook_imbalance
- 自动标记 data_quality_level
- 支持字符串数值转 float
- 对关键必填数字字段做 ValueError 校验
- 增加 4 个最小测试
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py 事件链

## 下一步任务

进入 P2-D4：market context 事件化。

P2-D4 目标：

- 不接真实交易所 API
- 不真实下单
- 不破坏现有 main.py
- 把 BTCMarketContext 放进 FCFEvent payload
- 验证 MarketContext 可以进入统一事件系统
- 验证 EventStore 可以保存包含 MarketContext 的事件
- 验证 ReplayEngine 可以回放相关事件
- 为后续多资产 MarketContext 泛化做准备

建议新增或修改：

- tests/test_market_context_event_flow.py

P2-D4 重点不是新增复杂策略，而是证明市场上下文可以进入现有事件系统。

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: 全金融市场 / 多资产交易事件系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动。当前 BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。P2-D1 BTC Market Context 规划已完成，P2-D2 BTCMarketContext 契约已完成，P2-D3 BTCMarketContext 最小标准化模块已完成。当前系统已有 8 个最小事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 15 passed。最新状态提交为 185e448 update state after P2 BTC market context builder。
next_action: 进入 P2-D4：market context 事件化。把 BTCMarketContext 放进 FCFEvent payload，验证 EventStore 可保存、ReplayEngine 可回放。注意项目目标是全金融市场适配，BTC 只是第一实现；不要把系统写死为 BTC-only。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
