# FCF Current State FCP 0048 BTC Perpetual Funding Method Schedule Evidence Registry App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Evidence commits:

- governance approval: `b6b02558045199f7626e70557f47890d495f7453`
- sidecar delivery: `6df22f37955c86ef3c883ad0e5e7f61132c56432`
- main delivery merge: `0ea3d923ea38c851a0a179e72b0529b5d304514a`

Validation evidence:

- isolated FCP-0048 suite: 16 passed
- affected BTC funding and governance suite: 84 passed
- all FCP suites: 874 passed
- full pytest: 6211 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- post-merge affected suite: 84 passed
- generated runtime outputs: restored; no tracked generated changes remained

The registry preserves exact contract-bound funding-rule evidence and fails
closed on effective-time ambiguity. It grants no funding-rate, payment,
balance, position, PnL, liquidation, fee, source, execution, or GAP authority.
No acquisition, SDK, network, credential, realtime, product, P48, wallet,
account, balance, position, order, execution, tag, release, or deployment is
authorized. No successor phase is selected.
