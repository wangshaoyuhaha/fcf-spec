# DASHBOARD-CONTRADICTION-SCANNER-APP-1 D4

## Purpose

Implement deterministic contradiction scanning between dashboard packets and governed source artifacts.

## Comparison key

Sources are compared only when both fields match:

- correlation_id
- research_run_id

The scanner does not fabricate missing identifiers.

## Detected contradictions

- missing governed risk flags
- downgraded risk severity
- dashboard summary versus raw-state conflict
- validation state mismatch
- review state mismatch
- lifecycle state mismatch
- archive state mismatch
- validation baseline mismatch
- source lineage mismatch

## Output

The scanner produces:

- scan_report_id
- scan_report_hash
- scan_status
- source manifest reference
- contradiction findings
- finding count

## Safety locks

- human review is always required
- archive preservation is always required
- execution is always forbidden
- source mutation is always forbidden
- risk flag deletion is always forbidden
- risk flag downgrade is always forbidden
- no contradiction is automatically resolved
