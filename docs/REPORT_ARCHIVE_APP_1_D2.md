# REPORT-ARCHIVE-APP-1 D2 Source Discovery

Stage:
REPORT-ARCHIVE-D2

Purpose:
Discover local source artifact candidates from completed sidecar layers.

Allowed:
- Discover local .json, .md, and .txt artifact candidates.
- Infer source app id from path or filename.
- Infer source type from path or filename.
- Return read-only candidate metadata.
- Summarize candidates by source app and source type.

Forbidden:
- No source file content reading.
- No source content mutation.
- No source deletion.
- No source overwrite.
- No archive packet generation.
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
REPORT-ARCHIVE-D3 may build archive item index records from discovered candidates.
