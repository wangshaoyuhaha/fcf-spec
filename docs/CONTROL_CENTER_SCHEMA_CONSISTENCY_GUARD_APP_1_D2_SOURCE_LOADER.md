# CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 D2 Source Loader

## Scope

D2 adds a read-only governance source loader.

It loads governance markdown files and extracts simple key-value fields for schema consistency checks.

## Source Types

Supported source types:

- CONTROL_CENTER
- BACKEND_HANDOFF
- NEW_WINDOW_PROMPT
- FINAL_CURRENT_STATE
- GOVERNANCE_DOCUMENT

## Default Source Patterns

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md
- FCF_CURRENT_STATE_*.md

## Loader Fields

Each source record contains:

- path
- source_kind
- exists
- utf8_status
- extracted_fields

## Read Rules

- use UTF-8
- do not modify source files
- missing files are reported
- decode failures are reported
- key-value extraction is best-effort only

## Blocking Rule

Governance source loading blocks when a required source is missing or not UTF-8 readable.

## Forbidden Scope

- no P48
- no core mutation
- no source mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
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