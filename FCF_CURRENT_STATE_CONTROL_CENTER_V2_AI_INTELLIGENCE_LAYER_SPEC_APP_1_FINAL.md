# FCF_CURRENT_STATE_CONTROL_CENTER_V2_AI_INTELLIGENCE_LAYER_SPEC_APP_1_FINAL

## 当前状态

CONTROL-CENTER-V2-AI-INTELLIGENCE-LAYER-SPEC-APP-1 已完成。

本阶段只更新主控和 handoff 文件，不开发新 sidecar，不修改 core，不创建 P48，不 tag，不 release，不 deploy。

## 最新已确认 main

- commit: 9d9b859 record FCF V2 AI intelligence layer in control center
- validation: python scripts/run_all_checks.py = ALL CHECKS PASSED
- pytest: 2082 passed
- git status: clean
- origin/main: synced

## 本次同步目标

将 Google / DeepSeek 讨论后的有用结论同步到项目活跃主控文件，避免后续窗口遗忘。

## FCF V2 主控定位

FCF V2 = 确定性金融计算引擎 + 可控 AI 智能认知层。

AI 是高级金融研究员，不是交易员、执行器、下单系统、仓位管理器或收益保证器。

## V2 推荐顺序

1. AI-CONTEXT-EVIDENCE-CONTRACT-APP-1
2. AI-CONTRARIAN-CHALLENGE-APP-1
3. DASHBOARD-CONTRADICTION-SCANNER-APP-1
4. MARKET-NARRATIVE-CONTEXT-APP-1
5. AI-SCENARIO-SIMULATION-APP-1
6. AI-ORCHESTRATION-ROADMAP-APP-1

## 不采纳或修正

- 不回退执行旧阶段。
- 不立即上自动新闻/叙事吞吐。
- 不取消 Dashboard Scanner。
- 不马上做完整 Orchestrator。
- 不把 pytest 数量当成唯一 AI 质量指标。
- 不让 AI 进入 core。
- 不让 AI 接触交易执行。

## 落地硬规则

每个 V2 sidecar 必须有输入 contract、输出 contract、可运行 loader 或 generator、本地样例数据、pytest 测试、forbidden action 测试、artifact / handoff 输出、final current state、run_all_checks、push 后 git clean。

AI 阶段必须额外覆盖幻觉输入测试、证据缺失测试、风险隐藏测试、挑战失败测试、人工复核必须存在测试。

## 安全边界

paper-only / local-only / read-only / sidecar-only / operator review required。

禁止真实交易、真实执行、broker/exchange API、API key、wallet private key、real account、real position、buy/sell/order、自动仓位、自动组合动作、收益保证、tag、release、deploy。
