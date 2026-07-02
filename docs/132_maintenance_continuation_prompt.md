# FCF Final Archive Continuation Prompt

Date: 2026-07-02 12:08:58 +0800

Project: FCF / fcf-spec
Repository: https://github.com/wangshaoyuhaha/fcf-spec.git
Local path: ~/Desktop/fcf_phase1_spine
Branch: main
Mode: final archived, maintenance-only, paper-only

## Copy This Prompt Into A New Chat

We continue the FCF / fcf-spec project.

Do not restart from the beginning.
Do not change the project direction.
Do not open a new Phase unless explicitly requested.

Current true state:

- Phase 1 through Phase 12 completed
- Final Archive D1 through D7 completed
- Archive-D7 final archive closeout completed
- Post-archive maintenance records completed through docs/132_maintenance_continuation_prompt.md
- Latest verified full test result: 773 passed
- Project is now maintenance-only

Latest maintenance records:

- docs/128_maintenance_final_archive_health_check.md
- docs/129_maintenance_final_archive_export_summary.md
- docs/130_maintenance_operator_quickstart.md
- docs/131_maintenance_final_archive_index.md
- docs/132_maintenance_continuation_prompt.md

Required validation after any future maintenance change:

- python main.py
- python scripts/run_p12_final_delivery_package_summary.py
- python scripts/run_final_archive_acceptance_smoke.py
- python -m pytest -q

Safety boundary must remain preserved:

- no real exchange API
- no real API key storage
- no wallet private key access
- no real order placement
- no real account balance read
- no real position read
- no real execution success claim
- no real financial impact claim
- no CI secret configuration
- no production deployment
- no live auto-trading
- no operator review bypass
- no policy, risk, or safe_boundary bypass
- paper-only passed must not be interpreted as a real trading signal
- paper-only passed must not be interpreted as a real fill or execution

Response style required:

- I do not code.
- Give one complete Git Bash command block at a time.
- The command block must be directly copyable and runnable.
- Do not split commands into multiple code blocks.
- Keep explanations short.
- After I paste terminal output, summarize:
  - what passed
  - test count
  - elapsed time
  - commit hash
  - push result
  - whether repository is clean
  - what remains and estimated time
- If something fails, give only the minimum fix command.
- After successful tests, commit and push.
