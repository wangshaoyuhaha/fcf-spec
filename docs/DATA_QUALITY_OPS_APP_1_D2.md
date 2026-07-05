# DATA-QUALITY-OPS-APP-1 D2 Source Loader

Stage:
DATA-QUALITY-OPS-D2

Purpose:
Load local data quality and archive metadata sources as read-only paper-only payloads.

Allowed:
- Load local JSON metadata objects.
- Load local Markdown or text metadata previews.
- Summarize loaded sources by app and source type.
- Preserve load errors as paper-only diagnostics.

Forbidden:
- No source content mutation.
- No source deletion.
- No source overwrite.
- No issue list generation.
- No repair queue generation.
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
DATA-QUALITY-OPS-D3 may generate paper-only data quality checks from loaded sources.
