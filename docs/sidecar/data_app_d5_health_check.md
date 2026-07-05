# DATA-APP-D5 Health_Check

Status: completed

Purpose:
- Add Health_Check tri-state gate for DATA-APP.
- Prevent bad data from entering STOCK-APP scoring.
- Keep AI from rationalizing broken or incomplete data.

States:
- PASS_STRICT: clean data enters Clean Universe.
- PASS_LIMITED: usable but limited data enters watchlist only.
- FAIL_QUARANTINE: bad data enters quarantine report.

Hard checks:
- manifest_ok
- has_rows
- required_fields_ok
- no_rejected_rows
- date_consistency_ok
- price_sanity_ok
- liquidity_ok
- trading_status_ok

Routing:
- PASS_STRICT -> CLEAN_UNIVERSE
- PASS_LIMITED -> WATCHLIST_ONLY
- FAIL_QUARANTINE -> QUARANTINE

Safety:
- paper-only
- local-only
- read-only
- no real exchange API
- no real brokerage API
- no API key
- no real order
- no real execution
- no real money impact
- operator review required
