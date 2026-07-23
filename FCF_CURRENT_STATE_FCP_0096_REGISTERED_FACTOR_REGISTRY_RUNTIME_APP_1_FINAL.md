# FCF Current State FCP 0096 Registered Factor Registry Runtime App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0096-REGISTERED-FACTOR-REGISTRY-RUNTIME-APP-1

Delivery commit:
`a089b27e0d93576f4c92d4385c7ab6cd7cbe92df`.
Merge commit:
`21f28b91223a8b7aec4459201de32292ac3071f9`.

The registered-artifact-only sidecar verifies exact ASCII JSON bytes and
builds immutable record, dependency, reverse-dependency, topological,
retirement, replacement, and transitive invalidation views.

Reference artifact SHA-256:
`be3e9b4edd3ab38b74459546a73aed8809907f2dfe1c27aee173fd924f8a95f9`.
Runtime snapshot hash:
`c576022a450c15ec3185e6756d2b48998c3ab761eaa95ce657945e0c2be61a40`.
Rendered output SHA-256:
`574c8467beaf5a70a76b5c27a4d5b7a04a8bdda45b483a6785347ca09eb6cc3d`.

Validation: 8 isolated tests, 53 affected-chain tests, 1848 all-FCP tests,
7185 full-pytest tests, and `run_all_checks.py` passed.

GAP-001, GAP-005, and GAP-007 remain open pending complete production
acceptance evidence. No calculation, scoring, promotion, account, order, or
execution authority was created. No tag, release, or deployment was run.
