# FCF Current State FCP 0054 BTC Perpetual Mark Index Liquidation Mechanics Evidence Registry App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Evidence commits:

- governance approval: `fce1b40ecebb5b50670a6e8315b95088b7befcd7`
- sidecar delivery: `746b81708457f79bf7973bd4f95ccf04c690adf2`
- main delivery merge: `ee94dc1973eb2dbd6c8db3cb8fa94b41e7c922d9`

Validation evidence:

- isolated FCP-0054 suite: 20 passed
- affected BTC liquidation-registry and governance suite: 532 passed
- all FCP suites: 960 passed
- full pytest: 6297 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- post-merge affected suite: 532 passed
- post-merge full pytest: 6297 passed
- post-merge `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

The registry binds exact FCP-0046 contract-entry lineage, preserves immutable
mark, index, bankruptcy, liquidation, partial-tier, insurance-fund, ADL, and
cascade-policy evidence, and resolves rules by half-open UTC effective time.
It grants no price, margin, liquidation, balance, position, PnL, fund, ADL,
selection, or execution authority.

GAP-098, GAP-100, GAP-101, and GAP-102 remain open and require registered
external evidence or later paper-only research. No acquisition, SDK, network,
credential, provider selection, raw repository retention, realtime, product,
P48, exchange, wallet, account, balance, position, order, execution, tag,
release, or deployment is authorized. No successor phase is selected.
