# CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1

## D1 Freshness Contract

Status: completed.

Purpose:
CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1 prevents stale handoff claims across project control center, backend handoff files, new-window prompts, and final current-state files.

Protected records:
- docs/FCF_PROJECT_CONTROL_CENTER.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md
- docs/HANDOFF_PROMPT.md
- FCF_CURRENT_STATE_*.md

Current baseline:
- latest main commit: b757644
- latest phase: CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
- latest merge commit: 2feba64
- latest D6 commit: 36db8f6
- latest validation: python -m pytest -q = 1782 passed
- run_all_checks: passed
- next phase: CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1

## D2 Handoff Source Loader

Status: completed.

Purpose:
D2 adds deterministic source discovery and UTF-8 loading for freshness-protected handoff artifacts.

Source groups:
- control center
- backend handoff
- new-window prompt
- docs handoff prompt
- final current-state files

Loader rules:
- load only tracked repo files
- ignore missing optional files safely
- preserve relative path identity
- read text as UTF-8
- never mutate loaded files
- never infer freshness by LLM

Safety boundary:
- paper-only
- local-only
- read-only governance validation
- sidecar-only
- operator review required
- no P48
- no core mutation
- no real trading
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## D3 Freshness Snapshot Builder

Status: completed.

Purpose:
D3 adds deterministic freshness snapshot extraction from loaded handoff artifacts.

Extracted signals:
- commit hashes
- pytest passed counts
- control-center phase tokens
- protected file path
- text length

Snapshot rules:
- extraction is code-only
- no LLM freshness inference
- no file mutation
- no runtime action
- no trading action

## D4 Freshness Drift Detector

Status: completed.

Purpose:
D4 adds deterministic drift detection between protected handoff snapshots and the approved baseline.

Detected drift:
- missing latest main commit
- missing latest completed phase
- missing latest merge commit
- missing latest D6 commit
- missing latest pytest count
- stale commit reference
- stale phase reference
- stale pytest count reference
- unsafe runtime reference

Rule:
Any drift means the handoff artifact is not fresh and must not be used as a new-window source until repaired.

## D5 Freshness Guard Packet

Status: completed.

Purpose:
D5 adds a deterministic guard packet that summarizes freshness drift across all protected handoff artifacts.

Packet fields:
- app_id
- total_sources
- blocked_sources
- passed
- reason_codes
- blocked_paths

Guard rule:
If any protected handoff artifact has drift reason codes, the packet fails.

The packet is paper-only, local-only, read-only, and cannot repair or overwrite source files.
