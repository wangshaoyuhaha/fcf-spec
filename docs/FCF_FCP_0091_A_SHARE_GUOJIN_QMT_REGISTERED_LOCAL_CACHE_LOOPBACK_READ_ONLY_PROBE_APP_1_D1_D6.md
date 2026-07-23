# FCF FCP 0091 A-Share Guojin QMT Registered Local Cache Loopback Read-Only Probe App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Probe Registration

Register exact SDK lineage, symbol, date, daily period, time-only field,
one-row limit, no-fill policy, and local-cache-only function identity.

## D2 Terminal-Liveness Gate

Require exact FCP-0090 TERMINAL_OBSERVED evidence before dynamic SDK import or
probe invocation. Otherwise emit NOT_RUN without attempting a connection.

## D3 Single Local-Cache Call

Invoke only `xtquant.xtdata.get_local_data` once. Forbid subscriptions,
downloads, server retrieval, account APIs, trading APIs, and retries.

## D4 Value-Free Observation

Inspect shape and schema only. Retain no returned timestamps, prices, volumes,
amounts, order-book values, or arbitrary exception text.

## D5 Fail-Closed Evidence

Emit NOT_RUN, CALL_FAILED, CALL_SUCCEEDED_EMPTY, or CALL_SUCCEEDED_WITH_ROWS.
Keep entitlement, rights, provider, activation, promotion, and GAP-104 open.

## D6 Validation And Closeout

Run isolated, affected A-share and governance, all FCP, full pytest, and
all-checks suites; restore generated outputs; audit exact files, ASCII, hashes,
and `git diff --check`; then commit, push, merge, revalidate, and synchronize.
