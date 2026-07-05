# REPORT-ARCHIVE-APP-1 D4 Integrity Summary

Stage:
REPORT-ARCHIVE-D4

Purpose:
Generate read-only checksum records and archive integrity summary from D3 item index records.

Allowed:
- Read local file bytes only to calculate SHA-256 checksums.
- Build integrity records.
- Build integrity summary.
- Summarize ready, missing, and unreadable source status.

Forbidden:
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
REPORT-ARCHIVE-D5 may generate a paper-only archive manifest and local archive packet.
