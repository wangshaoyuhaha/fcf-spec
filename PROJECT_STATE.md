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

market_constants 是当前新增的多资产 asset_class / market_type 标准常量与验证工具。

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 已启动。

当前完成到：

P2-D8：多资产 asset_class / market_type 标准常量与验证工具已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1: BTC Market Context 规划，已完成。

P2-D2: BTCMarketContext 契约，已完成。

P2-D3: BTCMarketContext 最小标准化模块，已完成。

P2-D4: market context 事件化测试，已完成。

P2-D5: 多资产 MarketContext / AssetMarketContext 泛化层规划，已完成。

P2-D6: 通用 BaseMarketContext 最小契约，已完成。

P2-D7: BTCMarketContext 到 BaseMarketContext 轻量兼容桥，已完成。

P2-D8: 多资产 asset_class / market_type 标准常量与验证工具，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 34 passed

## 当前关键提交

- f30ae80 add P2 market context adapter
- a210c58 update state after P2 market context adapter
- 1e11362 add P2 market constants

## P2-D8 完成内容

新增文件：

- fcf/contracts/market_constants.py
- tests/test_market_constants.py

完成能力：

- 定义统一 asset_class 常量
- 定义统一 market_type 常量
- 支持 normalize_asset_class
- 支持 normalize_market_type
- 支持 is_supported_asset_class
- 支持 is_supported_market_type
- 支持 validate_asset_class
- 支持 validate_market_type
- 支持 crypto、fx、equity、futures、commodity、rates、bond、index
- 支持 spot、perpetual、future、option、cash、forward、swap、cfd
- 增加 7 个最小测试
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py
- 不破坏当前 34 个测试

## 下一步任务

进入 P2-D9：让 BaseMarketContext 使用 market_constants 标准化。

P2-D9 目标：

- 保持 BaseMarketContext 现有接口兼容
- 让 BaseMarketContext 使用 market_constants.normalize_asset_class
- 让 BaseMarketContext 支持 market_type 标准化
- 增加对应测试
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不破坏现有 34 个测试
- 不接真实交易所 API
- 不真实下单

建议修改：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: 全金融市场 / 多资产交易事件系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动。BTCMarketContext 是第一个 crypto/BTC 市场样板，不是项目终点。P2-D1 到 P2-D8 已完成。当前已新增 BaseMarketContext 通用契约、BTCMarketContext 到 BaseMarketContext 的轻量兼容桥，以及 market_constants 多资产常量与验证工具。当前系统已有 8 个最小主事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 34 passed。最新代码提交为 1e11362 add P2 market constants。
next_action: 先更新 README.md 和 PROJECT_STATE.md，提交 P2-D8 状态收尾。然后进入 P2-D9：让 BaseMarketContext 使用 market_constants 标准化，保持兼容并增加测试。不迁移、不删除、不破坏 BTCMarketContext，不接真实交易所 API，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
