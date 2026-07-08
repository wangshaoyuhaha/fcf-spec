# CORRELATION-ID-TRACEABILITY-APP-1 D2 Source Map

## Purpose

This document defines the read-only source map for Correlation_ID traceability.

## Source Chain

Correlation_ID must connect the following local paper-only stages:

1. Data stage
2. Validation stage
3. Operator review stage
4. UI report stage
5. Archive stage
6. Dify handoff stage

## Source Stage Fields

Each source stage should expose or reference:

- correlation_id
- source_stage
- source_artifact_id
- source_artifact_path
- source_artifact_checksum
- source_artifact_created_at_utc
- upstream_correlation_id
- downstream_correlation_id
- operator_review_required

## Stage Rules

Data stage:
- identifies the local data snapshot or source manifest
- must not mutate source data

Validation stage:
- references validation state and validation artifact
- must not downgrade validation failures

Operator review stage:
- references paper-only review state
- must not bypass operator review

UI report stage:
- references read-only UI report or view model
- must not hide risk flags or reason codes

Archive stage:
- references archive manifest or archive item index
- must not overwrite or delete archived content

Dify handoff stage:
- references local handoff packet only
- must not deploy, create, or update a Dify app

## Forbidden Use

Correlation_ID source map must not become:
- a trade instruction
- an order ticket
- an execution trigger
- a broker or exchange connector
- a credential lookup key
- a score mutation key
- a risk flag downgrade key
- an operator review bypass key

## Output

D2 output is a source map contract only.
It is paper-only, local-only, read-only, and sidecar-only.
