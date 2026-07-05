# OPERATOR-REVIEW-APP-1 D2 Loader

Stage: OPERATOR-REVIEW-D2

Purpose:
Load UI-APP-1 local read-only report artifact or workflow handoff as a paper-only source payload.

Allowed source types:
- ui_app_local_report_artifact
- ui_app_workflow_handoff

Safety:
- Read-only loader.
- No trade action.
- No execution.
- No broker or exchange connection.
- No account, position, credential, or wallet access.
- No mutation of P1-P47 core modules.

D2 output:
- UiAppSourcePayload.
- load_ui_app_source_payload.
- summarize_ui_app_source_payload.

Next:
OPERATOR-REVIEW-D3 may convert a loaded UI source summary into a paper review record schema.
