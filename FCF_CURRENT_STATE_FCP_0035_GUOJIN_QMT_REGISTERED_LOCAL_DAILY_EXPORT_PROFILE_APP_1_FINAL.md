# FCF Current State FCP 0035 Guojin QMT Registered Local Daily Export Profile App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Evidence commits:

- governance approval: `7970b64974747f9b48ea49b76caefc39faf69d73`
- sidecar delivery: `c72505c68155507ae7aef512a785aeb007ea0ba4`
- main delivery merge: `c9ce59fee3cf80644c5e18d9194011203b098c50`

Validated result:

- FCP-0035 isolated suite: 18 passed
- affected A-share bridge and governance suite: 81 passed
- FCP governance stage suite: 697 passed
- full pytest: 6034 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- post-merge affected suite: 81 passed
- generated runtime outputs: restored; no tracked generated changes remained

The Guojin QMT registered local daily-export profile now preserves exact source
bytes, explicit instrument identity, ISO date normalization, 100-share lot
conversion, deterministic FCP-0019 bridge bytes, and additive front-adjustment
reference evidence without fabricating factor authority. Observed incomplete
coverage, MiniQMT entitlement, adjustment-factor lineage, trading status, and
point-in-time supplements remain visible research gaps. Real export bytes stay
outside the repository. No SDK, network, credential, provider selection,
account, balance, position, order, execution, realtime, product phase, P48,
tag, release, or deployment authority is added. No successor phase is selected.
