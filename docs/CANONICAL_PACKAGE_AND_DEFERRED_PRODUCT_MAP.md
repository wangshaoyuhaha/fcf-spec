# Canonical Package and Deferred Product Map

## Canonical Active Surfaces

- `apps/` contains current bounded product and runtime applications
- `src/fcf/` contains established FCF sidecar libraries
- `scripts/` contains local validation and Operator utilities
- `tests/` contains contract, integration, runtime, and control guards
- `docs/FCF_PROJECT_CONTROL_CENTER.md` is the project authority

## Legacy Compatibility Surfaces

The root `app/`, older root `*_app` packages, and `src/btc_finance_platform/`
remain compatibility surfaces. They must receive no new product capability
unless a migration phase explicitly authorizes it. Existing imports are frozen
until incremental migration tests prove removal is safe.

## Explicitly Deferred Product Work

- Dify and model-provider configuration
- live model and Prompt execution
- specialist training execution
- live or remote market-data retrieval
- persistent backend execution of Console actions
- full package consolidation
- public deployment and real financial execution
- V2 Factor Registry and forecast-target runtime
- V2 State-Sync and macro-to-micro transmission runtime
- V2 realtime ingestion, order-book, and anomaly-radar runtime
- V2 asynchronous cognitive shield and Paper simulation research

## Delivered V2 Contract Foundation

`apps/v2_r1_factor_contract_foundation_app_1/` is the canonical V2-R1
contract-only Sidecar. It provides immutable factor and forecast-target
metadata, append-only local registries, deterministic State-Sync anchors, and
read-only Operator presentation. It does not calculate or activate factors,
select a market or data provider, retrieve data, score candidates, invoke AI,
or create any order or execution path.

The deferred production Factor Registry, target-label, and State-Sync runtimes
remain tracked in the Gap register. Contract foundation delivery does not
close those production-runtime gaps.

`apps/v2_r2_historical_factor_baseline_app_1/` is the canonical V2-R2 local
historical-baseline Sidecar. It accepts explicit registered-artifact metadata,
enforces point-in-time availability and rights, calculates deterministic
Decimal baseline statistics, and provides leakage-safe replay and read-only
review. It does not retrieve data, select a market, activate factors, rank
candidates, or create an execution path.

`apps/v2_r3_local_event_ingress_foundation_app_1/` is the canonical V2-R3
local registered-event ingress Sidecar. It validates deterministic event,
receive, and processing time, bounded sequence and capacity, immutable replay,
checkpoint restoration, and read-only review metadata. It is not an approved
realtime source, external queue, daemon, market connection, scanner, or
anomaly-radar runtime.

Canonical future-architecture sources:

- `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md`
- `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md`
- `docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md`
- `docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md`
- `FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json`

These sources are accepted architecture, not delivered product capability.

The current-state manifest, Project Control Center, three architecture
registers above, Future Capability Change Protocol, and Future Capability
Intake Register form the `FCF Seven-File Project Governance and Memory System`.
The accepted institutional-calendar extension is
`FCF-V2-INSTITUTIONAL-CALENDAR-CAUSAL-MARKET-INTELLIGENCE`; it remains
NOT_IMPLEMENTED and has no selected phase.

Current project truth and continuity sources:

- `FCF_CURRENT_STATE_MANIFEST.json`
- `docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md`

The manifest states what is current. The future architecture states what may
exist later. The Gap register states what is unfinished or outside current
authorization. Historical handoff text cannot override the manifest.

## Generated Output Policy

- `artifacts/` contains reproducible local smoke outputs and is not canonical
- Dify handoff entries under `artifacts/` are optional generated sources
- tracked runtime and current-state Dify sources remain mandatory
- generated outputs may be deleted after validation
- four tracked runtime outputs are restored byte-for-byte by `run_all_checks.py`

## Legal Decision

No LICENSE file is present. The repository owner must choose the legal license.
Engineering work must not infer legal permission on the owner's behalf.
