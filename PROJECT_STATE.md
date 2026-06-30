# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

BTC / 加密货币交易系统的事件驱动最小骨架。

不是足球系统。

cat > PROJECT_STATE.md <<'EOF'
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

P2-D1：BTC Market Context 规划已完成。

## 已完成进度

D1: 项目基础骨架，已完成。
D2: 核心事件契约，已完成。
D3: EventBus / EventStore / ReplayEngine 基础骨架，已完成。
D4: 数据标准化与 regime 检测骨架，已完成。
D5: 决策候选与策略评审骨架，已完成。
D6: 最小运行时已跑通。
D7: 最小测试与回放验证，已完成。
D8: 模块代码最小落地，已完成。
D9: 风控、执行、影子模式最小闭环，已完成。
D10: 审计日志、JSONL 事件持久化与回放一致性加强，已完成。
D11: Phase 1 骨架验收与收尾，已完成。

P2-D1: BTC Market Context 规划，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8
- 事件链包含：
  1. fcf.data.raw_received
  2. fcf.data.normalized
  3. fcf.regime.detected
  4. fcf.decision.proposed
  5. fcf.policy.reviewed
  6. fcf.order.approved
  7. fcf.order.executed
  8. fcf.shadow.simulated

python -m pytest -q:

- 8 passed

## 当前关键提交

- 94f9d23 add D11 phase1 acceptance summary
- 197c893 add P2 BTC market context plan

纠偏记录：

- a4bca33 add D10 event store persistence foundation 是错误方向提交
- a8d4bd6 Revert "add D10 event store persistence foundation" 已安全撤销该错误提交

## Phase 2 当前边界

Phase 2 初期暂不做：

- 不接真实交易所 API 密钥
- 不真实下单
- 不做高杠杆实盘
- 不做自动重仓策略
- 不做不可解释黑箱模型
- 不绕过 policy_engine
- 不绕过 risk_guardian
- 不绕过 EventStore
- 不破坏 Phase 1 已经稳定的 8 事件链

## 下一步任务

进入 P2-D2：创建 BTCMarketContext 契约。

建议新增文件：

- fcf/contracts/market_context.py
- tests/test_market_context.py

P2-D2 目标：

- 定义 BTCMarketContext 数据结构
- 支持 to_dict
- 支持 market_context_from_dict
- 增加最小测试
- 不接真实交易所 API
- 不真实下单
- 不修改 main.py 事件链
- 保持 python main.py 输出 events_recorded: 8
- 保持 python -m pytest -q 通过

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
current_stage: BTC / 加密货币交易系统；Phase 1 Build Spine 已完成稳定收尾；D1-D11 已完成。Phase 2 已启动，P2-D1 BTC Market Context 规划已完成，新增 docs/12_phase2_btc_market_context.md。当前系统已有 8 个最小事件链，python main.py 输出 events_recorded: 8，python -m pytest -q 显示 8 passed。P2-D1 提交为 197c893 add P2 BTC market context plan。
next_action: 进入 P2-D2：创建 BTCMarketContext 契约文件 fcf/contracts/market_context.py，并增加 tests/test_market_context.py。只定义数据结构和测试，不接真实交易所 API，不真实下单，不修改 main.py 事件链。
要求：全程用中文一步步指挥我操作，每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。
