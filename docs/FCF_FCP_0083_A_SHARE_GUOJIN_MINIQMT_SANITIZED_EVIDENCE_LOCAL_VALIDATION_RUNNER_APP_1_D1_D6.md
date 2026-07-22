# FCF FCP 0083 A-Share Guojin MiniQMT Sanitized Evidence Local Validation Runner App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Runner Boundary

Define one read-only local runner that accepts an artifact path, artifact ID,
SHA-256, byte length, and as-of UTC. No provider client is imported or invoked.

## D2 Exact Local Read

Require an existing regular non-symlink file, enforce the FCP-0082 byte bound,
read bytes once, and delegate exact length, digest, ASCII, schema, duplicate,
secret-key, and semantic validation to FCP-0082.

## D3 Deterministic Review Evaluation

Delegate evaluation to FCP-0082 and preserve only INSUFFICIENT_EVIDENCE or
OPERATOR_REVIEW_ELIGIBLE with all non-authorizing fields unchanged.

## D4 Canonical Read-Only Output

Emit canonical ASCII JSON to standard output. Do not rewrite, copy, cache,
register, promote, delete, or otherwise mutate the source artifact.

## D5 Fail-Closed CLI

Reject incomplete arguments, unsafe identities, malformed UTC or SHA-256,
missing, directory, symlink, oversized, secret-bearing, or invalid evidence.
Errors reveal no source bytes or secret values.

## D6 Validation And Closeout

Run isolated, affected A-share evidence, all FCP, full pytest, and all-checks
suites; restore generated outputs; verify exact changed files, ASCII, hashes,
and `git diff --check`; then commit, push, merge, revalidate, and synchronize.
