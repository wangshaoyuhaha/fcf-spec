# CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 D1 Contract

## Scope

CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 is a sidecar-only governance schema consistency guard.

It protects project governance records from inconsistent field names, missing required fields, unsafe status values, and unsafe safety boundary flags.

## Protected Governance Records

D1 defines schema contracts for:

- stage records
- final current-state records
- safety boundary records

## Required Stage Record Keys

- app_id
- stage_id
- status
- branch
- commit
- validation
- git_status
- safety_boundary

## Required Final Current-State Keys

- app_id
- latest_main_commit
- main_merge_commit
- final_branch_commit
- validation
- git_status
- origin_main
- tag
- release
- deploy

## Allowed Status Values

- planned
- in_progress
- completed
- merged
- archived
- blocked

## Safety Boundary

Required true flags:

- paper_only
- local_only
- read_only
- sidecar_only
- operator_review_required

Required false flags:

- real_trading_allowed
- broker_api_allowed
- exchange_api_allowed
- api_key_allowed
- buy_button_allowed
- sell_button_allowed
- order_button_allowed
- tag_allowed
- release_allowed
- deploy_allowed

## D1 Deliverables

- scripts/control_center_schema_consistency_guard.py
- tests/test_control_center_schema_consistency_guard.py
- docs/CONTROL_CENTER_SCHEMA_CONSISTENCY_GUARD_APP_1_D1_CONTRACT.md

## Forbidden Scope

- no P48
- no core mutation
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no broker API
- no exchange API
- no API key
- no wallet key
- no real account
- no real position
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy