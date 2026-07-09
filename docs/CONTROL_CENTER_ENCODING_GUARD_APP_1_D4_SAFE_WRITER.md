# CONTROL-CENTER-ENCODING-GUARD-APP-1 D4 Safe Writer

## Scope

D4 adds a byte-safe UTF-8 LF writer for guarded governance files.

The writer is designed to avoid decode failures and partial writes when updating:

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md
- FCF_CURRENT_STATE_*.md
- FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md

## D4 Functions

D4 adds:

- normalize_lf
- atomic_write_utf8_lf
- append_section_utf8_lf
- create_backup_copy
- assert_safe_write_result_ok

## Write Rules

All safe writes must:

- normalize CRLF and CR to LF
- encode with UTF-8
- write through a temporary file
- replace the target atomically
- optionally create a .bak copy
- re-probe the final file after write

## Idempotent Append Rule

append_section_utf8_lf must not duplicate an existing section marker.

If the section already exists, it returns without rewriting the file.

## Sidecar Boundary

D4 only provides safe file writing utilities for governance documents.

It must not mutate core logic or trading behavior.

## Forbidden Scope

- no core mutation
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
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