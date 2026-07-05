# DATA-QUALITY-OPS-APP-1 D3 Quality Checks

Stage:
DATA-QUALITY-OPS-D3

Purpose:
Generate paper-only data quality operation checks from loaded local metadata sources.

Allowed:
- Build PASS / REVIEW_REQUIRED / FAIL checks.
- Preserve findings as paper-only diagnostics.
- Summarize checks by status, severity, and finding code.

Forbidden:
- No source content mutation.
- No source deletion.
- No source overwrite.
- No issue list generation in this stage.
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
DATA-QUALITY-OPS-D4 may convert checks into a paper-only issue list.
