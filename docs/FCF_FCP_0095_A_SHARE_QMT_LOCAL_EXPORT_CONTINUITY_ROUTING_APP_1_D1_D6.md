# FCF FCP 0095 A-Share QMT Local Export Continuity Routing App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact Runtime Evidence

Bind the exact path-free FCP-0090 terminal-observed and FCP-0091
single-call-failed evidence hashes without retaining account or market values.

## D2 Non-Blocking MiniQMT State

Record MiniQMT as `DEFERRED_NON_BLOCKING`; do not retry the failed call.

## D3 Registered Local Export Continuity

Preserve `REGISTERED_QMT_LOCAL_EXPORT` as the available research workflow
without granting provider or promotion authority.

## D4 Candidate Supplement Isolation

Keep RQData trial and Tushare as closed, ordered, unselected candidate
supplements.

## D5 Closed Next Actions And Open Gaps

Require local batch registration, batch coverage validation, and independent
candidate reconciliation. Preserve GAP-093 through GAP-109.

## D6 Validation And Closeout

Run isolated, affected, all FCP, full pytest, and all-checks suites; restore
generated outputs; audit exact files and `git diff --check`; then commit, push,
merge, revalidate, and synchronize final authority state.

Completed evidence:

- delivery commit: `628ccae826840b760fdf3303308874914835f75a`
- merge commit: `f9e0ebcf47b9a55e0857ff1c9ac3631012c174c1`
- isolated tests: 33 passed
- affected-chain tests: 102 passed
- all-FCP tests: 1840 passed
- full pytest: 7177 passed
- `run_all_checks.py`: passed
