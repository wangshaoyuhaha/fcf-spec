# ARTIFACT-LIFECYCLE-REGISTRY-APP-1 D2

## Stage

ARTIFACT-LIFECYCLE-D2 lifecycle transition policy.

## Purpose

Define read-only lifecycle transition validation.

## D2 Adds

- allowed lifecycle transition vocabulary
- transition validation
- transition index
- unresolved marking for invalid transitions

## Boundary

D2 only validates and indexes lifecycle transitions.

D2 must not:

- mutate source artifacts
- apply lifecycle status changes
- auto-repair artifact status
- backfill evidence
- auto-pass operator review
- touch P1-P47 core
- create P48
- tag
- release
- deploy
