# SIDECAR-TOPOLOGY-REVIEW-APP-1 D5 Future Sidecar Queue and Governance Gates

Status: D5 future sidecar queue and governance gates completed.

## Purpose

This document defines the future sidecar queue rules and governance gates after the topology review.

It is governance-only and does not approve feature implementation by itself.

## Queue rule

No future sidecar may start automatically.

Each future sidecar requires:

- explicit operator approval
- declared upstream artifacts
- declared downstream artifacts
- declared read boundary
- declared write boundary
- declared safety boundary
- declared rollback path
- validation tests
- current-state source file
- final closeout package before merge review

## Candidate sidecar queue

| Priority | Candidate | Status | Notes |
| --- | --- | --- | --- |
| Q1 | CONTROL-CENTER-MAINTENANCE-APP-1 | candidate | keep total control file current after each merge |
| Q2 | DIFY-LOCAL-CONFIG-HARDENING-APP-1 | deferred optional candidate | only when operator is ready to configure Dify or Ollama locally |
| Q3 | CORRELATION-ID-TRACEABILITY-APP-1 | candidate | strengthen global Correlation_ID across reports and archives |
| Q4 | RISK-FLAG-VISIBILITY-APP-1 | candidate | ensure UI and reports never hide or downgrade risk flags |
| Q5 | REASON-CODE-GOVERNANCE-APP-1 | candidate | strengthen reason-code consistency across sidecars |
| Q6 | ARCHIVE-INTEGRITY-REVIEW-APP-1 | candidate | review immutable archive chain and final state records |
| Q7 | OPERATOR-WORKFLOW-REVIEW-APP-1 | candidate | review manual operator gates and handoff workflow |

## Governance gates

Every candidate sidecar must pass these gates before development:

### Gate 1: Scope gate

The sidecar must clearly state:

- problem
- non-goals
- files to create or modify
- files not allowed to modify
- safety boundary

### Gate 2: Core freeze gate

The sidecar must confirm:

- no P48
- no mutation of frozen core P1-P47
- no direct bypass of core governance
- no direct real-money execution path

### Gate 3: Data and artifact gate

The sidecar must declare:

- upstream artifacts
- downstream artifacts
- artifact owner
- artifact immutability rule
- traceability rule

### Gate 4: Operator review gate

The sidecar must preserve:

- manual operator review
- no automated trade approval
- no deploy
- no release
- no tag without explicit approval

### Gate 5: UI and presentation gate

Any UI-facing sidecar must confirm:

- risk flags remain visible
- reason codes remain visible
- blocked outputs remain blocked
- safe fallback responses remain safe
- UI cannot downgrade governance state

### Gate 6: Dify and external tool gate

Any Dify-related or external-tool-related sidecar must confirm:

- no automatic Dify app creation
- no Dify API write unless explicitly approved in a future separate scope
- no deployment
- no secrets
- no API keys
- no private keys
- no broker, exchange, or wallet connection

### Gate 7: Validation gate

The sidecar must include:

- deterministic validation tests
- safety-boundary tests
- current-state file test when applicable
- final clean git status before merge review

## Deferred item

DIFY-LOCAL-CONFIG-HARDENING-APP-1 remains deferred.

It must not start until the operator explicitly confirms local Dify or Ollama configuration work.

## D5 result

The future sidecar queue and governance gates are established.

D6 must create final closeout and main merge review package.
