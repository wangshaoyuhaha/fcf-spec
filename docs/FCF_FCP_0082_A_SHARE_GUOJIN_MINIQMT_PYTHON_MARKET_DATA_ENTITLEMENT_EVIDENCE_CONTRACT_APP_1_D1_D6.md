# FCF FCP 0082 A-Share Guojin MiniQMT Python Market-Data Entitlement Evidence Contract App 1 D1-D6

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

## D1 Closed Evidence Vocabulary

Define exact terminal, Python module, entitlement, capability, probe, rights,
retention, compatibility, blocker, and review-state vocabularies.

## D2 Sanitized Registered Artifact Boundary

Accept only bounded ASCII metadata without account identifiers, credentials,
authorization codes, tokens, passwords, raw market values, or executable
requests. Verify exact byte length and SHA-256 before parsing.

## D3 MiniQMT Market-Data Compatibility Facts

Bind declared terminal and module versions, local module identity, read-only
market-data capability, market coverage, clock semantics, and exact probe
metadata without importing or invoking MiniQMT or xtquant.

## D4 Deterministic Fail-Closed Evaluation

Emit only INSUFFICIENT_EVIDENCE or OPERATOR_REVIEW_ELIGIBLE. Missing,
conflicting, expired, secret-bearing, executable, non-read-only, or
unregistered facts remain blocked and cannot be inferred.

## D5 Mandatory Operator Review Packet

Expose exact evidence identity, observed facts, blockers, compatibility state,
and non-authorizing outcome. Review eligibility cannot establish entitlement,
select a provider, activate data, promote rows, or close the Gap.

## D6 Validation And Closeout

Run isolated tests, affected A-share data and governance tests, all FCP tests,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, ASCII verification, and `git diff --check` before
commit, push, merge, and final synchronization.
