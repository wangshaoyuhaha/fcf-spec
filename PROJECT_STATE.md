# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

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
- 已新增 BaseMarketContext 作为通用多资产上下文契约
- 后续逐步形成 AssetMarketContext / CryptoMarketContext / FXMarketContext / EquityMarketContext 等扩展层

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 已启动。

当前完成到：

P2-D6：通用 BaseMarketContext 最小契约已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1: BTC Market Context 规划，已完成。

P2-D2: BTCMarketContext 契约，已完成。

P2-D3: BTCMarketContext 最小标准化模块，已完成。

P2-D4: market context 事件化测试，已完成。

P2-D5: 多资产 MarketContext / AssetMarketContext 泛化层规划，已完成。

P2-D6: 通用 BaseMarketContext 最小契约，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 24 passed

## 当前关键提交

- 0eb07a9 add P2 multi asset market context plan
- 2638670 update state after P2 multi asset context plan
- 7d28195 add P2 base market context contract

## P2-D6 完成内容

新增文件：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

完成能力：

- 定义 BaseMarketContext 数据结构
- 支持 asset_class
- 支持 symbol
- 支持 venue
- 支持 market_type
- 支持 timestamp
- 支持 timeframe
- 支持 currency / quote_currency
- 支持价格、流动性、波动率、市场状态、风险字段
- 支持 to_dict
- 支持 base_market_context_from_dict
- 支持 normalize_asset_class
- 增加 6 个最小测试
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py
- 不破坏当前 24 个测试

## 下一步任务

进入 P2-D7：asset_class 标准化与 BTCMarketContext 轻量兼容桥。

P2-D7 目标：

- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不破坏现有测试
- 增加 BTCMarketContext 到 BaseMarketContext 的轻量转换能力
- 验证 BTCMarketContext 可以转换为 BaseMarketContext
- 验证转换后仍可进入 FCFEvent payload
- 验证 EventStore / ReplayEngine 仍可处理
- 不接真实交易所 API
- 不真实下单

建议新增：

- fcf/modules/market_context_adapter.py
- tests/test_market_context_adapter.py

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: 全金融市场 / 多资产交易事件系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动。BTCMarketContext 是第一个 crypto/BTC 市场样板，不是项目终点。P2-D1 到 P2-D6 已完成。当前已新增 BaseMarketContext 通用契约。当前系统已有 8 个最小主事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 24 passed。最新代码提交为 7d28195 add P2 base market context contract。
next_action: 先更新 README.md 和 PROJECT_STATE.md，提交 P2-D6 状态收尾。然后进入 P2-D7：asset_class 标准化与 BTCMarketContext 轻量兼容桥，新增 fcf/modules/market_context_adapter.py 和 tests/test_market_context_adapter.py。不迁移、不删除、不破坏 BTCMarketContext，不接真实交易所 API，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
