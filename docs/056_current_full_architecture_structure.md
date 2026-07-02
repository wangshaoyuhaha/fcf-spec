# Current Full Architecture Structure

Status: living architecture snapshot

Root direction:
- BTC is the first paper-only implementation line.
- The final target is a general FCF-style finance platform for crypto, stocks, ETFs, FX, commodities, and other markets.
- The whole project remains paper-only.

Original FCF skeleton mapping:
- fcf/core/event_bus.py -> future event-driven orchestration
- fcf/core/event_model.py -> current stable contracts and typed dictionaries
- fcf/core/policy_engine.py -> P5 policy gates and governance checks
- fcf/modules/perception.py -> local data, multi-market inputs, future adapters
- fcf/modules/regime.py -> P5 regime classification
- fcf/modules/governor.py -> P5 risk governor
- fcf/modules/execution.py -> paper-only review/archive workflow, no real execution
- fcf/modules/simulation.py -> future P9 backtest and calibration
- fcf/modules/meta.py -> future P10 model/version registry
- fcf/storage/audit_store.py -> P3/P4/P5/P6/P7 reports, audit trail, future learning memory

Completed phases:
- P0 paper-only safety skeleton
- P1 single-symbol paper analysis loop
- P2 multi-symbol and batch paper analysis loop
- P3 local data schema, fixtures, validation, handoff
- P4 paper analysis logic, review packet, readable report
- P5 risk governance, regime layer, policy gate, audit, UI contract
- P6 multi-market architecture, adapter registry, readiness gate
- P7 operator console contract through report and manifest

Planned future phases:
- P8 learning memory and feedback dataset
- P9 backtest and calibration
- P10 model registry and strategy versioning
- P11 UI and operator console pages
- P12 final archive and delivery

Safety boundary:
- paper-only
- no real exchange API
- no real brokerage API
- no real API key
- no wallet private key
- no real order
- no real execution
- no real balance
- no real position
- no real money impact
- operator review required
