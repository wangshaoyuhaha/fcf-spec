# FCF Current State FCP 0027 Registered Data Primitive Type Integrity Hardening App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0027-registered-data-primitive-type-integrity-hardening-app-1`

Approved scope:

- exact lowercase SHA-256 inputs without silent normalization in BTC substrate and bridge contracts
- strict non-boolean integers for bounded byte, count, sequence, and schema fields
- exact closed boolean flags across local A-share and BTC bridge authority boundaries
- isolated regression coverage for every independently reproduced acceptance defect
- preserved provider neutrality, market isolation, and mandatory Operator review
- validation, merge, and authority synchronization

No SDK, network, credential, provider selection, wallet, account, balance,
position, order, execution, realtime, product phase, P48, tag, release, or
deployment is authorized.
