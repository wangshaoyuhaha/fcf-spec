# MARKET-NARRATIVE-CONTEXT-APP-1 D2

## Purpose

Define registered narrative source metadata and deterministic source
trust levels.

## Source trust levels

- LEVEL_0_LOCAL_DETERMINISTIC
- LEVEL_1_PROJECT_ARCHIVED
- LEVEL_2_OPERATOR_PROVIDED
- LEVEL_3_EXTERNAL_REGISTERED

Trust level is provenance metadata only.

Trust level does not establish truth.
Trust level does not replace evidence review.
Trust level does not authorize automatic conclusions.

## Required source metadata

- artifact_id
- artifact_type
- source_trust_level
- content_sha256
- registered_at_utc
- correlation_id
- research_run_id
- evidence_reference_ids
- local_snapshot_present
- operator_review_required
- original_content_preserved

## External material rule

Externally originated material must already be registered as a local
snapshot and must contain at least one evidence reference.

The sidecar does not fetch external data.
The sidecar does not invoke a live model.
The sidecar does not execute prompts.

## Deterministic validation

The schema validates:

- registered artifact type
- stable identifiers
- SHA-256 content hash
- UTC registration timestamp
- evidence reference identifiers
- duplicate evidence references
- local snapshot presence
- operator review requirement
- original content preservation
- live fetch prohibition
- automatic truth-decision prohibition

## Permanent boundary

- P1-P47 core frozen
- no P48
- no core mutation
- paper-only
- local-only
- read-only
- sidecar-only
- deterministic-only
- registered artifacts only
- operator review required
- original conclusions preserved
- no live model invocation
- no prompt execution
- no AI orchestrator execution
- no automatic truth decision
- no automatic winner selection
- no automatic conclusion replacement
- no automatic model or prompt switching
- no operator review bypass
- no trade action
- no real execution
- no broker or exchange connection
- no API keys
- no wallet keys
- no tag
- no release
- no deploy

## D2 status

The registered source schema, trust-level model, validation rules, and
tests are implemented.
