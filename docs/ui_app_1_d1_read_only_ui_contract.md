# UI-APP-D1 Read-Only UI Contract

## Purpose

UI-APP-1 is a local read-only workflow and report viewing sidecar.

It reads structured outputs from:

- DATA-APP-1
- STOCK-APP-1
- AI-CONTEXT-1

It renders local view models and local report artifacts for operator review.

## Allowed scope

- Show clean universe, watchlist, and quarantine summary.
- Show ranked watchlist.
- Show score breakdown.
- Show reason codes.
- Show risk flags.
- Show AI-CONTEXT explanation report.
- Show operator review summary.
- Show read-only workflow status.
- Generate local read-only HTML, JSON, or text reports.
- Record paper-only operator review status locally.

## Forbidden scope

- No trade action buttons.
- No broker connection.
- No market execution connection.
- No credential storage.
- No private secret access.
- No real account access.
- No real position access.
- No real execution.
- No P1-P47 core mutation.
- No P48 core expansion.
- No operator review bypass.

## Safety boundary

UI-APP-1 must remain:

- paper-only
- local-only
- read-only
- sidecar-only
- operator-review-required

The core must not import UI-APP-1, and UI-APP-1 must not mutate core state.
