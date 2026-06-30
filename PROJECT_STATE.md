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

Phase 3 已启动，当前重点是数据接入边界、mock 数据接入、可回放输入和本地外部调用边界。

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 多资产 MarketContext 基础层已完成阶段验收。

Phase 3 已启动。

当前完成到：

P3-D4：本地 system input pipeline / 外部调用边界，已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1 到 P2-D10: Phase 2 多资产市场上下文基础层，已完成阶段验收。

P3-D1: 真实数据接入边界规划，已完成。

P3-D2: mock market data adapter，已完成。

P3-D3: replayable raw market fixture，已完成。

P3-D4: 本地 system input pipeline / 外部调用边界，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 52 passed

## 当前关键提交

- 88b67a4 add P3 replayable raw market fixture
- 12181b5 update state after P3 replayable raw market fixture
- 7a6ee83 add P3 market input pipeline

## P3-D4 完成内容

新增文件：

- fcf/pipelines/__init__.py
- fcf/pipelines/market_input_pipeline.py
- tests/test_market_input_pipeline.py

完成能力：

- 新增本地 market input pipeline
- 输入 raw market dict
- 调用 mock_market_data_adapter
- 生成 fcf.market.raw_received 事件
- 保存到 EventStore
- 调用 ReplayEngine 回放
- 输出可供外部系统调用的 summary dict
- 支持单条 raw market input
- 支持 batch raw market input
- 支持 fixture rows 输入
- 为后续 Dify workflow 接入做准备
- 不接真实交易所 API
- 不保存密钥
- 不真实下单
- 不修改 main.py
- 不破坏当前测试

## Dify 接入位置

Dify 不是底层交易内核。

Dify 应作为后续上层工作流 / 对话入口 / 编排层。

当前已经完成 Dify 接入前的关键准备：

- mock market data adapter
- replayable raw market fixture
- market input pipeline
- 外部调用 summary dict

下一步进入 P3-D5：

Dify workflow 接入规划。

## 下一步任务

进入 P3-D5：Dify workflow 接入规划。

P3-D5 目标：

- 新增 Dify 接入规划文档
- 明确 Dify 不直接接交易所 API
- 明确 Dify 不真实下单
- 明确 Dify 只调用受控 pipeline
- 明确 Dify 输入字段
- 明确 Dify 输出 summary
- 明确 Dify workflow 节点结构
- 明确 Dify 与 FCF 本地系统的边界
- 保持 python main.py 输出 events_recorded: 8
- 保持 python -m pytest -q 通过

建议新增：

- docs/16_dify_workflow_integration_plan.md

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 7a6ee83
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成稳定收尾，D1-D11 已完成。Phase 2 多资产市场上下文基础层已完成阶段验收，P2-D1 到 P2-D10 已完成。Phase 3 已启动，P3-D1 真实数据接入边界规划已完成，P3-D2 mock market data adapter 已完成，P3-D3 replayable raw market fixture 已完成，P3-D4 本地 system input pipeline / 外部调用边界已完成。当前系统不是足球系统，也不是 BTC-only；BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。当前主事件链仍为 8 个事件，python main.py 输出 events_recorded: 8，python -m pytest -q 预计显示 52 passed。Dify 不作为底层交易内核，下一步进入 P3-D5 做 workflow 接入规划。
next_action: 先更新 README.md 和 PROJECT_STATE.md，把 P3-D4 标记为已完成并提交。然后进入 P3-D5：Dify workflow 接入规划，新增 docs/16_dify_workflow_integration_plan.md。Dify 不直接接交易所 API，不真实下单，只调用受控 pipeline。
要求：全程用中文一步步指挥我操作；命令必须给可直接复制的 Git Bash 格式；多行 cat 写文件必须包含完整 EOF；每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
