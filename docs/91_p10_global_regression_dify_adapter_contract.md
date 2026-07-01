# P10-D2 - Global Regression Dify Adapter Contract

P10-D2 新增 Dify-safe global regression adapter contract。

新增文件：

- docs/91_p10_global_regression_dify_adapter_contract.md
- fcf/api/dify_global_regression_api.py
- tests/test_p10_global_regression_dify_adapter_contract.py

新增入口：

- handle_dify_global_regression_request

## 输入 contract

输入 request dict：

- request_id
- operator_id
- review_mode
- requested_checks
- output_format

允许 review_mode：

- paper_only
- operator_review
- non_production_review

允许 output_format：

- json

允许 requested_checks：

- all_smokes
- global_report
- safe_boundary
- project_state_consistency

## 输出 contract

输出稳定 response dict：

- ok
- api
- api_version
- error
- data

data 内包含：

- request_id
- operator_id
- review_mode
- requested_checks
- output_format
- run_all_smokes
- global_regression_report
- global_safe_boundary_check
- project_state_consistency_check
- operator_review_required
- ready_for_operator_review
- safe_boundary

## 安全边界

该 adapter 只允许调用现有 paper-only regression runner。

该 adapter 不允许：

- 真实交易所 API
- 真实下单
- 真实 API key 保存
- 钱包私钥读取
- 真实账户余额读取
- 真实仓位读取
- 实盘收益声明
- 实盘成交声明
- 交易所真实拒单声明
- 真实资金影响声明
- CI secret 配置
- production deployment
- 自动实盘交易
- 自动绕过人工复核
- 绕过 policy / risk / safe_boundary

下一步：

P10-D3：operator review response templates。
