# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D2 Source Loader

## Scope

D2 adds a read-only completion index source loader.

It loads governance sources needed to build and validate the project completion index.

## Source Types

Supported source types:

- CONTROL_CENTER
- FINAL_CURRENT_STATE
- GOVERNANCE_DOCUMENT

## Default Source Patterns

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_CURRENT_STATE_*.md

## Source Record Fields

Each source record contains:

- path
- source_kind
- exists
- utf8_status
- extracted_fields

## Read Rules

- use UTF-8
- do not mutate source files
- do not delete source files
- do not overwrite source files
- missing files are reported
- UTF-8 decode failures are reported
- key-value extraction is best-effort only

## Blocking Rule

Completion source loading blocks when any required source is missing or not UTF-8 readable.

## D2 Deliverables

- completion source classifier
- completion source discovery
- UTF-8 readability status
- markdown key-value extraction
- source loading
- source summary
- readable-source assertion

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
- no wallet key
- no real account
- no real position
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy