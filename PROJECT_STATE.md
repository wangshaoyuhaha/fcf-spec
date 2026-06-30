# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

Phase 2 多资产市场上下文基础层已完成阶段验收。

Phase 3 已启动，当前重点是数据接入边界和 mock 数据接入。

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 多资产 MarketContext 基础层已完成阶段验收。

Phase 3 已启动。

当前完成到：

P3-D2：mock market data adapter，已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1 到 P2-D10: Phase 2 多资产市场上下文基础层，已完成阶段验收。

P3-D1: 真实数据接入边界规划，已完成。

P3-D2: mock market data adapter，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 45 passed

## 当前关键提交

- f397ff8 add P3 data ingestion boundary plan
- 343fa48 update state after P3 data ingestion boundary
- f0b5b8d add P3 mock market data adapter

## P3-D2 完成内容

新增文件：

- fcf/modules/mock_market_data_adapter.py
- tests/test_mock_market_data_adapter.py

完成能力：

- 输入本地 raw market dict
- 校验必要字段
- 校验 asset_class
- 校验 market_type
- 校验关键 numeric 字段
- 输出统一 raw market event payload
- 可生成 fcf.market.raw_received 事件
- EventStore 可保存 raw market event
- ReplayEngine 可回放 raw market event
- 不调用外部 API
- 不保存密钥
- 不真实下单
- 不修改 main.py
- 不破坏当前 45 个测试

## Dify 接入位置

Dify 不是底层交易内核。

Dify 应该作为后续上层工作流 / 对话入口 / 编排层。

建议路线：

- P3-D3：replayable raw market fixture
- P3-D4：本地 system input pipeline / 外部调用边界
- P3-D5：Dify workflow 接入规划

也就是说，Dify 预计在 P3-D5 开始正式规划。

## 下一步任务

进入 P3-D3：replayable raw market fixture。

P3-D3 目标：

- 新增本地 fixture 样本数据
- 用 fixture 驱动 mock_market_data_adapter
- 生成 raw market event
- 保存到 EventStore
- ReplayEngine 可回放
- 不接真实交易所 API
- 不真实下单
- 保持 python main.py 输出 events_recorded: 8
- 保持 python -m pytest -q 通过

建议新增：

- fixtures/raw_market_data_crypto.json
- tests/test_raw_market_fixture_replay.py

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: f0b5b8d
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成稳定收尾，D1-D11 已完成。Phase 2 多资产市场上下文基础层已完成阶段验收，P2-D1 到 P2-D10 已完成。Phase 3 已启动，P3-D1 真实数据接入边界规划已完成，P3-D2 mock market data adapter 已完成。当前系统不是足球系统，也不是 BTC-only；BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。当前主事件链仍为 8 个事件，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 45 passed。Dify 不作为底层交易内核，预计在 P3-D5 做 workflow 接入规划。
next_action: 先更新 README.md 和 PROJECT_STATE.md，把 P3-D2 标记为已完成并提交。然后进入 P3-D3：replayable raw market fixture，新增 fixtures/raw_market_data_crypto.json 和 tests/test_raw_market_fixture_replay.py。Phase 3 初期不要接真实交易所 API 密钥，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作；命令必须给可直接复制的 Git Bash 格式；多行 cat 写文件必须包含完整 EOF；每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
