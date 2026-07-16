# DIFY-UI-HANDOFF-APP-1 D2 Source Loader

## Purpose

D2 builds a read-only local source manifest for FCF UI, report, workflow, and Dify handoff input artifacts.

## Stage

DIFY-UI-HANDOFF-D2

## Source groups

- runtime/operator_console/index.html
- artifacts/operator_console_static_export
- artifacts/operator_workflow_bundle
- artifacts/paper_readable_report
- artifacts/paper_governance_report
- FCF_CURRENT_STATE_DASHBOARD_STATUS_APP_1_FINAL.md
- FCF_CURRENT_STATE_FINAL_COMPLETION_REVIEW_APP_1_FINAL.md

## D2 behavior

The source loader may inspect local paths, file sizes, checksums, directory file counts, and sample file names.

The source loader must not mutate source files.

Tracked runtime and current-state sources are required. Generated `artifacts/`
sources are optional and are counted separately when unavailable. Validation
fails only when a required source is missing or availability accounting is
inconsistent.

## Required safety boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

## Forbidden scope

- No source mutation
- No source deletion
- No source overwrite
- No Dify API write
- No automated Dify app creation
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
- No operator review bypass
- No tag
- No release
- No deploy

## Next stage

D3 will define the Dify input and output contract.
