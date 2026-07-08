# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D4 Syntax Repair

## Purpose

This repair restores a valid Python module after a malformed scanner patch.

## Fixed Issue

The previous D4 repair introduced invalid Python quoting.

## Repair

The sidecar module was rewritten cleanly with:

- D1 dependency edge guard
- D2 sidecar registry
- D3 explicit read-only handoff edges
- D4 import boundary scanner
- false-positive-safe scanner activation rules

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
