# DATA-AND-CREDENTIAL-GOVERNANCE D2 Licensing

## Status

IMPLEMENTED

## Delivered

- immutable per-source license policies
- deterministic license-policy registry checksum
- explicit local, cloud, redistribution, and training permissions
- retention and Operator-review requirements
- fail-closed evaluator with evidence-linked decisions

Missing policies, prohibited licenses, unlicensed uses, and external uses without
explicit permission are blocked. Unknown or restricted licenses may only remain
degraded and Operator-reviewable for an explicitly allowed local use.

No network retrieval, secret material, authenticated request, or execution path
is introduced.
