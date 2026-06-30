# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

当前系统已经完成：

- Phase 1 Build Spine 稳定收尾
- Phase 2 多资产市场上下文基础层阶段验收

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 多资产 MarketContext 基础层已完成阶段验收。

当前完成到：

P2-D10：Phase 2 多资产市场上下文阶段验收与收尾，已完成。

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

P2-D10: Phase 2 多资产市场上下文阶段验收与收尾，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 37 passed

## 当前关键提交

- 2bbcf12 standardize base market context constants
- 13af778 update state after P2 base context standardization
- af89da6 add P2 market context acceptance summary

## P2-D10 完成内容

新增文件：

- docs/14_phase2_market_context_acceptance.md

完成内容：

- 总结 P2-D1 到 P2-D9 已完成内容
- 固化 Phase 2 多资产市场上下文基础层
- 确认 BTCMarketContext 是 crypto/BTC 第一实现，不是项目终点
- 确认 BaseMarketContext 已作为通用多资产上下文契约
- 确认 market_constants 已作为 asset_class / market_type 标准化工具
- 确认 market_context_adapter 已完成 BTC 到 Base 的轻量兼容桥
- 确认 MarketContext 可以进入 FCFEvent / EventStore / ReplayEngine
- 确认 main.py 仍稳定输出 events_recorded: 8
- 确认 python -m pytest -q 仍稳定显示 37 passed
- 不接真实交易所 API
- 不真实下单
- 不破坏 main.py 主事件链

## 当前架构基础

当前已经形成：

- 事件契约层：FCFEvent
- 事件记录层：EventStore
- 回放验证层：ReplayEngine
- 市场上下文第一实现：BTCMarketContext
- 通用市场上下文契约：BaseMarketContext
- 多资产标准常量：market_constants
- 市场上下文 adapter：market_context_adapter
- market context 事件化测试
- Phase 2 阶段验收文档

## 下一步任务

进入 Phase 3：真实数据接入边界规划。

Phase 3 初期仍然不直接接真实交易所 API 密钥。

Phase 3 初期仍然不真实下单。

Phase 3 第一阶段建议：

- 创建数据源边界文档
- 规划 mock data adapter
- 规划 raw market data schema
- 规划 replayable input fixture
- 定义数据接入安全边界
- 定义真实 API 接入前的隔离层
- 保持当前 37 个测试通过

建议新增：

- docs/15_phase3_data_ingestion_boundary.md

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: af89da6
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成稳定收尾，D1-D11 已完成。Phase 2 多资产市场上下文基础层已完成阶段验收，P2-D1 到 P2-D10 已完成。当前系统不是足球系统，也不是 BTC-only；BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。当前已完成 BTCMarketContext、BaseMarketContext、market_constants、market_context_builder、market_context_adapter、market context 事件化测试，以及 docs/14_phase2_market_context_acceptance.md 阶段验收文档。当前主事件链仍为 8 个事件，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 37 passed。最新阶段验收提交为 af89da6 add P2 market context acceptance summary。
next_action: 进入 Phase 3：真实数据接入边界规划。Phase 3 初期只做数据源边界文档、mock data adapter、raw market data schema、replayable input fixture；不要接真实交易所 API 密钥，不真实下单，不破坏现有测试。建议先创建 docs/15_phase3_data_ingestion_boundary.md。
要求：全程用中文一步步指挥我操作；命令必须给可直接复制的 Git Bash 格式；多行 cat 写文件必须包含完整 EOF；每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
