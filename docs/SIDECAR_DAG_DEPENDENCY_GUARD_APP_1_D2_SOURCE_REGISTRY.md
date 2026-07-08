# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D2 Source Registry

## Purpose

D2 adds a deterministic read-only sidecar registry for dependency graph validation.

The registry defines known sidecar nodes, dependency zones, and allowed dependency direction.

## Dependency Zones

- data_foundation
- research_intelligence
- governance_review
- presentation_handoff
- archive_audit

## Zone Direction

Allowed direction:

data_foundation -> research_intelligence -> governance_review -> presentation_handoff -> archive_audit

Blocked direction:

archive_audit -> presentation_handoff
presentation_handoff -> governance_review
governance_review -> research_intelligence
research_intelligence -> data_foundation

## D2 Scope

D2 provides:

- sidecar node schema
- sidecar node validation
- node index builder
- dependency direction validation
- full graph validation helper

## Safety Boundary

Required:

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required

Forbidden:

- no P48 core expansion
- no P1-P47 core mutation
- no core bypass
- no source mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no real execution
- no broker API
- no exchange API
- no API key
- no wallet private key
- no real account
- no real position
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## D2 Output

D2 adds deterministic sidecar registry helpers and tests.
