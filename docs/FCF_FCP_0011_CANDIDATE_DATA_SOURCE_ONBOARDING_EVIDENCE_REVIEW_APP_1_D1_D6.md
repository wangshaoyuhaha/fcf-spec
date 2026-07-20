# FCF FCP 0011 Candidate Data Source Onboarding Evidence Review App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Candidate Profile

Candidate profiles contain safe identity, display name, application state,
Operator-declared markets and canonical fields, and registered evidence IDs.
Secret material is rejected. Network state is DISABLED, provider selection is
UNSELECTED, and Operator review is mandatory.

## D2 Documentary Evidence Completeness

The closed evidence categories are rights, permitted use, retention, lineage,
freshness and latency, cost and quota, schema, and timestamp and revision
semantics. Missing categories remain explicit. Empty evidence cannot be inferred
from a provider name, an application approval, a local demo, or a declared field.

## D3 Canonical Compatibility

Compatibility is assessed against the FCP-0009 canonical
TICK, MINUTE_BAR, and ORDER_BOOK required fields. It does not embed a vendor schema, call a vendor,
or assert that a declared field is actually available.

## D4 Deterministic Review Packet

Each immutable packet exposes documentary status, compatibility status, missing
evidence, missing fields, application state, and a deterministic SHA-256 hash.
External activation is always BLOCKED, entitlement is UNRESOLVED, credentials
are ABSENT, network is DISABLED, and provider selection is UNSELECTED.

## D5 Read-Only Browser Review

`/data-source-onboarding` supports GET and HEAD only. Simplified Chinese is the
default and English remains explicit. No form, button, script, upload, secret
input, write, approval, trading, or execution control is present.

The registered fixture lists Operator-declared candidate names only. All five
candidates remain incomplete until the Operator supplies registered documentary
evidence and declared canonical field coverage. The complete synthetic candidate
exists only to prove deterministic evaluation and cannot authorize activation.

## D6 Validation And Closeout Boundary

Validation order is the FCP-0011 isolated suite, related FCP-0001/FCP-0009/FCP-0010
and browser targeted suite, full pytest, `scripts/run_all_checks.py`, generated
output restoration, exact changed-file verification, and `git diff --check`.

Validation evidence:

- MappingProxy review hashing smoke: passed
- ASCII application source smoke: passed
- FCP-0011 isolated suite: 28 passed
- related entitlement, adapter, localization, and browser suite: 652 passed
- validation-lock governance suite: 49 passed
- full pytest: 5621 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored by the explicit allowlist
- governance approval commit: `2986334cb15c025162acc8246655cd1404a564e1`
- sidecar delivery commit: `e1d188801efa95f8be9f59e8e401e37971524564`
- main merge commit: `d9e5057bdebca66526125a105a0f1700c011d2da`

FCP-FCP-0011 remains ACCEPTED_ARCHITECTURE with phase_id NONE. Validation cannot
select a provider, connect a network, accept credentials, approve rights, close
a gap, claim realtime or product readiness, start a product phase, create P48,
or enable execution.
