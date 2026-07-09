# CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 D4 Consistency Matrix

## Scope

D4 adds cross-source consistency checks for governance files.

It compares normalized fields across governance sources and blocks conflicting values.

## Checked Source Types

- CONTROL_CENTER
- BACKEND_HANDOFF
- NEW_WINDOW_PROMPT
- FINAL_CURRENT_STATE
- GOVERNANCE_DOCUMENT

## Default Consistency Fields

- app_id
- branch
- validation
- git_status
- origin_main
- tag
- release
- deploy

## Issue Severity

D4 supports:

- PASS
- WARN
- BLOCK

## Warning Rules

A warning is produced when:

- a field is present in some sources but missing in other sources
- a field is not found in any loaded source

## Blocking Rules

A block is produced when:

- the same canonical field has conflicting values across sources

## Purpose

D4 prevents control center, handoff, and final current-state files from silently disagreeing on branch, validation, git status, origin sync, tag, release, or deploy records.

## Forbidden Scope

- no P48
- no core mutation
- no source mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy