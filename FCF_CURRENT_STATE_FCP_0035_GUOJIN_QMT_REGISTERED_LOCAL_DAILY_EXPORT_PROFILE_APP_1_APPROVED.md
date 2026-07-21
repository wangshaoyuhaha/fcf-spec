# FCF Current State FCP 0035 Guojin QMT Registered Local Daily Export Profile App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0035-guojin-qmt-registered-local-daily-export-profile-app-1`

Approved scope:

- accept exact Operator-registered local Guojin QMT daily export bytes
- preserve the exact seven-column source schema and source digest
- require explicit instrument identity instead of filename inference
- normalize YYYYMMDD dates and 100-share lot volume deterministically
- preserve additive front-adjustment evidence without fabricating a factor
- expose incomplete range, missing factor, status, and point-in-time evidence
- remain compatible with the FCP-0017 and FCP-0019 authority contracts

No SDK, network retrieval, credential, provider selection, raw repository
retention, realtime activation, product phase, P48, trading API, order,
execution, tag, release, or deployment is authorized.
