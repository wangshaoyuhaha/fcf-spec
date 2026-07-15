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

## Windows pytest temporary roots

On Windows, pytest temporary-root arguments must preserve drive and path
separators exactly.

Required behavior:

- prefer setting `TEMP` and `TMP` to a verified writable scratch directory
  outside the repository
- when `--basetemp` is required, pass it as a direct process argument
- validate the absolute scratch parent before pytest starts
- create and remove a probe directory before the test run
- verify after the run that pytest created no repository-root temporary path
- never pass an absolute Windows `--basetemp` value through
  `PYTEST_ADDOPTS`
- never construct a pytest temporary path by shell string concatenation that
  can remove backslashes or a drive separator

If a test intentionally creates an inaccessible ACL state, cleanup must:

- validate the exact absolute target and its expected parent
- restore only allowlisted tracked generated outputs
- use the narrowest available ACL recovery
- request an explicit UAC confirmation only for that exact generated target
- never hide the target with `.gitignore` or an exclude rule
- never commit while a generated repository path remains unresolved

## Recoverable environment failures

A shell, temporary-directory, ACL, quoting, or transient network failure is
not a project-code failure unless a project assertion, integrity check, or
safety contract also fails.

After the first actual exception is identified, the workflow may repair the
execution mechanism and continue from the last verified checkpoint when:

- project changes remain exactly within the expected path set
- completed targeted tests remain valid
- no safety or integrity assertion failed
- no unclassified dirty file exists
- commit and push remain blocked until required cleanup succeeds

Verified project changes must not be rolled back solely because a later
recoverable execution-environment operation failed.

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

## Continuous execution authority

The development workflow must continue from the last verified checkpoint
after a recoverable environment problem.

Recoverable problems include:

- shell quoting or interpolation errors
- tool-access failure on an unrelated ignored path
- temporary-root creation or cleanup failure
- Git stat-only working-tree reports
- transient network or remote push failure
- stderr warnings with native exit code zero
- sandbox or ACL denial that can be repaired through an exact-path operation

A recoverable problem does not invalidate completed code writes, tests,
commits, pushes, or merges.

The workflow stops only when there is a real:

- project assertion failure
- test failure
- integrity failure
- safety-boundary failure
- unexpected changed path
- unresolved generated repository artifact
- unclassified working-tree difference

## Native command sequence guard

PowerShell does not stop a semicolon-separated sequence merely because a
native command returned a nonzero exit code.

Every required native command must therefore use one of these mechanisms:

- Invoke-FcfRequiredProcess
- Assert-FcfProcessSucceeded
- an immediate explicit `$LASTEXITCODE` check followed by `exit` or
  `throw`

A later successful command must never hide an earlier native failure.

Validation, staging, commit, merge, and push must not appear in one unguarded
semicolon-separated chain.

## Git stat-only state repair

When Git reports a modified path but both `git diff -- <path>` and the
content-hash comparison show no content difference:

1. verify the exact single path
2. compare the working-tree content hash with the index blob hash
3. refresh the Git index
4. if the stat-only report persists, stage only that exact path
5. verify the cached diff is empty
6. verify the working tree is clean

This operation repairs metadata only. It must not replace, restore, or rewrite
the file.

## Tool-access fallback

A tool-access failure on an ignored or inaccessible path must not stop
repository inspection.

Required fallback order:

1. use `git ls-files` for tracked repository discovery
2. use exact known paths
3. exclude the inaccessible unrelated path from read-only traversal
4. request exact-path elevation only when the path is required

Never perform repository-wide recursive ACL or cleanup operations.

## Authority synchronization checkpoint

Every phase must record its approved order in all active authority files
before implementation starts.

After merge, the phase is incomplete until all active authority files contain:

- completed phase identity
- D6 commit
- main merge commit
- validation baseline
- next phase status
- permanent restrictions

The active authority files are:

- docs/FCF_PROJECT_CONTROL_CENTER.md
- docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md
- docs/HANDOFF_PROMPT.md
- FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
- FCF_NEW_WINDOW_CHAT_PROMPT.md

The active authority synchronization guard must pass before final push.
