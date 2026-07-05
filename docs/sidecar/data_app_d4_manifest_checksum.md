# DATA-APP-D4 Manifest And Checksum

Status: completed

Purpose:
- Add read-only manifest builder for DATA-APP local files.
- Add sha256 checksum for source traceability.
- Build file-level and batch-level manifest contracts.
- Validate manifest safety boundary.

Outputs:
- manifest_id
- market
- source_file
- source_type
- schema_version
- checksum_sha256
- row_count
- accepted_count
- rejected_count
- adapter_ok
- created_at_utc

Batch outputs:
- source_count
- aggregate checksum
- sources
- all_sources_ok

Safety:
- paper-only
- local-only
- read-only
- no real exchange API
- no real brokerage API
- no API key
- no real order
- no real execution
- no real money impact
- operator review required
