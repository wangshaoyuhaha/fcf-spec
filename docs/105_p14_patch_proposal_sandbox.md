# P14-D31 To P14-D33 Patch Proposal Sandbox

Status: completed after validation.

Scope:
- P14-D31: define paper-only patch proposal object
- P14-D32: validate patch proposal safety gate
- P14-D33: regression tests for no-auto-apply boundary

Purpose:
Allow AI to design patch proposals while preventing automatic code changes, commits, merges, releases, or deployment.

Allowed:
- generate patch proposal
- list target files
- list test plan
- list risk notes
- write local proposal record

Forbidden:
- auto-apply patches
- auto-commit
- auto-merge
- auto-release
- auto-deploy
- target exchange API
- target brokerage API
- use API keys
- use wallet private keys
- create real orders
- execute real trades
- affect real balances or positions
- affect real money

Operator review and scenario review remain required.
