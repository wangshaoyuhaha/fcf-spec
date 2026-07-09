# CONTROL-CENTER-ENCODING-GUARD-APP-1 D2 Source Registry

## Scope

D2 adds a guarded governance source registry.

## Registry Inputs

Default guarded files:

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md

Additional guarded files:

- FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md
- FCF_CURRENT_STATE_*.md

## Registry Record Fields

- path
- file_kind
- exists
- encoding_status
- write_policy
- safety_scope

## File Kinds

- CONTROL_CENTER
- BACKEND_HANDOFF
- NEW_WINDOW_PROMPT
- FINAL_AUDIT
- FINAL_CURRENT_STATE
- GOVERNANCE_DOCUMENT

## Encoding Status

- OK
- MISSING
- UTF8_DECODE_ERROR

## Write Policy

- UTF8_LF_ONLY

## Safety Scope

- PAPER_ONLY_LOCAL_ONLY_READ_ONLY_SIDECAR_ONLY

## Forbidden Scope

- no core mutation
- no trading mutation
- no score mutation
- no reason code mutation
- no risk flag deletion
- no broker connection
- no exchange connection
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