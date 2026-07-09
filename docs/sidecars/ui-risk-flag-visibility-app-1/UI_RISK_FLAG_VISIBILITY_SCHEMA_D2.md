# UI-RISK-FLAG-VISIBILITY-APP-1 D2 风险元数据保护字段清单

状态：D2 Protected Risk Metadata Schema
范围：sidecar-only
核心边界：P1-P47 冻结；禁止 P48；禁止 core mutation。
运行边界：paper-only / local-only / read-only / operator review required。

## 目标

本阶段定义 UI、handoff、review、dashboard、export、archive 等展示层必须保留的风险元数据字段。

D2 只做治理与可见性约束。
D2 不新增交易能力。
D2 不接入 broker / exchange API。
D2 不读取或使用 API key。
D2 不创建真实订单、真实仓位、真实账户、真实执行。
D2 不修改 core。

## 必须保护的字段

以下字段只要在上游数据包、候选项、报告、归档项、review packet 中出现，下游展示层就必须原样保留或显式展示：

- risk_flags
- reason_codes
- review_status
- blocked_reasons
- conflict_signals
- missing_required_fields
- unsafe_permissions
- operator_review_required
- circuit_break
- correlation_id
- source_artifact
- evidence_chain_status

## 字段展示规则

### risk_flags

必须显式展示原始风险旗标。

禁止：

- 隐藏 risk_flags
- 用一句安全摘要替代 risk_flags
- 只用颜色或图标替代原始风险旗标
- 把风险旗标改写成不可审计的模糊文字

### reason_codes

必须保持机器可读，同时对人类可见。

禁止：

- 删除 reason_codes
- 将多个 reason_codes 合并成一个模糊原因
- 只保留解释文本、不保留原始 reason_codes

### review_status

必须显式展示 review_status。

如果 review_status 为 REVIEW_REQUIRED，下游不得自动通过。

### blocked_reasons

只要存在 blocked_reasons，就必须显式展示。

blocked_reasons 不得被弱化为 minor issue、looks fine、safe、approved。

### conflict_signals

只要存在 conflict_signals，就必须显式展示。

任何 conflict_signals 都必须进入 operator review。

### missing_required_fields

只要存在 missing_required_fields，就必须显式展示。

任何 missing_required_fields 都必须进入 operator review。

### unsafe_permissions

只要存在 unsafe_permissions，就必须显式展示。

任何 unsafe_permissions 都必须进入 operator review。

### circuit_break

只要出现 circuit_break，就必须显式展示。

CIRCUIT_BREAK 不允许降级。

### correlation_id

只要存在 correlation_id，就必须保留，用于审计追踪。

### source_artifact

只要存在 source_artifact，就必须保留，用于 artifact chain 追踪。

### evidence_chain_status

如果 evidence_chain_status 是 stale、incomplete、missing、unresolved，必须显式展示，并进入 operator review。

## 最小可见性数据包字段

合规的数据包至少应保留以下风险治理字段：

- risk_flags
- reason_codes
- review_status
- blocked_reasons
- conflict_signals
- missing_required_fields
- unsafe_permissions
- operator_review_required
- circuit_break
- correlation_id
- source_artifact
- evidence_chain_status

## D2 验收标准

D2 通过条件：

- 风险元数据保护字段清单已写入 repo
- risk_flags 和 reason_codes 必须显式可见
- REVIEW_REQUIRED 不得自动通过
- CIRCUIT_BREAK 不得降级
- conflict_signals 必须保留并进入 operator review
- missing_required_fields 必须保留并进入 operator review
- unsafe_permissions 必须保留并进入 operator review
- correlation_id 和 source_artifact 存在时必须保留
- evidence_chain_status 异常时必须进入 operator review
- 测试覆盖以上约束
