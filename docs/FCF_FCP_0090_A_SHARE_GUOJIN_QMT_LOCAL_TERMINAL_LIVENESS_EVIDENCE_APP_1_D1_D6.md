# FCF FCP 0090 A-Share Guojin QMT Local Terminal Liveness Evidence App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Process-Family Registry

Register exact Guojin QMT process families and a bounded observation policy.

## D2 In-Memory Local Enumeration

Enumerate local process names only. Do not request identifiers, owners,
sessions, command lines, executable paths, windows, or account context.

## D3 Immediate Allowlist Reduction

Discard unregistered names immediately and retain only registered-family
presence and bounded counts.

## D4 Fail-Closed Liveness Evidence

Emit TERMINAL_OBSERVED only when a registered terminal family is present.
Otherwise emit TERMINAL_NOT_OBSERVED with explicit blockers.

## D5 Authority Boundary

Keep GAP-104 open. Liveness is not entitlement, rights, retention,
market-data availability, provider selection, realtime activation, or data
promotion authority.

## D6 Validation And Closeout

Run isolated, affected A-share and governance, all FCP, full pytest, and
all-checks suites; restore generated outputs; audit exact files, ASCII, hashes,
and `git diff --check`; then commit, push, merge, revalidate, and synchronize.
