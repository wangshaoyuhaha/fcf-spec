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

market_constants 是多资产 asset_class / market_type 标准常量与验证工具。

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 已启动。

当前完成到：

P2-D9：BaseMarketContext 使用 market_constants 标准化已完成。

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

P2-D9: BaseMarketContext 使用 market_constants 标准化，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 37 passed

## 当前关键提交

- 1e11362 add P2 market constants
- 0cd8eb2 update state after P2 market constants
- 2bbcf12 standardize base market context constants

## P2-D9 完成内容

修改文件：

- fcf/contracts/base_market_context.py
- tests/test_base_market_context.py

完成能力：

- BaseMarketContext 使用 market_constants.normalize_asset_class
- BaseMarketContext 使用 market_constants.normalize_market_type
- BaseMarketContext 新增 normalized_market_type
- BaseMarketContext.to_dict 输出标准化后的 asset_class
- BaseMarketContext.to_dict 输出标准化后的 market_type
- base_market_context_from_dict 标准化 asset_class
- base_market_context_from_dict 标准化 market_type
- 增加 3 个最小测试
- 不迁移 BTCMarketContext
- 不删除 BTCMarketContext
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py
- 不破坏当前 37 个测试

## 下一步任务

进入 P2-D10：Phase 2 多资产市场上下文阶段验收与收尾。

P2-D10 目标：

- 不继续无限加功能
- 总结 P2-D1 到 P2-D9 已完成内容
- 固化当前多资产 MarketContext 基础层
- 确认 main.py 仍稳定输出 events_recorded: 8
- 确认 python -m pytest -q 仍稳定通过
- 更新 README.md
- 更新 PROJECT_STATE.md
- 生成新的续聊话术

建议新增：

- docs/14_phase2_market_context_acceptance.md

P2-D10 完成后，再进入下一阶段：

- Phase 3：真实数据接入边界规划
- 仍然不直接接真实交易所 API 密钥
- 仍然不真实下单

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: 全金融市场 / 多资产交易事件系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动。P2-D1 到 P2-D9 已完成。当前已新增 BTCMarketContext、BaseMarketContext、market_constants、market_context_adapter，并完成 market context 事件化测试。BTCMarketContext 是第一个 crypto/BTC 市场样板，不是项目终点。当前系统已有 8 个最小主事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 37 passed。最新代码提交为 2bbcf12 standardize base market context constants。
next_action: 先更新 README.md 和 PROJECT_STATE.md，提交 P2-D9 状态收尾。然后进入 P2-D10：Phase 2 多资产市场上下文阶段验收与收尾，新增 docs/14_phase2_market_context_acceptance.md。不要继续无限加功能，不接真实交易所 API，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
