# P14-D34 To P14-D36 Data Quality Sentry

Status: completed after validation.

Scope:
- P14-D34: classify paper data quality issues
- P14-D35: generate local data quality sentry report
- P14-D36: regression tests for no-auto-quarantine boundary

Purpose:
Detect missing, stale, or outlier paper data before learning, trust scoring, and governor proposals.

Allowed:
- detect missing data
- detect stale data
- detect outlier data
- propose quarantine for operator review
- write local report

Forbidden:
- auto-quarantine sources
- auto-disable sources
- connect real exchange API
- connect real brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real balances or positions
- affect real money

Operator review remains required.
