# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D1 Contract

## Purpose

SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 establishes a read-only dependency guard for sidecar applications.

The guard verifies that sidecar dependencies form a directed acyclic graph.

## D1 Scope

D1 defines:

- sidecar dependency node
- sidecar dependency edge
- allowed dependency direction
- blocked core mutation boundary
- cycle detection contract
- baseline validation helper

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

## D1 Dependency Rule

Allowed:

source_sidecar -> downstream_sidecar

Blocked:

downstream_sidecar -> upstream_sidecar
sidecar -> core_mutation
ui -> risk_flag_downgrade
archive -> source_overwrite

## D1 Output

D1 adds deterministic DAG dependency guard helpers and baseline tests.
