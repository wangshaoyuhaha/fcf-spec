# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D3 NameError Fix

## Purpose

This patch fixes a missing module constant used by dependency direction validation.

## Fixed Issue

validate_dependency_direction referenced EXPLICIT_ALLOWED_DEPENDENCY_EDGES before the constant existed in the module.

## Fix

Define EXPLICIT_ALLOWED_DEPENDENCY_EDGES as a module-level frozenset.

Allowed explicit read-only handoff edges:

- UI-APP-1 -> OPERATOR-REVIEW-APP-1
- OPERATOR-REVIEW-APP-1 -> REPORT-ARCHIVE-APP-1

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no source mutation
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no real execution
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy
