# FCP-0106 QMT Live Operator Review Runbook

## Preconditions

1. Use the ordinary Guojin QMT terminal.
2. Log in during an A-share trading session.
3. Keep `FCF_READ_ONLY_QUOTE_BRIDGE` stopped until the local probe is waiting.
4. Confirm `C:\FCF_QMT_BRIDGE\incoming` is a regular local directory and contains
   no event from an earlier or simulated session.
5. Confirm the repository is on the registered FCP-0106 branch with a clean
   worktree.

## Start The Local Probe

Run this command from the repository root:

```text
python scripts/run_fcp_0106_qmt_live_operator_review_probe.py --spool-root C:\FCF_QMT_BRIDGE\incoming --timeout-seconds 600 --poll-milliseconds 250
```

After the probe is waiting, run `FCF_READ_ONLY_QUOTE_BRIDGE` in QMT. Stop the
QMT strategy immediately after the probe exits.

## Exit Meanings

- Exit `0`: one registered fresh event passed schema, integrity, identity,
  ordering, receive-clock, and market-clock gates. The JSON output is a
  value-free candidate evidence packet pending Operator review.
- Exit `1`: the probe failed closed. Do not treat any file as realtime
  evidence. Preserve the error text for diagnosis.
- Exit `2`: no registered fresh event arrived within the bounded wait. Do not
  claim realtime acceptance.

## Required Success Fields

The successful JSON must contain:

- `candidate_status` equal to `OPERATOR_REVIEW_REQUIRED`;
- `realtime_gate_passed` equal to `true`;
- `read_only` equal to `true`;
- `operator_review_required` equal to `true`;
- `receive_age_ms` between `-2000` and `10000`;
- `event_age_ms` between `-2000` and `10000`;
- all authority fields equal to `false`;
- exact registration, event, snapshot, and evidence hashes.

The packet does not contain price or volume values. It does not promote market
data, calibrate native QMT volume, approve itself, access an account, or create
an order or execution path.
