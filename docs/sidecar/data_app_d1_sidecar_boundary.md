# DATA-APP-D1 Sidecar Boundary

Status: completed

Purpose:
- Define DATA-APP as a sidecar application layer.
- Preserve P1-P47 core freeze.
- Avoid P48 core expansion.
- Prepare read-only data ingestion before STOCK-APP.

Allowed scope:
- CSV input
- Excel input
- JSON input
- Local database input
- Public read-only data input
- Schema validation
- Manifest and checksum planning
- Health_Check planning
- Clean Universe handoff planning

Forbidden scope:
- No core import from DATA-APP in core modules
- No core mutation
- No core audit store write
- No real exchange API
- No real brokerage API
- No API key storage
- No wallet private key access
- No real order creation
- No real execution
- No real balance read
- No real position read
- No real money impact
- No auto trading

Contract:
- App: DATA-APP
- Contract version: DATA_APP_SIDECAR_D1
- Layer: sidecar
- Next layer: STOCK-APP
- Operator review required: true

Validation:
- scripts/run_data_app_boundary_smoke.py
- tests/test_data_app_boundary.py
