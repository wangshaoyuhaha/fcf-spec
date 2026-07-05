# DATA-QUALITY-OPS-APP-1 D1 Ops Contract

Stage:
DATA-QUALITY-OPS-D1

Purpose:
Define a paper-only, local-only, read-only, sidecar-only data quality operations contract.

Allowed source apps:
- DATA-APP-1
- REPORT-ARCHIVE-APP-1
- OPERATOR-REVIEW-APP-1

Allowed source types:
- data_quality_summary
- health_check_report
- quarantine_report
- archive_manifest
- paper_archive_packet
- operator_review_handoff

Allowed outputs:
- data_quality_ops_check
- data_quality_issue_list
- data_repair_queue
- data_quality_ops_handoff

Forbidden:
- No source content mutation.
- No source deletion.
- No source overwrite.
- No repair queue execution instruction.
- No trade instruction.
- No real execution.
- No buy button.
- No sell button.
- No order button.
- No broker connection.
- No exchange connection.
- No credential storage.
- No wallet private key access.
- No real account access.
- No real position access.
- No P1-P47 core mutation.
- No P48 core expansion.
- No tag.
- No release.
- No deploy.

Next:
DATA-QUALITY-OPS-D2 may load local data quality and archive metadata sources without mutating them.
