cat > PROJECT_STATE.md <<'EOF'
[200~cat > PROJECT_STATE.md <<'EOF'
# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

BTC / 加密货币交易系统的事件驱动最小骨架。

不是足球系统。

系统核心目标是：

- 用统一事件契约记录交易链路
- 用 EventStore 保存事件
- 用 ReplayEngine 回放验证
- 用 risk_guardian 控制风险
- 用 executor / shadow_simulator 区分执行与影子模拟
- 为后续 BTC 市场上下文、策略候选、风控审计打基础

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 已启动。

当前完成到：

P2-D2：BTCMarketContext 契约已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1: BTC Market Context 规划，已完成。

P2-D2: BTCMarketContext 契约，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 11 passed

## 当前关键提交

- 197c893 add P2 BTC market context plan
- 88ef746 update state for P2 BTC market context
- 21e7218 add P2 BTC market context contract

## P2-D2 完成内容

新增文件：

- fcf/contracts/market_context.py
- tests/test_market_context.py

完成能力：

- 定义 BTCMarketContext 数据结构
- 支持 to_dict
- 支持 market_context_from_dict
- 增加 3 个最小测试
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py 事件链

## 下一步任务

进入 P2-D3：BTCMarketContext 最小标准化模块。

建议新增文件：

- fcf/modules/market_context_builder.py
- tests/test_market_context_builder.py

P2-D3 目标：

- 输入原始 BTC market dict
- 输出 BTCMarketContext
- 自动计算 spread
- 自动计算 orderbook_imbalance
- 自动标记 data_quality_level
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py 事件链

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: BTC / 加密货币交易系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动，P2-D1 BTC Market Context 规划已完成，P2-D2 BTCMarketContext 契约已完成。当前系统已有 8 个最小事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 11 passed。P2-D2 提交为 21e7218 add P2 BTC market context contract。
next_action: 进入 P2-D3：创建 BTCMarketContext 最小标准化模块 fcf/modules/market_context_builder.py，并增加 tests/test_market_context_builder.py。输入原始 BTC market dict，输出 BTCMarketContext，自动计算 spread、orderbook_imbalance，并标记 data_quality_level。不接真实交易所 API，不真实下单，不修改 main.py 事件链。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
EOF~
