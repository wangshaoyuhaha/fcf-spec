# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

BaseMarketContext 是当前新增的通用多资产上下文契约。

系统未来需要逐步适配：

- crypto: BTC, ETH, SOL 等
- FX: EURUSD, USDJPY 等
- equities: AAPL, TSLA, SPY 等
- futures: ES, NQ, CL, GC 等
- commodities: oil, gold 等
- rates / bonds: 利率、国债、收益率相关市场

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 已启动。

当前完成到：

P2-D7：asset_class 标准化与 BTCMarketContext 轻量兼容桥已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1: BTC Market Context 规划，已完成。

P2-D2: BTCMarketContext 契约，已完成。

P2-D3: BTCMarketContext 最小标准化模块，已完成。

P2-D4: market context 事件化测试，已完成。

P2-D5: 多资产 MarketContext / AssetMarketContext 泛化层规划，已完成。

P2-D6: 通用 BaseMarketContext 最小契约，已完成。

P2-D7: BTCMarketContext 到 BaseMarketContext 轻量兼容桥，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 27 passed

## 当前关键提交

- 7d28195 add P2 base market context contract
- 61ea7e1 update state after P2 base market context contract
- f30ae80 add P2 market context adapter

## P2-D7 完成内容

新增文件：

- fcf/modules/market_context_adapter.py
- tests/test_market_context_adapter.py

完成能力：

- BTCMarketContext 可以转换为 BaseMarketContext
- 自动推断 crypto symbol 的 currency / quote_currency
- BTCMarketContext 可以生成统一事件 payload
- 转换后的 BaseMarketContext 可以进入 FCFEvent payload
- EventStore 可以保存转换后的 market context 事件
- ReplayEngine 可以回放转换后的 market context 事件
- 增加 3 个最小测试
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py
- 不破坏当前 27 个测试

## 下一步任务

进入 P2-D8：多资产 asset_class / market_type 标准常量与验证工具。

P2-D8 目标：

- 定义统一 asset_class 常量
- 定义统一 market_type 常量
- 定义 normalize / validate 工具
- 为 crypto、fx、equity、futures、commodity、rates、bond、index 建立基础标准
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不破坏现有测试
- 不接真实交易所 API
- 不真实下单

建议新增：

- fcf/contracts/market_constants.py
- tests/test_market_constants.py

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: 全金融市场 / 多资产交易事件系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动。BTCMarketContext 是第一个 crypto/BTC 市场样板，不是项目终点。P2-D1 到 P2-D7 已完成。当前已新增 BaseMarketContext 通用契约，并新增 BTCMarketContext 到 BaseMarketContext 的轻量兼容桥。当前系统已有 8 个最小主事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 27 passed。最新代码提交为 f30ae80 add P2 market context adapter。
next_action: 先更新 README.md 和 PROJECT_STATE.md，提交 P2-D7 状态收尾。然后进入 P2-D8：多资产 asset_class / market_type 标准常量与验证工具，新增 fcf/contracts/market_constants.py 和 tests/test_market_constants.py。不迁移、不删除、不破坏 BTCMarketContext，不接真实交易所 API，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
