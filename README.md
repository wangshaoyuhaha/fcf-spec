# FCF Spec

FCF Spec 是一个足球交易 / 决策系统的最小事件骨架项目。

当前阶段：

- Phase 1 Build Spine
- D1-D10 已完成
- D11 正在进行 Phase 1 骨架验收与收尾

## 当前能力

当前系统已经具备一条最小事件链：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

当前已经完成：

- FCFEvent 事件契约
- EventBus
- EventStore
- ReplayEngine
- 数据标准化模块
- regime 检测模块
- decision proposer
- policy engine
- risk guardian
- executor
- shadow simulator
- JSONL 事件持久化
- JSONL 事件读取
- ReplayEngine 回放一致性测试

## 当前验证方式

运行最小主流程：

```bash
python main.py
cat > README.md <<'EOF'
# FCF Spec

FCF Spec 是一个足球交易 / 决策系统的最小事件骨架项目。

当前阶段：

- Phase 1 Build Spine
- D1-D10 已完成
- D11 正在进行 Phase 1 骨架验收与收尾

## 当前能力

当前系统已经具备一条最小事件链：

1. fcf.data.raw_received
2. fcf.data.normalized
3. fcf.regime.detected
4. fcf.decision.proposed
5. fcf.policy.reviewed
6. fcf.order.approved
7. fcf.order.executed
8. fcf.shadow.simulated

当前已经完成：

- FCFEvent 事件契约
- EventBus
- EventStore
- ReplayEngine
- 数据标准化模块
- regime 检测模块
- decision proposer
- policy engine
- risk guardian
- executor
- shadow simulator
- JSONL 事件持久化
- JSONL 事件读取
- ReplayEngine 回放一致性测试

## 当前验证方式

运行最小主流程：

```bash
python main.py
