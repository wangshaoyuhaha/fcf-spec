# FCF Execution Safety Protocol

## Status

MANDATORY DEVELOPMENT TOOLING PROTOCOL

## Purpose

This protocol prevents workflow damage caused by shell parsing,
native-command stderr handling, network instability, repeated execution,
line-ending conversion, and unsafe cleanup.

It governs development tooling only.

It does not modify P1-P47 frozen Core behavior.

## Command result authority

External command success is determined only by its process exit code.

Standard output and standard error must be captured separately.

Text written to standard error is not automatically a failure.

Examples:

- stderr warning plus exit code 0: SUCCESS WITH WARNING
- empty stderr plus nonzero exit code: FAILURE
- stdout success text plus nonzero exit code: FAILURE

## Local preflight

Development preflight is local-only.

Required checks:

- expected branch
- expected HEAD
- expected changed-path set
- clean repository when required

Forbidden development preflight:

- git ls-remote
- remote API dependency
- network availability as a write gate
- provider health as a local write gate

## Network operations

Network operations occur only after local validation and local commit.

Push rules:

- maximum three attempts
- bounded delay
- preserve the local commit after failure
- do not rewrite files after push failure
- do not create another commit after push failure
- resume with push only

## Safe process runner

All future generated PowerShell must use:

scripts/fcf_safe_runner.ps1

Required functions:

- Invoke-FcfProcess
- Invoke-FcfProcessWithRetry
- Get-FcfRepositoryState
- Assert-FcfRepositoryState
- Assert-FcfChangedPaths
- Write-FcfTextFile
- Write-FcfCheckpoint
- Read-FcfCheckpoint

## Checkpoints

Long workflows must write an explicit checkpoint after each completed
boundary.

Suggested boundaries:

1. files written
2. targeted validation passed
3. local commit created
4. push completed
5. main merge created
6. full validation passed
7. authoritative documents synchronized

A resumed workflow must continue from the last completed checkpoint.

It must not repeat earlier writes or commits.

## Line endings

Generated text files must use Write-FcfTextFile.

Required defaults:

- Python: LF
- Markdown: LF
- JSON: LF
- YAML: LF
- PowerShell: CRLF on the Windows operator workstation

Temporary Git configuration overrides are forbidden.

Forbidden examples:

- git -c core.autocrlf=false add
- git -c core.autocrlf=true add
- changing global core.autocrlf during a phase

Repository-wide line-ending normalization requires a separate audit.

## Staging

Stage only explicit expected paths.

Before commit:

- verify exact staged path set
- verify no untracked files
- run git diff --cached --check
- inspect staged numstat
- reject unexpected whole-file rewrites

## Cleanup

Forbidden cleanup:

- git clean -fd
- git clean -xdf
- git reset --hard
- git restore against the repository root
- recursive deletion of the repository
- wildcard cleanup outside an approved temporary directory

Generated runtime files may be restored only through an explicit allowlist.

## Workflow separation

A development phase must be separated into these boundaries:

### Boundary A

- local preflight
- write files
- targeted validation
- no network
- no commit
- no push

### Boundary B

- inspect Boundary A log
- stage explicit files
- cached diff validation
- local commit
- bounded push retries

### Boundary C

- main merge
- targeted validation
- full pytest
- run_all_checks
- explicit generated-file restoration
- push main

### Boundary D

- authoritative document synchronization
- validation
- commit
- push

A failure at one boundary must not repeat prior completed boundaries.

## Required self-tests

The safe runner must verify:

- stderr warning with exit code 0 remains successful
- nonzero exit code remains failed
- retry recovers from one transient failure
- output and error streams remain separate
- line-ending normalization is deterministic
- repeated writes are idempotent
- checkpoints can be read after writing

## Permanent restrictions

This tooling must not:

- mutate frozen Core
- create P48
- invoke models
- execute Prompts
- activate automatic routing
- access trading credentials
- access balances or positions
- access wallet keys
- place orders
- create releases
- create tags
- deploy
