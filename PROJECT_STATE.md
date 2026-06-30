# FCF Project State

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main

## 当前项目定位

FCF Spec 当前定位为：

全金融市场 / 多资产交易系统的事件驱动最小骨架。

不是足球系统。

也不是只做 BTC。

BTCMarketContext 是 Phase 2 的第一个 crypto/BTC 市场样板实现，不是项目终点。

Phase 2 多资产市场上下文基础层已完成阶段验收。

Phase 3 已启动，当前重点是数据接入边界、mock 数据接入、可回放输入、本地外部调用边界、Dify workflow 接入规划和本地 API wrapper。

## 当前阶段

Phase 1 Build Spine 已完成稳定收尾。

Phase 2 多资产 MarketContext 基础层已完成阶段验收。

Phase 3 已启动。

当前完成到：

P3-D6：本地 API wrapper，已完成。

## 已完成进度

D1-D11: Phase 1 Build Spine 已完成。

P2-D1 到 P2-D10: Phase 2 多资产市场上下文基础层，已完成阶段验收。

P3-D1: 真实数据接入边界规划，已完成。

P3-D2: mock market data adapter，已完成。

P3-D3: replayable raw market fixture，已完成。

P3-D4: 本地 system input pipeline / 外部调用边界，已完成。

P3-D5: Dify workflow 接入规划，已完成。

P3-D6: 本地 API wrapper，已完成。

## 当前验证结果

python main.py:

- events_recorded: 8

python -m pytest -q:

- 58 passed

## 当前关键提交

- 6b616f4 add P3 Dify workflow integration plan
- a2ebac6 update state after P3 Dify workflow plan
- 77ff341 add P3 local market input api wrapper

## P3-D6 完成内容

新增文件：

- fcf/api/__init__.py
- fcf/api/local_market_input_api.py
- tests/test_local_market_input_api.py

完成能力：

- 新增本地 API wrapper
- 包装 process_raw_market_input
- 包装 process_raw_market_batch
- 提供 handle_single_market_input
- 提供 handle_batch_market_input
- 提供 describe_api_contract
- 返回稳定 response dict
- 成功返回 ok true / data
- 失败返回 ok false / error
- 为 Dify HTTP/API 节点做准备
- 不直接接 Dify
- 不接真实交易所 API
- 不保存密钥
- 不真实下单
- 不修改 main.py
- 不破坏当前测试

## 下一步任务

进入 P3-D7：Dify API contract / example payload 文档。

P3-D7 目标：

- 新增 Dify API 契约文档
- 明确 Dify 调用 local_market_input_api 的输入 JSON
- 明确 Dify 收到的输出 JSON
- 明确错误响应格式
- 明确 workflow 节点怎么传字段
- 明确不能真实下单
- 明确不能接真实交易所 API key
- 保持 python main.py 输出 events_recorded: 8
- 保持 python -m pytest -q 通过

建议新增：

- docs/17_dify_api_contract_examples.md

## 新聊天启动信息

如果当前聊天变慢或达到上限，把下面这段复制到新聊天：

repo: https://github.com/wangshaoyuhaha/fcf-spec.git
branch: main
last_commit: 77ff341
current_stage: 全金融市场 / 多资产交易事件系统。Phase 1 Build Spine 已完成稳定收尾，D1-D11 已完成。Phase 2 多资产市场上下文基础层已完成阶段验收，P2-D1 到 P2-D10 已完成。Phase 3 已启动，P3-D1 到 P3-D6 已完成。P3-D6 新增本地 API wrapper：fcf/api/local_market_input_api.py，可包装 process_raw_market_input 和 process_raw_market_batch，返回稳定 response dict，为后续 Dify HTTP/API 节点做准备。当前主事件链仍为 8 个事件，python main.py 输出 events_recorded: 8，python -m pytest -q 预计显示 58 passed。Dify 不作为底层交易内核，不直接接交易所 API，不真实下单，只调用受控 API wrapper / pipeline。
next_action: 先更新 README.md 和 PROJECT_STATE.md，把 P3-D6 标记为已完成并提交。然后进入 P3-D7：Dify API contract / example payload 文档，新增 docs/17_dify_api_contract_examples.md。
要求：全程用中文一步步指挥我操作；命令必须给可直接复制的 Git Bash 格式；多行 cat 写文件必须包含完整 EOF；每次重要更新都提交并 push 到 GitHub，并更新新的续聊话术。

## P3-D7 完成记录

P3-D7：Dify API contract / example payload 文档已完成。

新增文件：

- docs/17_dify_api_contract_examples.md

完成内容：

- 明确 Dify single input JSON
- 明确 Dify batch input JSON
- 明确 FCF 成功输出 JSON
- 明确 FCF 错误响应 JSON
- 明确 workflow 节点字段传递方式
- 明确安全边界

安全边界保持不变：

- Dify 不作为底层交易内核
- Dify 不直接接真实交易所 API
- Dify 不保存真实 API key
- Dify 不真实下单
- Dify 只调用受控 API wrapper / pipeline

下一步：

进入 P3-D8：Dify workflow HTTP/API node mapping 文档。
建议继续先做文档，不接真实交易所，不真实下单，不破坏现有测试。


## P3-D8 完成记录

P3-D8：Dify workflow HTTP/API node mapping 文档已完成。

新增文件：

- docs/18_dify_workflow_http_api_node_mapping.md

完成内容：

- 明确 Dify workflow 推荐节点顺序
- 明确 Start Node
- 明确 User Intent Node
- 明确 Market Input Parser Node
- 明确 Required Field Check Node
- 明确 Market Type Normalization Node
- 明确 Build FCF Request Node
- 明确 FCF API Call Node
- 明确 IF Response OK Node
- 明确 Success Summary Node
- 明确 Error Summary Node
- 明确字段映射
- 明确多资产扩展方向

安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不绕过 FCF policy / risk / EventStore / ReplayEngine

下一步：

进入 P3-D9：Dify local HTTP adapter 规划或最小 FastAPI wrapper。
建议先做规划文档，再决定是否实现本地 HTTP adapter。
任何实现都只能调用受控 local_market_input_api，不接真实交易所，不真实下单。


## P3-D9 完成记录

P3-D9：Dify local HTTP adapter 最小路由层已完成。

新增文件：

- docs/19_dify_local_http_adapter.md
- fcf/api/dify_http_adapter.py
- tests/test_dify_http_adapter.py

完成内容：

- 新增 route_dify_http_request
- 新增 describe_routes
- 支持 GET /api/v1/contract
- 支持 POST /api/v1/market-input/single
- 支持 POST /api/v1/market-input/batch
- 支持 404 unknown route
- 支持 405 method not allowed
- 支持 400 bad request
- 支持 wrapper validation error 映射为 422
- 保持只调用受控 local_market_input_api wrapper

安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不引入外部 Web 框架依赖
- 不绕过 FCF policy / risk / EventStore / ReplayEngine

下一步：

进入 P3-D10：Dify local HTTP adapter examples / CLI smoke runner。
建议新增一个 scripts 或 examples 层，用本地样例请求调用 route_dify_http_request，输出稳定 response dict。
仍然不接真实交易所 API，不真实下单。


## P3-D10 完成记录

P3-D10：Dify local HTTP adapter smoke runner 已完成。

新增文件：

- docs/20_dify_http_adapter_smoke_runner.md
- scripts/__init__.py
- scripts/run_dify_http_adapter_smoke.py
- tests/test_dify_http_adapter_smoke_runner.py

完成内容：

- 新增 run_smoke
- 新增本地 contract 调用样例
- 新增本地 single success 调用样例
- 新增本地 batch success 调用样例
- 新增本地 bad input 调用样例
- 新增本地 unknown route 调用样例
- 输出稳定 JSON summary
- 增加 pytest 覆盖

安全边界：

- 不启动真实 HTTP server
- 不接真实 Dify
- 不接真实交易所 API
- 不保存真实 API key
- 不真实下单
- 只调用受控 local HTTP adapter / API wrapper

下一步：

进入 P3-D11：Dify workflow user-facing response templates。
建议新增文档和测试，固化 success / error / safety refusal 的用户可见输出模板。


## P3-D11 完成记录

P3-D11：Dify workflow user-facing response templates 已完成。

新增文件：

- docs/21_dify_user_facing_response_templates.md
- fcf/api/dify_response_templates.py
- tests/test_dify_response_templates.py

完成内容：

- 新增 render_success_response
- 新增 render_error_response
- 新增 render_safety_refusal
- 新增 render_dify_user_response
- 固化 success 用户可见模板
- 固化 error 用户可见模板
- 固化 safety refusal 用户可见模板
- 增加 pytest 覆盖

安全边界：

- 不接真实交易所 API
- 不保存真实 API key
- 不读取钱包私钥
- 不真实下单
- 不把 pipeline 成功伪装成真实交易成功

下一步：

进入 P3-D12：Dify adapter + response templates integration smoke。
建议把 P3-D10 smoke runner 的结果接入 P3-D11 response templates，形成一条本地端到端样例链路。

