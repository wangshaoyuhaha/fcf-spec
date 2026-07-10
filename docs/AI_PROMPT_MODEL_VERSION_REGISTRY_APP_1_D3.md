# AI-PROMPT-MODEL-VERSION-REGISTRY-APP-1 D3

## Purpose

Build a deterministic read-only index for governed prompt, model,
contract, and registry version records.

## Index contents

- registry_index_id
- registry_index_hash
- record_count
- registry_entry_ids
- version_keys
- kind_summary
- status_summary
- immutable record snapshots

## Version uniqueness

Each governed version key must be unique:

- PROMPT uses prompt_version
- MODEL uses model_version
- CONTRACT uses contract_version
- REGISTRY uses registry_version

Duplicate registry entry identifiers and duplicate version keys are rejected.

## Query support

The index supports read-only lookup by:

- registry_entry_id
- record_kind

Returned records are copies and cannot mutate the registry index.

## Integrity

The index identifier and hash are generated deterministically from:

- registry entry identifiers
- registry entry hashes
- version keys
- kind summary
- status summary

## Safety locks

- human review required
- archive required
- no model execution
- no automatic activation
- no automatic promotion
- no automatic rollback
- no source mutation
- no real trading
- no real execution
- no deployment or trading action
