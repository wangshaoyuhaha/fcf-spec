# FCF Current State FCP 0090 A-Share Guojin QMT Local Terminal Liveness Evidence App 1 Delivered

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0090-A-SHARE-GUOJIN-QMT-LOCAL-TERMINAL-LIVENESS-EVIDENCE-APP-1

The sidecar implements immutable registration, snapshot, evidence, a Windows
local process-name observer, immediate closed-registry reduction, and a
path-free canonical renderer.

Contract SHA-256:
`c82466c987b415d5d78db0dba161fc1653b651d8caa642860ba5dda6772c097a`.
Reference snapshot SHA-256:
`f990651e95449acae4863fd4812ba5569734f95b736b681c2c62e4bfe134c2f8`.
Reference evidence hash:
`73683bffb99cbb428c275ea8e07c85e0edf8e41177c9dcf949e6fca1afd2af17`.
Reference output SHA-256:
`366c02360c7192505a3d651e20c84d21b238e1188203a4a3443e9f2681c0ab6a`.

Observed registered-local liveness evidence at
2026-07-23T00:57:11.436138Z:

- observed process names: 372
- registered QMT family counts: all zero
- readiness state: TERMINAL_NOT_OBSERVED
- snapshot SHA-256: `072f841a38aa778b2646cdc0123a8a9f2c71d4c6c902e519d5ed8a756eeb02ba`
- evidence hash: `ce66a717ca3cf83795111d506b7817f829f749b6caba44cf59b793e9110bee07`
- blockers: MINIQMT_ENTITLEMENT_UNPROVEN, READ_ONLY_MARKET_DATA_PROBE_UNPROVEN, QMT_TERMINAL_NOT_OBSERVED

No arbitrary process name, identifier, owner, session, command line,
executable path, window, account identifier, credential, or market value was
retained. GAP-104 remains RESEARCH_REQUIRED. No SDK invocation, network,
provider, realtime, promotion, product, P48, broker, exchange, balance,
position, order, execution, tag, release, or deployment authority is created.
