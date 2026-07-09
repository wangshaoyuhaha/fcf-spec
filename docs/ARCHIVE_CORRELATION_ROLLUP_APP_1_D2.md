# ARCHIVE-CORRELATION-ROLLUP-APP-1 D2

## Stage

ARCHIVE-CORRELATION-D2 read-only source artifact reference model.

## Purpose

Define how existing artifact references are indexed for correlation rollup.

This stage records metadata only. It does not read, mutate, repair, backfill, or create source evidence.

## D2 Adds

- source artifact reference builder
- source artifact reference validator
- read-only reference index grouped by required rollup links
- missing chain detection as mark-only status

## Required Link Types

- data_snapshot
- candidate
- ai_explanation
- ui_packet
- review_packet
- archive_packet
- handoff
- final_state

## Status Policy

Allowed source reference statuses:

- PRESENT
- INCOMPLETE
- STALE
- UNRESOLVED

Rollup index status:

- COMPLETE when every required link exists and validates
- INCOMPLETE when one or more required link types are absent
- UNRESOLVED when all link types exist but one or more references fail validation

## Explicit Non-Actions

D2 must not:

- mutate source artifacts
- delete source artifacts
- overwrite source artifacts
- repair source artifacts
- backfill evidence
- auto-fill correlation_id
- generate placeholder review
- auto-pass operator review
- create UI dashboard panel
- touch P1-P47 core
- create P48
- tag
- release
- deploy
