# FCF Current State FCP 0049 BTC Perpetual Fee Rebate Schedule Evidence Registry App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Evidence commits:

- governance approval: `18aa9d8174c8d36fd09ef3111cbcd66a09521daf`
- sidecar delivery: `c3b6b6e80c9fd561be9261b228645ddf2c0a39ef`
- main delivery merge: `018f02b3b6dc9edf66c36cedcfc5883a8ab51bf6`

Validation evidence:

- isolated FCP-0049 suite: 16 passed
- affected BTC fee and governance suite: 68 passed
- all FCP suites: 890 passed
- full pytest: 6227 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- post-merge affected suite: 68 passed
- generated runtime outputs: restored; no tracked generated changes remained

The registry preserves exact contract-bound fee and rebate schedule evidence and
fails closed on effective-time ambiguity. It grants no account-tier selection,
fee or rebate calculation, balance, position, PnL, liquidation, funding,
source, execution, or GAP authority. No acquisition, SDK, network, credential,
realtime, product, P48, wallet, account, balance, position, order, execution,
tag, release, or deployment is authorized. No successor phase is selected.
