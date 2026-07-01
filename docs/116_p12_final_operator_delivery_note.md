# P12-D7 - Final Operator Delivery Note

P12-D7 新增 final operator delivery note。

新增文件：

- docs/116_p12_final_operator_delivery_note.md
- docs/117_p12_acceptance_smoke.md
- scripts/run_p12_acceptance_smoke.py
- tests/test_p12_acceptance_smoke.py

## 1. Operator 接手定位

该交付包是 FCF paper-only / non-production delivery package。

operator 可以做：

- 运行本地回归命令
- 运行 Dify-safe paper review
- 读取 operator review response
- 读取 safe_boundary
- 读取 release readiness package summary
- 读取 archive readiness checklist
- 进入人工复核

operator 不可以做：

- 真实交易
- 实盘下单
- 真实账户读取
- 真实仓位读取
- 钱包私钥读取
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

## 2. 最终运行命令

operator 最终命令：

- python main.py
- python scripts/run_p11_release_readiness_package_summary.py
- python scripts/run_p12_acceptance_smoke.py
- python -m pytest -q

通过标准：

- events_recorded: 8
- status completed
- ready_for_p11_d10_bridge_plan true
- ready_for_p12_d8_closeout true
- pytest 全部 passed

## 3. Operator review 入口

Dify-safe API wrapper：

- handle_dify_global_regression_request

Operator response template：

- render_operator_review_response

Regression stability gate：

- evaluate_regression_stability_gate

Phase 12 acceptance smoke：

- python scripts/run_p12_acceptance_smoke.py

## 4. Final delivery checklist

operator 接手前必须确认：

- docs/111_p12_final_non_production_delivery_package.md exists
- docs/112_p12_archive_readiness_checklist.md exists
- docs/113_p12_final_command_index.md exists
- docs/114_p12_final_artifact_manifest.md exists
- docs/115_p12_final_safety_boundary_declaration.md exists
- docs/116_p12_final_operator_delivery_note.md exists
- docs/117_p12_acceptance_smoke.md exists
- python scripts/run_p12_acceptance_smoke.py status completed
- ready_for_p12_d8_closeout true
- python -m pytest -q 全部 passed

## 5. Failed stop rules

如果任何命令 failed：

- 立即停止
- 不进入下一阶段
- 不进入归档状态
- 不解释为交易信号
- 不连接真实交易所
- 不配置 API key
- 不读取钱包私钥
- 不尝试真实下单
- 不删除测试绕过失败
- 不修改 safe_boundary 绕过失败
- 不绕过人工复核
- 不绕过 policy / risk / safe_boundary
- 保留完整错误输出
- 回到 docs/94_p10_failure_triage_guide.md

## 6. Final operator safety boundary

operator 必须确认：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不读取真实账户余额
- 不读取真实仓位
- 不声明真实成交
- 不声明真实资金影响
- 不配置 CI secret
- 不做 production deployment
- 不自动实盘交易
- 不自动绕过人工复核
- 不绕过 policy / risk / safe_boundary
- 不把 paper-only passed 解释成真实交易信号
- 不把 paper-only passed 解释成真实成交

## 7. Final handoff statement

最终交接声明：

FCF 当前交付包可以交给 operator 做 paper-only / non-production 运行、复核和归档准备。

operator 必须通过人工复核读取结果。
operator 不能把任何 passed 结果解释为真实交易信号。
operator 不能把任何 passed 结果解释为真实成交。
operator 不能连接真实交易所。
operator 不能配置真实 API key。
operator 不能读取钱包私钥。
operator 不能真实下单。
operator 不能绕过 policy / risk / safe_boundary。

下一步：

P12-D8：Phase 12 closeout。
