# FCF Current State FCP 0075 A-Share External Candidate Daily Corpus Quality Quarantine Evidence App 1 Delivered

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

The bounded local scanner reads an Operator-supplied candidate daily CSV
corpus and emits path-free immutable structural, value-quality, coverage,
adjustment-ambiguity, provenance-gap, and rights-risk evidence.

The scanned candidate contained 5,607 files, 14,992,089 parseable rows, and
2,979,854,382 bytes. It exposed 84 malformed rows, 13 invalid OHLC rows, and
250 files with a terminal date earlier than the corpus latest terminal date.
The 84 malformed rows were independently traced to missing historical amount
fields. Raw rows, file names, and local paths remain outside Git.

The evidence remains `QUARANTINED_UNVERIFIED_EXTERNAL_CANDIDATE`. It cannot
promote rows, calculate factors, create training labels, select a provider, or
establish provider, license, revision, corporate-action, adjustment-factor,
trading-status, calendar, point-in-time, or Registered Evidence authority.

No acquisition, SDK, network, credential, realtime, broker, exchange,
account, balance, position, order, execution, product phase, P48, tag, release,
or deployment path is created.
