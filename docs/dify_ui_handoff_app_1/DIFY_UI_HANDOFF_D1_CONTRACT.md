# DIFY-UI-HANDOFF-APP-1 D1 Contract

## Purpose

DIFY-UI-HANDOFF-APP-1 defines the paper-only local handoff boundary for connecting existing FCF artifacts to a manually configured local Dify/Ollama workflow.

This stage does not create a real trading system. It does not connect to brokers, exchanges, wallets, accounts, or live execution systems.

## Stage

DIFY-UI-HANDOFF-D1

## Allowed scope

- Read local FCF reports
- Read local UI manifests
- Read local operator workflow artifacts
- Prepare Dify input and output contracts
- Prepare local prompt templates
- Prepare manual Dify configuration guidance
- Preserve risk flags
- Preserve reason codes
- Preserve operator review requirement

## Forbidden scope

- No real trading
- No real execution
- No buy button
- No sell button
- No order button
- No broker connection
- No exchange connection
- No API key storage
- No wallet private key access
- No real account access
- No real position access
- No automatic position sizing
- No automatic portfolio action
- No workflow auto approval
- No operator review bypass
- No future return prediction
- No guaranteed performance claim
- No risk flag downgrade
- No reason code deletion
- No P48 core expansion
- No P1-P47 core mutation
- No tag
- No release
- No deploy

## Local user environment assumption

The operator already has local Dify, Ollama, and Docker available. This contract only defines safe local handoff rules. It does not automate Dify app creation and does not require secrets.

## Upstream local sources

- runtime/operator_console/index.html
- artifacts/operator_console_static_export
- artifacts/operator_workflow_bundle
- artifacts/paper_readable_report
- artifacts/paper_governance_report
- FCF_CURRENT_STATE_DASHBOARD_STATUS_APP_1_FINAL.md
- FCF_CURRENT_STATE_FINAL_COMPLETION_REVIEW_APP_1_FINAL.md

## Planned next stages

- D2 source loader and local artifact index
- D3 Dify input and output contract
- D4 Dify prompt template and safety prompt
- D5 manual Dify workflow configuration guide
- D6 refreshed local UI entry handoff and closeout
