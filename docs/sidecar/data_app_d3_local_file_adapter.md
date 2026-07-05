# DATA-APP-D3 Local File Adapter

Status: completed

Purpose:
- Add read-only local file adapter for A-share DATA-APP input.
- Enable CSV and JSON ingestion.
- Reserve Excel input without enabling it in D3.
- Validate rows through DATA-APP A-share schema.

Active inputs:
- CSV
- JSON

Reserved inputs:
- Excel

Outputs:
- source_file
- source_type
- row_count
- accepted_count
- rejected_count
- accepted_rows
- rejected_rows

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
