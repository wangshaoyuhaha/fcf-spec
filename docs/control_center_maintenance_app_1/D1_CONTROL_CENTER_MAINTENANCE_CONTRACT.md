# CONTROL-CENTER-MAINTENANCE-APP-1 D1 Contract

Status: D1 planning contract.

## Purpose

CONTROL-CENTER-MAINTENANCE-APP-1 is a governance-only sidecar.

It defines the mandatory maintenance rules for the FCF Project Control Center after each completed sidecar merge.

## Scope

This sidecar must define:

- when the control center must be updated
- what merge information must be recorded
- what validation information must be recorded
- what deferred backlog items must be preserved
- what safety boundaries must remain visible
- what must never be inferred only from chat memory

## Mandatory control center update trigger

The FCF Project Control Center must be updated after:

- each sidecar main merge
- each final current-state file commit
- each architecture gap review
- each accepted backlog change
- each deferred backlog decision
- each safety-boundary repair
- each validation baseline change

## Required merge record fields

Each control center merge record must include:

- sidecar name
- branch name
- main merge commit
- final branch commit
- push status
- validation result
- pytest count
- final git status
- no tag confirmation
- no release confirmation
- no deploy confirmation
- final files
- deferred backlog changes
- next candidate sidecars

## Source of truth rule

The control center file is the repo-level source of truth.

Chat memory may summarize state, but must not replace repo control records.

## Safety boundary

This sidecar must remain:

- paper-only
- local-only
- read-only
- governance-only
- operator-review-only
- sidecar-only

This sidecar must not:

- mutate frozen core P1-P47
- create P48
- connect broker APIs
- connect exchange APIs
- connect wallet APIs
- store API keys
- read real accounts
- read real positions
- create real orders
- execute real trades
- deploy anything
- create a release
- create a tag

## D1 deliverables

- D1 maintenance contract
- sidecar package placeholder
- D1 validation test
- D1 current-state file
