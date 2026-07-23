# FCF Current State FCP 0088 A-Share Guojin QMT Registered Local Dual Export Offline SDK Compatibility Evidence App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0088-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-DUAL-EXPORT-OFFLINE-SDK-COMPATIBILITY-EVIDENCE-APP-1

The immutable path-free compatibility evidence is implemented, validated, and
merged to main. It combines exact typed FCP-0035 front-adjustment reference and
FCP-0084 coverage evidence with one explicit offline CPython 3.11 native-module
load observation. It does not connect to MiniQMT or invoke market-data
functions.

Validation evidence:

- isolated FCP-0088 tests: 14 passed
- affected A-share and governance tests: 849 passed
- all FCP tests: 1748 passed
- full pytest: 7085 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED before and after merge
- generated outputs: restored; no tracked generated changes remained

Contract SHA-256:
`bb15419efd3b45ee37fc05b9e5ee8507f363670fe78b5db451bf79a1d895b1f1`.
Reference evidence hash:
`fd0760c7f04012d0ba3db0b2af43233579b111fafdd04be14fe2e9b4e8ee8509`.
Reference output SHA-256:
`2f86c7b4b7c63f538ee6cebdf5ff463e05600792911a27517dfa378875abda64`.
Observed compatibility evidence hash:
`4d6f4924326be8ffa9e72d055196a242488ab46e6b239030becea4cd17f0ada5`.
Observed coverage evidence hash:
`ee9cd9c718b57d9d41bb8247190790ba8388adf4b27cb5d8f6504d6499e87f38`.
Observed SDK ABI hash:
`d606cf3d59c00539811faebfd86c8352607725afa7ff89f9f9730445871fba2c`.

Evidence commits:

- approval: `f8ab4851b20158578bd871f164c04c38bf2bfa35`
- sidecar delivery: `df71c76058feaa77f13a1930ff97e36ed30da27f`
- main merge: `2383e8c941954757a14c698544b9587259f84970`

Observed registered-local evidence remains limited to 500 rows dated
2024-06-28 through 2026-07-21, five adjustment boundaries, and one offline
native load with no connection or network use. GAP-104, GAP-105, and GAP-106
remain RESEARCH_REQUIRED. Entitlement, rights, retention, expected dates,
pagination, completeness, adjustment-factor authority, trading status, and
point-in-time supplements remain unproven.

No raw or normalized rows, market values, paths, SDK connection, network,
credentials, accounts, provider selection, realtime activation, promotion,
product, P48, broker, exchange, balance, position, order, execution, tag,
release, or deployment authority was created.
