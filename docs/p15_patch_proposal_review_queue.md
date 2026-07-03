# P15-D8 Patch Proposal Review Queue

Status: completed

Purpose:
- index patch proposals created by the sandbox
- keep all proposed changes under human review
- prevent silent model or parameter mutation

Queue fields:
- proposal id
- source module
- reason
- proposed change summary
- expected benefit
- risk note
- review status
- operator decision

Rules:
- patch proposal is not patch application
- no auto-merge
- no auto-deploy
- no parameter auto-update
- operator approval is required
