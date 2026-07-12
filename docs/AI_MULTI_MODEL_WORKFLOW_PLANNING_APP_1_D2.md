# AI-MULTI-MODEL-WORKFLOW-PLANNING-APP-1 D2

## Stage

AI-MULTI-MODEL-WORKFLOW-PLANNING-D2

## Purpose

Bind existing machine-readable role contracts to planning-only model
slots using references from the existing Model and Prompt Version
Registry.

D2 does not create a new role, model, Prompt, Policy, Config Snapshot,
or Routing Eligibility registry.

## Source role boundary

The authoritative existing role manifest contains:

- deterministic runtime orchestration coordinator
- market narrative context analyst
- causal reasoning analyst
- contrarian challenge reviewer
- comprehensive report synthesizer
- terminal human Operator

Only roles whose existing role kind is PLANNED_AI_ROLE may receive model
slot bindings.

The deterministic coordinator and Human Operator cannot receive model
bindings.

## Required slots

Every existing PLANNED_AI_ROLE must contain:

- PRIMARY
- FALLBACK
- COMPARISON
- LOCAL_ONLY
- CLOUD_APPROVED

Each slot references:

- existing model registry entry
- existing Prompt registry entry
- provider identifier
- local or cloud location
- Policy identifier
- Policy version
- Policy digest
- Config Snapshot identifier

## Cloud boundary

CLOUD_APPROVED is a slot name only.

It does not grant cloud permission or runtime activation.

A cloud slot remains POLICY_REVIEW_REQUIRED and requires deterministic
privacy, licensing, registered-artifact, Policy, Config Snapshot, and
Operator review gates.

## Runtime restrictions

Every role and slot remains:

- planning-only
- not active
- not automatically selectable
- not automatically switchable
- not automatically routable
- model invocation NOT_ALLOWED
- Prompt execution NOT_ALLOWED
- runtime activation NOT_ALLOWED
- archive writing NOT_ALLOWED
- real execution NOT_ALLOWED

## Permanent boundary

- P1-P47 frozen
- no P48
- no Core mutation
- paper-only
- read-only
- sidecar-only
- deterministic authority preserved
- registered artifacts only
- Operator review required
- no HTTP service
- no port listener
- no credential access
- no broker or exchange connection
- no balance or position access
- no wallet access
- no real order
- no tag
- no release
- no deploy