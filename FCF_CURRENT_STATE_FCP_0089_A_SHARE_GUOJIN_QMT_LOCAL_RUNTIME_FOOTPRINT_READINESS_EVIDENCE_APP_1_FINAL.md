# FCF Current State FCP 0089 A-Share Guojin QMT Local Runtime Footprint Readiness Evidence App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0089-A-SHARE-GUOJIN-QMT-LOCAL-RUNTIME-FOOTPRINT-READINESS-EVIDENCE-APP-1

The immutable path-free runtime-footprint readiness evidence is implemented,
validated, and merged to main. It uses a bounded non-recursive metadata-only
scan of one Operator-designated local Guojin QMT `userdata_mini` directory.

Validation evidence:

- isolated FCP-0089 tests: 11 passed
- affected A-share and governance tests: 518 passed
- all FCP tests: 1759 passed
- full pytest: 7096 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED before and after merge
- generated outputs: restored; no tracked generated changes remained

Contract SHA-256:
`8e711a0463613aa1f60eded5b798378c246aaa981c88ffa5ddeefba1fd6f7e17`.
Reference evidence hash:
`e1a4de03cd08c483dcda80032cdec8d5a031da72bb3e5ef310aae3563a676887`.
Reference output SHA-256:
`b2575598a635c43069b92ef8886d0de8d9fcceb62659f8dc1a488280ed2ff74e`.
Observed footprint manifest SHA-256:
`e615110671b90557c134a4696201e25f70a81f99842040bf8e3f7d2ab8629454`.
Observed footprint evidence hash:
`09d6c3f8555ec9f50366a51c0a388702d13b565db93db5d2240bb5d82a701511`.

Evidence commits:

- approval: `22d68c98eb59bd6f0fd2044711017387386cd01a`
- sidecar delivery: `04cdea7059fc5678e809ce0624fc0d4f7e4852ca`
- main merge: `b6e531c6e0811a1662b9f2bb9ed2e1bacf9e09b9`

The registered-local snapshot contains 20 top-level entries, six directories,
14 regular files, 340752361 aggregate regular-file bytes, all required
directory and cache-family classes, and readiness state
READY_FOR_OPERATOR_PROBE. GAP-104 remains RESEARCH_REQUIRED. Terminal
liveness, entitlement, rights, retention, market-data availability, provider
selection, realtime activation, and data promotion remain unproven.

No file content, recursive traversal, arbitrary entry name, local path, SDK
invocation, process inspection, network, credentials, accounts, market values,
product, P48, broker, exchange, balance, position, order, execution, tag,
release, or deployment authority was created.
