# P7-D3 - Multi-asset Guarded Paper Execution Smoke Runner

## 1. 目的

P7-D3 新增 multi-asset guarded paper execution smoke runner。

该 runner 读取：

- fixtures/paper_orders_multi_asset_guarded.json

并逐条调用：

- handle_paper_execution

用于验证 P7-D2 fixture 覆盖的 guarded paper execution 分支能稳定跑通。

## 2. 覆盖范围

P7-D3 smoke runner 覆盖资产类别：

- crypto
- equities
- fx
- commodities

覆盖分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

## 3. 预期输出

runner 输出 JSON，包含：

- status
- runner
- fixture_path
- case_count
- passed_count
- failed_count
- asset_class_counts
- branch_counts
- cases
- safe_boundary

当所有 case 都符合 expected 时：

status = completed

## 4. 安全边界

P7-D3 不接真实交易所 API。
P7-D3 不保存真实 API key。
P7-D3 不读取钱包私钥。
P7-D3 不真实下单。
P7-D3 不允许绕过 policy / risk。
P7-D3 不把 paper execution 伪装成 real execution。

sandbox fill 不是真实成交。
sandbox reject 不是交易所真实拒单。
policy deny 不是交易所真实拒单。
risk deny 不是交易所真实拒单。

## 5. 验收标准

P7-D3 完成需要满足：

- 新增 scripts/run_multi_asset_guarded_paper_execution_smoke.py
- 新增 tests/test_multi_asset_guarded_paper_execution_smoke_runner.py
- runner 输出 status completed
- runner 覆盖 16 个 fixture case
- runner 覆盖 4 个资产类别
- runner 覆盖 4 个分支
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 输出 status completed
- python -m pytest -q 通过

