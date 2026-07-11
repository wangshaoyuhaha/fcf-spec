# AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1 D2

## Stage

D2 Registered Source Manifest and Version-Lock Schema

## Status

COMPLETED ON SIDECAR BRANCH

## Purpose

Register and version-lock every upstream artifact before deterministic report
assembly begins.

D2 does not create the comprehensive report.

## Required Source Types

- MARKET_NARRATIVE_CONTEXT
- CAUSAL_REASONING_CHAIN
- CONTRARIAN_CHALLENGE
- SCENARIO_SIMULATION
- AI_EVALUATION_EVIDENCE
- VALIDATION_BASELINE

## Optional Registered Source Types

- PROMPT_MODEL_VERSION_REGISTRY
- ARCHIVE_CORRELATION_ROLLUP
- OPERATOR_REVIEW

## Required Source Record Fields

- artifact_id
- artifact_type
- artifact_version
- correlation_id
- research_run_id
- source_stage_id
- source_path
- locked_sha256
- source_conclusion_state
- validation_state
- requirement_level

## Preservation Fields

Every source record requires:

- source_artifact_preserved = true
- original_conclusion_preserved = true
- operator_review_required = true

## Version-Lock Rules

The manifest locks:

- artifact identifier
- artifact type
- artifact version
- SHA-256 digest
- correlation identifier
- research run identifier

A report synthesis run must not silently replace a locked artifact version.

## Run Isolation Rules

All records in one manifest must use:

- one correlation_id
- one research_run_id

Mixing unrelated research runs is blocked.

## Path Rules

Source paths must be:

- repository-relative
- normalized with POSIX separators
- free from parent traversal
- outside runtime artifact directories

Runtime learning artifacts are not final source truth.

## Deterministic Rules

- source records are sorted by artifact type and artifact identifier
- artifact identifiers must be unique
- required artifact types must be present
- version locks must exactly match source records
- timestamps are not generated
- report synthesis remains not started

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- deterministic-only
- registered artifacts only
- source artifacts preserved
- original conclusions preserved
- operator review required
- no live model invocation
- no prompt execution
- no runtime orchestrator
- no automatic archive execution
- no trade action
- no real execution
- no tag
- no release
- no deploy

## D2 Deliverables

- registered source record schema
- supported source type registry
- required source type registry
- deterministic source manifest builder
- deterministic version-lock builder
- correlation and research-run isolation checks
- duplicate artifact detection
- repository source path validation
- targeted D2 tests

## Next Stage

D3 is not started by this commit.

Expected D3 subject:

Deterministic Comprehensive Report Section Assembly