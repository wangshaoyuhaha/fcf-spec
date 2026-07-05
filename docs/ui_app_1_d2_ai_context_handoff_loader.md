# UI-APP-D2 AI-CONTEXT Handoff Loader

## Purpose

UI-APP-D2 adds a local JSON loader for AI-CONTEXT handoff payloads.

The loader is read-only and accepts only local JSON files.

## Required payload fields

- app_id
- stage_id
- paper_only
- local_only
- read_only
- sidecar_only
- operator_review_required
- ranked_watchlist
- explanation_report
- operator_review_summary

## Safety rules

The loader rejects payloads that enable:

- buy buttons
- sell buttons
- order buttons
- broker connections
- exchange connections
- credential storage
- wallet private key access
- real account access
- real position access
- real execution
- operator review bypass
- core mutation

## Boundary

UI-APP-D2 does not modify P1-P47 core modules.
UI-APP-D2 does not create trade instructions.
UI-APP-D2 does not connect to any external service.
