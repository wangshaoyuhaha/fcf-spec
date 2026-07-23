# FCF Current State FCP 0090 A-Share Guojin QMT Local Terminal Liveness Evidence App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0090-A-SHARE-GUOJIN-QMT-LOCAL-TERMINAL-LIVENESS-EVIDENCE-APP-1

The immutable path-free terminal-liveness evidence is implemented, validated,
and merged to main. It observes local process image names in memory, reduces
them immediately to five registered Guojin QMT families, and retains no
unregistered process identity.

Validation evidence:

- isolated FCP-0090 tests: 12 passed
- affected A-share and governance tests: 530 passed
- all FCP tests: 1771 passed
- full pytest: 7108 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED before and after merge
- generated outputs: restored; no tracked generated changes remained

Contract SHA-256:
`c82466c987b415d5d78db0dba161fc1653b651d8caa642860ba5dda6772c097a`.
Reference evidence hash:
`73683bffb99cbb428c275ea8e07c85e0edf8e41177c9dcf949e6fca1afd2af17`.
Reference output SHA-256:
`366c02360c7192505a3d651e20c84d21b238e1188203a4a3443e9f2681c0ab6a`.
Observed snapshot SHA-256:
`072f841a38aa778b2646cdc0123a8a9f2c71d4c6c902e519d5ed8a756eeb02ba`.
Observed evidence hash:
`ce66a717ca3cf83795111d506b7817f829f749b6caba44cf59b793e9110bee07`.

Evidence commits:

- approval: `eb98cf5b3c3f541b8534d61832b2711cb97a6751`
- sidecar delivery: `512daa76126962bd54bb2fe4313aceb73df04dfa`
- main merge: `e1cabda50c2048b826d7571e2aeebf80932c844c`

The observed registered-local snapshot at 2026-07-23T00:57:11.436138Z
contained 372 process image names and zero matches for all registered QMT
families. The deterministic result is TERMINAL_NOT_OBSERVED. GAP-104 remains
RESEARCH_REQUIRED; entitlement and a read-only market-data probe remain
unproven.

No arbitrary process name, identifier, owner, session, command line,
executable path, window, account identifier, credential, market value, SDK
invocation, network, provider, realtime, promotion, product, P48, broker,
exchange, balance, position, order, execution, tag, release, or deployment
authority was created.
