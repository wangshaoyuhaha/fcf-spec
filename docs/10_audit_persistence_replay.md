# D10 审计日志 / 持久化 / 回放一致性

## 目标
构建统一 EventStore，使系统具备：

- 事件持久化（JSONL）
- 可回放（ReplayEngine 从文件恢复）
- 审计日志完整链路
- 与 D9 风控/执行/影子系统一致

## 核心模块

### 1. EventStore
职责：
- 写入事件到本地 JSONL 文件
- 按顺序追加
- 支持 flush

接口：
- append(event)
- load_all()

存储格式：
每行一个 JSON：
{
  "event_id": "",
  "type": "",
  "timestamp": "",
  "payload": {}
}

---

### 2. ReplayEngine（增强版）
职责：
- 从 EventStore 读取事件
- 重建事件流
- 支持 deterministic replay

接口：
- replay(file_path)
- rebuild_state()

---

### 3. 一致性要求
必须保证：

- 写入顺序 = 回放顺序
- replay 后 event chain hash 一致
- shadow / execution 不参与 replay 干扰

---

## D10 验收标准

- [ ] EventStore 写入 jsonl 成功
- [ ] ReplayEngine 可完整读取
- [ ] replay 输出 events == main run events
- [ ] pytest 增加一致性测试通过

