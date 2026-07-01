# P7-D2 - Multi-asset Guarded Paper Execution Fixture

## 1. 目的

P7-D2 新增 multi-asset guarded paper execution fixture。

该 fixture 覆盖：

- crypto
- equities
- fx
- commodities

每个资产类别覆盖四个分支：

- fill_success
- sandbox_reject
- policy_deny
- risk_deny

## 2. 新增文件

- fixtures/paper_orders_multi_asset_guarded.json
- tests/test_multi_asset_guarded_paper_fixture.py

## 3. 分支定义

fill_success：

- policy gate 通过
- risk guardian 通过
- sandbox execution engine 返回 filled
- 生成 sandbox execution event

sandbox_reject：

- policy gate 通过
- risk guardian 通过
- sandbox execution engine 返回 rejected
- 生成 sandbox execution event
- 该拒单不是交易所真实拒单

policy_deny：

- policy gate 拒绝
- 不进入 risk guardian 后续执行分支
- 不进入 sandbox execution engine
- 不生成 sandbox execution event
- 不是交易所真实拒单

risk_deny：

- policy gate 通过
- risk guardian 拒绝
- 不进入 sandbox execution engine
- 不生成 sandbox execution event
- 不是交易所真实拒单

## 4. 安全边界

P7-D2 不接真实交易所 API。
P7-D2 不保存真实 API key。
P7-D2 不读取钱包私钥。
P7-D2 不真实下单。
P7-D2 不允许绕过 policy / risk。
P7-D2 不把 paper execution 伪装成 real execution。

## 5. 验收标准

P7-D2 完成需要满足：

- fixture 覆盖 crypto / equities / fx / commodities
- 每个资产类别覆盖 fill_success / sandbox_reject / policy_deny / risk_deny
- fixture schema 测试通过
- guarded paper execution 分支测试通过
- policy_deny 不生成 sandbox event
- risk_deny 不生成 sandbox event
- python main.py 输出 events_recorded: 8
- 所有 smoke runner 输出 status completed
- python -m pytest -q 通过

