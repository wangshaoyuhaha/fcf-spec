# AI-PROMPT-MODEL-VERSION-REGISTRY-APP-1 D2

## Purpose

Define deterministic governed records for prompt, model, contract,
and registry versions.

## Record identity

Each record contains:

- registry_entry_id
- registry_entry_hash
- record_kind
- record_status

Identity is generated deterministically from version and trace evidence.

## Version fields

- prompt_version
- model_version
- contract_version
- registry_version
- content_hash

## Trace fields

- correlation_id
- research_run_id
- source_artifact_ids
- validation_baseline_id

Trace fields must be supplied by governed sources.
The registry does not fabricate lineage.

## Integrity

- content_hash must be SHA-256
- registry_entry_hash is SHA-256
- duplicate source artifact identifiers are rejected
- source artifact identifiers are sorted deterministically

## Safety locks

- human review required
- archive required
- no model execution
- no automatic activation
- no automatic promotion
- no automatic rollback
- no credential access
- no real trading
- no real execution
- no deployment instruction
- no buy, sell, order, position sizing, or portfolio action
