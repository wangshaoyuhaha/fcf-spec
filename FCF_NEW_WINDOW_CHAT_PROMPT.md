You are continuing the FCF / Financial Cognitive Framework project.

Project:
FCF / Financial Cognitive Framework
Repository: wangshaoyuhaha/fcf-spec
Local path: C:\Users\Admin\Desktop\btc_finance_platform
Branch: main

Language:
Reply in Chinese.
Keep responses short and direct.
For PowerShell, provide complete copyable commands.
Do not ask the user to manually open files.
Prefer PowerShell for file writes.
At each phase end, report commit, push, validation, and git status.
Do not tag, release, or deploy without explicit approval.

Current latest true state:
ARCHIVE-CORRELATION-ROLLUP-APP-1 is completed, merged into main, validated, pushed, and clean.

Latest main merge commit:
59ba8e7 merge ARCHIVE-CORRELATION-ROLLUP-APP-1 into main

Final sidecar commit:
fb05e00 fix ARCHIVE-CORRELATION-D6 final handoff tests

Validation:
python scripts/run_all_checks.py = ALL CHECKS PASSED
python -m pytest -q = 2002 passed

git status:
clean

origin/main:
synced

no tag / no release / no deploy

Project positioning:
FCF is a local multi-asset financial research governance platform.
It is not BTC-only.
It is not a trading execution system.

Core architecture:
P1-P47 core is frozen.
No P48.
New capability must use sidecar extension.
Preserve core frozen + sidecar extension.
Preserve one-way dependency.
No core mutation.

Latest completed sidecar purpose:
ARCHIVE-CORRELATION-ROLLUP-APP-1 upgrades correlation_id from passive field preservation into a read-only full-chain evidence index.

It indexes existing chain links:
data_snapshot, candidate, ai_explanation, ui_packet, review_packet, archive_packet, handoff, final_state.

It only marks:
COMPLETE, INCOMPLETE, STALE, UNRESOLVED.

It must not:
auto-pass, auto-fill correlation_id, backfill evidence, generate placeholder review, create UI dashboard panel, touch core, create P48.

Safety boundary:
paper-only / local-only / read-only / sidecar-only / operator review required.

Strictly forbidden:
real trading
real execution
broker/exchange API
API key
wallet private key
real account
real position
buy/sell/order
automatic position sizing
automatic portfolio action
profit guarantee
tag
release
deploy

Next step:
Return to control center planning and approve the next sidecar only after read-only verification.
