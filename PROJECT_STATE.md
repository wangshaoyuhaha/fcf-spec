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

P2-D4：market context 事件化测试已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1: BTC Market Context 规划，已完成。

P2-D2: BTCMarketContext 契约，已完成。

P2-D3: BTCMarketContext 最小标准化模块，已完成。

P2-D4: market context 事件化测试，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 18 passed

## 当前关键提交

- 5d11c7c add P2 BTC market context builder
- 185e448 update state after P2 BTC market context builder
- 3462a74 clarify multi-market direction after P2 builder
- e720d47 add P2 market context event flow tests

## P2-D4 完成内容

新增文件：

- tests/test_market_context_event_flow.py

完成能力：

- BTCMarketContext 可以放进 FCFEvent payload
- MarketContext 可以进入统一事件系统
- EventStore 可以保存包含 MarketContext 的事件
- EventStore 可以从 JSONL 读取该事件
- ReplayEngine 可以回放包含 MarketContext 的事件
- 增加 3 个最小事件流测试
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py 事件链

## 下一步任务

进入 P2-D5：通用 MarketContext / AssetMarketContext 泛化层规划。

P2-D5 暂不急着重命名已通过的 BTCMarketContext。

P2-D5 目标：

- 明确 BTCMarketContext 是 crypto/BTC 第一实现
- 规划通用 MarketContext 基类或协议
- 规划 asset_class 字段标准
- 规划 symbol / venue / market_type 通用字段
- 规划 crypto、equity、futures、FX 的扩展边界
- 不破坏现有 18 个测试
- 不接真实交易所 API
- 不真实下单

建议新增文档：

- docs/13_multi_asset_market_context.md

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: 全金融市场 / 多资产交易事件系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动。BTCMarketContext 是第一个 crypto/BTC 市场样板，不是项目终点。P2-D1 BTC Market Context 规划已完成，P2-D2 BTCMarketContext 契约已完成，P2-D3 BTCMarketContext 最小标准化模块已完成，P2-D4 market context 事件化测试已完成。当前系统已有 8 个最小主事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 18 passed。最新代码提交为 e720d47 add P2 market context event flow tests。
next_action: 先更新 README.md 和 PROJECT_STATE.md，提交 P2-D4 状态收尾。然后进入 P2-D5：通用 MarketContext / AssetMarketContext 泛化层规划，新增 docs/13_multi_asset_market_context.md。不要急着重命名已通过的 BTCMarketContext，不接真实交易所 API，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
