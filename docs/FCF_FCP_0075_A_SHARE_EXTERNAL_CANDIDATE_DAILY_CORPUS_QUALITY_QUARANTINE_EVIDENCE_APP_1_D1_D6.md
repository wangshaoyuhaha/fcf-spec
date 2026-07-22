# FCF FCP 0075 A-Share External Candidate Daily Corpus Quality Quarantine Evidence App 1 D1-D6

Status: VALIDATED_PENDING_MERGE

## D1 Closed Quarantine Contract

Register the closed schema, evidence identity, quarantine status, provenance
gaps, rights risk, and non-authorizing promotion flags.

## D2 Deterministic Read-Only Scanner

Stream local CSV bytes in stable file-name order, hash every candidate file,
and emit one path-free manifest fingerprint without retaining raw rows in Git.

## D3 Structural And Value Quality Evidence

Measure file, market, byte, row, header, filename, malformed-row, code, date,
OHLC, numeric, return, volume, and adjustment-ratio findings.

## D4 Coverage And Adjustment Ambiguity

Preserve date boundaries, latest and stale terminal counts, and adjustment
ratio observations without inferring completeness or official factor lineage.

## D5 Actual Quarantine Evidence

The read-only scan observed 5,607 files, 14,992,089 parseable rows, and
2,979,854,382 bytes. It found 84 rows with missing historical amount values,
13 invalid OHLC rows, and 250 stale-terminal files. The candidate remains
quarantined because all eight mandatory authority gaps remain unresolved.

## D6 Validation And Closeout

Run isolated, all-FCP, full-pytest, all-checks, generated-output, exact-file,
ASCII, and diff validation before merge and final synchronization.

Validation evidence:

- isolated FCP-0075 suite: 22 passed
- affected governance suite: 43 passed
- all FCP suites: 1452 passed
- full pytest: 6789 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked generated delta
- exact changed files and ASCII scope verified
- `git diff --check`: passed
