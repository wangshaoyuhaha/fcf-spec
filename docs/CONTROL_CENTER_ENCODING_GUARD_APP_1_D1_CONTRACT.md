# CONTROL-CENTER-ENCODING-GUARD-APP-1 D1 Contract

## Scope

CONTROL-CENTER-ENCODING-GUARD-APP-1 is a sidecar-only guard for project governance documents.

It protects governance handoff files from unreadable text encoding states.

## Guarded Files

Default guarded files:

- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md

Future final current-state files may be added to this guard without changing core logic.

## D1 Rules

- All guarded files must be readable with strict UTF-8.
- Missing guarded files must be reported as MISSING.
- Invalid UTF-8 must be reported as UTF8_DECODE_ERROR.
- File writes performed by this guard must use UTF-8 and LF newlines.
- This guard does not edit core logic.
- This guard does not create trading behavior.
- This guard does not call broker, exchange, wallet, or order APIs.

## Safety Boundary

- paper-only
- local-only
- read-only governance validation
- sidecar-only
- no P48
- no core mutation
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

## D1 Deliverables

- scripts/control_center_encoding_guard.py
- tests/test_control_center_encoding_guard.py
- docs/CONTROL_CENTER_ENCODING_GUARD_APP_1_D1_CONTRACT.md
