# DATA-QUALITY-OPS-APP-1 D4 Issue List

Stage:
DATA-QUALITY-OPS-D4

Purpose:
Convert D3 paper-only data quality checks into a paper-only issue list.

Allowed:
- Convert REVIEW_REQUIRED checks into open paper-review issues.
- Convert FAIL checks into error-level paper-review issues.
- Summarize issues by severity, status, and issue code.

Forbidden:
- No source content mutation.
- No source deletion.
- No source overwrite.
- No repair queue generation in this stage.
- No trade action.
- No real execution.
- No broker or exchange connection.
- No credential, wallet, account, or position access.
- No P1-P47 core mutation.
- No P48 core expansion.
- No tag.
- No release.
- No deploy.

Next:
DATA-QUALITY-OPS-D5 may generate a paper-only repair queue and local ops packet.
