# AI-COMPREHENSIVE-REPORT-INTEGRATION-APP-1 D2

## State

APPROVED / ACTIVE / D2

## Purpose

Add the first actual external Python consumer for the completed
AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1 package.

D2 loads only registered local source envelopes and validates exact
source identity, artifact reference, version, correlation ID, and
payload SHA-256 locks.

## External source import

The integration sidecar imports:

apps.ai_comprehensive_report_synthesis_app_1

This establishes an explicit downstream Python dependency from the
integration application to the completed synthesis application.

The dependency remains one-way.

The synthesis application must not import this integration application.

## Required envelope fields

- source_app_id
- source_module
- source_artifact_type
- source_artifact_ref
- source_artifact_version
- source_sha256
- correlation_id
- source_payload
- operator_review_required

## Exact locks

D2 supports exact validation of:

- source artifact reference
- source artifact version
- correlation ID
- canonical source payload SHA-256

A lock mismatch rejects loading.

## Canonical hashing

The payload hash uses deterministic JSON serialization:

- sorted keys
- compact separators
- ASCII-safe encoding
- no NaN values
- UTF-8 bytes
- SHA-256 digest

## Read-only rules

- input mappings are deep-copied
- input mappings are not mutated
- source files are read only
- only local JSON files are allowed
- network source references are rejected
- source payload repair is forbidden
- missing source metadata is not invented
- version mismatches are not corrected
- hash mismatches are not corrected

## Safety boundary

- P1-P47 core frozen
- no P48
- no core mutation
- paper-only
- local-only
- read-only
- sidecar-only
- registered artifacts only
- deterministic only
- operator review required
- no automatic approval
- no automatic archive execution
- no runtime model invocation
- no prompt execution
- no automatic routing
- no real execution
- no tag
- no release
- no deploy

## D2 deliverables

- external source package import
- registered source envelope builder
- deterministic canonical SHA-256 function
- registered source envelope validator
- mapping source loader
- local JSON source loader
- exact version-lock validation
- exact artifact-reference lock validation
- exact correlation-ID lock validation
- exact SHA-256 lock validation
- D2 tests

## Next stage

D3 may add a deterministic read-only operator-review adapter after D2
validation, commit, push, and clean status.
