# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 是全金融市场 / 多资产交易事件系统。

本项目不是足球系统。
本项目不是 BTC-only。
BTCMarketContext 是第一个 crypto/BTC 市场样板实现，不是项目终点。

当前系统仍然是本地安全受控开发版本。
当前系统不接真实交易所 API。
当前系统不保存真实 API key。
当前系统不读取钱包私钥。
当前系统不真实下单。

## 当前阶段

Phase 1 Build Spine 已完成。
D1-D11 已完成。

Phase 2 多资产 MarketContext 基础层已完成。
P2-D1 到 P2-D10 已完成。

Phase 3 数据接入与 Dify integration 已完成阶段收尾。
P3-D1 到 P3-D14 已完成。

Phase 4 schema hardening 与 multi-asset fixture expansion 已完成阶段收尾。
P4-D1 到 P4-D13 已完成。

Phase 5 paper-only sandbox execution 已完成阶段收尾。
P5-D1 到 P5-D12 已完成。

Phase 6 policy / risk deny hardening 已完成阶段收尾。
P6-D1 到 P6-D12 已完成。

## 当前关键能力

当前系统已经具备：

- FCFEvent
- EventStore
- ReplayEngine
- main.py 最小事件链
- 多资产 MarketContext 基础层
- raw market input schema
- schema error catalog
- market input pipeline schema integration
- local_market_input_api
- dify_http_adapter
- dify_response_templates
- multi-asset fixture
- multi-asset Dify success smoke
- multi-asset Dify error smoke
- paper order schema
- sandbox execution engine
- sandbox execution EventStore / Replay integration
- paper execution API wrapper
- Dify paper execution local adapter
- paper execution user-facing response templates
- Dify paper execution smoke runner
- Dify paper execution response integration smoke
- paper execution policy gate
- policy gate API integration
- paper_policy_deny user-facing response
- policy deny response smoke coverage
- paper execution risk guardian
- risk guardian API integration
- paper_risk_deny user-facing response
- risk deny response smoke coverage

## 当前 paper execution API 顺序

当前 handle_paper_execution 执行顺序：

1. evaluate_paper_execution_policy
2. evaluate_paper_execution_risk
3. execute_sandbox_order_with_eventstore

PolicyDeny：

- ok=false
- error.type=PolicyDeny
- 不进入 risk guardian
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 不真实下单

RiskDeny：

- ok=false
- error.type=RiskDeny
- 不进入 sandbox execution
- 不生成 sandbox execution event
- 不真实下单

## Phase 6 已完成范围

P6-D1：Policy and risk deny case hardening plan，已完成。
P6-D2：paper execution policy gate module，已完成。
P6-D3：integrate paper execution policy gate into paper execution API，已完成。
P6-D4：paper execution policy deny response templates，已完成。
P6-D5：Dify paper execution response smoke includes policy deny，已完成。
P6-D6：paper execution risk guardian module plan，已完成。
P6-D7：paper execution risk guardian module，已完成。
P6-D8：integrate risk guardian into paper execution API，已完成。
P6-D9：paper execution risk deny response templates，已完成。
P6-D10：Dify paper execution response smoke includes risk deny，已完成。
P6-D11：Phase 6 policy / risk deny acceptance，已完成。
P6-D12：Phase 6 closeout / project state consolidation，已完成。

## 当前关键代码

- fcf/schemas/raw_market_input_schema.py
- fcf/schemas/schema_error_catalog.py
- fcf/pipelines/market_input_pipeline.py
- fcf/api/local_market_input_api.py
- fcf/api/dify_http_adapter.py
- fcf/api/dify_response_templates.py
- fcf/paper/paper_order_schema.py
- fcf/paper/sandbox_execution_engine.py
- fcf/api/paper_execution_api.py
- fcf/api/dify_paper_execution_adapter.py
- fcf/api/paper_execution_response_templates.py
- fcf/policy/paper_execution_policy.py
- fcf/risk/paper_execution_risk_guardian.py

## 当前关键 smoke runner

- scripts/run_dify_http_adapter_smoke.py
- scripts/run_dify_integration_smoke.py
- scripts/run_multi_asset_dify_smoke.py
- scripts/run_multi_asset_error_dify_smoke.py
- scripts/run_dify_paper_execution_smoke.py
- scripts/run_dify_paper_execution_response_smoke.py

## 当前 Dify paper response smoke 覆盖

- fill_to_user_paper_fill_success
- reject_to_user_paper_reject_success
- policy_deny_to_user_paper_policy_deny
- risk_deny_to_user_paper_risk_deny
- bad_order_to_user_paper_execution_error
- real_execution_intent_to_safety_refusal

## 当前验证命令

python main.py

预期输出：

- events_recorded: 8

python scripts/run_dify_http_adapter_smoke.py

预期输出：

- status completed

python scripts/run_dify_integration_smoke.py

预期输出：

- status completed

python scripts/run_multi_asset_dify_smoke.py

预期输出：

- status completed

python scripts/run_multi_asset_error_dify_smoke.py

预期输出：

- status completed

python scripts/run_dify_paper_execution_smoke.py

预期输出：

- status completed

python scripts/run_dify_paper_execution_response_smoke.py

预期输出：

- status completed

python -m pytest -q

预期输出：

- 235 passed

## 安全边界

Dify 不作为底层交易内核。
Dify 不直接接真实交易所 API。
Dify 不保存真实 API key。
Dify 不读取钱包私钥。
Dify 不真实下单。
Dify 只调用受控 API wrapper / pipeline。
Dify 不允许绕过 policy / risk。
Dify 不把 pipeline 成功伪装成真实交易成功。

当前系统不接真实交易所 API。
当前系统不保存真实 API key。
当前系统不读取钱包私钥。
当前系统不真实下单。

paper execution 只是 paper / sandbox。
sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
PolicyDeny 不是交易所真实拒单。
RiskDeny 不是交易所真实拒单。
paper execution 不修改真实账户。
paper execution 不修改真实仓位。

## Phase 7 推荐方向

建议下一步进入：

P7-D1：Multi-asset guarded paper execution fixture plan。

目标：

- 新增 multi-asset guarded paper execution fixture 规划文档
- 覆盖 crypto / equities / fx / commodities
- 明确每个资产类别的 raw_order 样例
- 明确每个资产类别的 risk_context 样例
- 明确 policy deny / risk deny 分支样例
- 不接真实交易所 API
- 不真实下单
- 不破坏现有测试

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 执行 git rev-parse --short HEAD 后填写
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成，D1-D11 已完成。Phase 2 多资产 MarketContext 基础层已完成，P2-D1 到 P2-D10 已完成。Phase 3 数据接入与 Dify integration 已完成阶段收尾，P3-D1 到 P3-D14 已完成。Phase 4 schema hardening 与 multi-asset fixture expansion 已完成阶段收尾，P4-D1 到 P4-D13 已完成。Phase 5 paper-only sandbox execution 已完成阶段收尾，P5-D1 到 P5-D12 已完成。Phase 6 policy / risk deny hardening 已完成阶段收尾，P6-D1 到 P6-D12 已完成。当前不是足球系统，也不是 BTC-only。BTCMarketContext 只是第一个 crypto/BTC 市场样板，不是项目终点。
当前能力：raw market input schema、schema error catalog、market input pipeline schema integration、local_market_input_api、dify_http_adapter、dify_response_templates、multi-asset fixture、multi-asset Dify success smoke、multi-asset Dify error smoke、paper order schema、sandbox execution engine、sandbox execution EventStore / Replay integration、paper execution API wrapper、Dify paper execution local adapter、paper execution user-facing response templates、Dify paper execution smoke runner、Dify paper execution response integration smoke、paper execution policy gate、policy gate API integration、paper_policy_deny user-facing response、policy deny response smoke coverage、paper execution risk guardian、risk guardian API integration、paper_risk_deny user-facing response、risk deny response smoke coverage 均已完成。
当前 paper execution API 顺序：evaluate_paper_execution_policy -> evaluate_paper_execution_risk -> execute_sandbox_order_with_eventstore。PolicyDeny / RiskDeny 都直接返回 ok=false，不进入 sandbox execution，不生成 sandbox execution event，不真实下单。
当前验证：python main.py 输出 events_recorded: 8；python scripts/run_dify_http_adapter_smoke.py 输出 status completed；python scripts/run_dify_integration_smoke.py 输出 status completed；python scripts/run_multi_asset_dify_smoke.py 输出 status completed；python scripts/run_multi_asset_error_dify_smoke.py 输出 status completed；python scripts/run_dify_paper_execution_smoke.py 输出 status completed；python scripts/run_dify_paper_execution_response_smoke.py 输出 status completed；python -m pytest -q 预计显示 235 passed。
安全边界：Dify 不作为底层交易内核，不直接接真实交易所 API，不保存真实 API key，不读取钱包私钥，不真实下单，只调用受控 API wrapper / pipeline，不允许绕过 policy / risk，不把 paper execution 伪装成 real execution。sandbox fill 不是真实成交，sandbox reject 不是交易所真实拒单，PolicyDeny / RiskDeny 都不是交易所真实拒单。
next_action: 进入 P7-D1：Multi-asset guarded paper execution fixture plan。新增 multi-asset guarded paper execution fixture 规划文档，覆盖 crypto / equities / fx / commodities，明确每个资产类别的 raw_order 样例、risk_context 样例、policy deny / risk deny 分支样例。不接真实交易所 API，不真实下单，不破坏测试。
要求：全程中文一步步指挥；命令必须是可直接复制的 Git Bash 格式；多行 cat 必须包含完整 EOF；每次重要更新都 commit 并 push，并更新新的续聊话术。成功后直接给下一步代码，不必等待用户说继续。

