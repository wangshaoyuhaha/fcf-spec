# DASHBOARD-CONTRADICTION-SCANNER-APP-1 D3

## Purpose

Define the governed contradiction finding record used by the scanner.

## Finding identity

Each finding contains:

- finding_id
- finding_hash
- contradiction_class
- severity
- status

The identifier is generated deterministically from the evidence record.

## Traceability

Required:

- correlation_id
- research_run_id
- validation_baseline_id
- source_artifact_ids

Trace identifiers must be supplied by governed sources.
The scanner does not fabricate missing lineage.

## Evidence

Every finding requires non-empty structured evidence and a human-readable summary.

## Severity

Allowed values:

- LOW
- MEDIUM
- HIGH
- CRITICAL

## Status

Allowed values:

- OPEN
- ACKNOWLEDGED
- RESOLVED
- ARCHIVED

A finding cannot become automatically resolved.

## Safety locks

Every finding requires:

- human_review_required = true
- archive_required = true
- execution_allowed = false
- source_mutation_allowed = false
- risk_flag_deletion_allowed = false
- risk_flag_downgrade_allowed = false

## Forbidden action fields

- buy
- sell
- order
- execute
- position_size
- portfolio_action
- trade_instruction
