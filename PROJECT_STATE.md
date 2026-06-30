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

Phase 3 已启动，当前重点是数据接入边界、mock 数据接入和可回放输入。

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 多资产 MarketContext 基础层已完成阶段验收。

Phase 3 已启动。

当前完成到：

P3-D3：replayable raw market fixture，已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1 到 P2-D10: Phase 2 多资产市场上下文基础层，已完成阶段验收。

P3-D1: 真实数据接入边界规划，已完成。

P3-D2: mock market data adapter，已完成。

P3-D3: replayable raw market fixture，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 48 passed

## 当前关键提交

- f0b5b8d add P3 mock market data adapter
- 490f515 update state after P3 mock market data adapter
- 88b67a4 add P3 replayable raw market fixture

## P3-D3 完成内容

新增文件：

- fixtures/raw_market_data_crypto.json
- tests/test_raw_market_fixture_replay.py

完成能力：

- 新增本地 crypto raw market fixture
- fixture 包含 BTCUSDT 和 ETHUSDT 两条样本数据
- fixture 可驱动 mock_market_data_adapter
- fixture 可生成 fcf.market.raw_received 事件
- EventStore 可保存 fixture 生成的 raw market events
- ReplayEngine 可回放 fixture 生成的 raw market events
- 不接真实交易所 API
- 不保存密钥
- 不真实下单
- 不修改 main.py
- 不破坏当前 48 个测试

## Dify 接入位置

Dify 不是底层交易内核。

Dify 应作为后续上层工作流 / 对话入口 / 编排层。

建议路线：

- P3-D4：本地 system input pipeline / 外部调用边界
- P3-D5：Dify workflow 接入规划

也就是说，Dify 预计在 P3-D5 正式进入规划。

## 下一步任务

进入 P3-D4：本地 system input pipeline / 外部调用边界。

P3-D4 目标：

- 新增一个本地 pipeline 入口
- 输入 raw market dict
- 调用 mock_market_data_adapter
- 生成 raw market event
- 保存到 EventStore
- 调用 ReplayEngine 回放
- 输出可给外部系统调用的 summary dict
- 为后续 Dify workflow 接入做准备
- 不接真实交易所 API
- 不真实下单
- 不破坏当前 48 个测试

建议新增：

- fcf/pipelines/market_input_pipeline.py
- tests/test_market_input_pipeline.py

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 88b67a4
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成稳定收尾，D1-D11 已完成。Phase 2 多资产市场上下文基础层已完成阶段验收，P2-D1 到 P2-D10 已完成。Phase 3 已启动，P3-D1 真实数据接入边界规划已完成，P3-D2 mock market data adapter 已完成，P3-D3 replayable raw market fixture 已完成。当前系统不是足球系统，也不是 BTC-only；BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。当前主事件链仍为 8 个事件，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 48 passed。Dify 不作为底层交易内核，预计在 P3-D5 做 workflow 接入规划。
next_action: 先更新 README.md 和 PROJECT_STATE.md，把 P3-D3 标记为已完成并提交。然后进入 P3-D4：本地 system input pipeline / 外部调用边界，新增 fcf/pipelines/market_input_pipeline.py 和 tests/test_market_input_pipeline.py。Phase 3 初期不要接真实交易所 API 密钥，不真实下单，不破坏现有测试。
要求：全程用中文一步步指挥我操作；命令必须给可直接复制的 Git Bash 格式；多行 cat 写文件必须包含完整 EOF；每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
