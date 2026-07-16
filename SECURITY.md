# Security Policy

FCF is local-only and paper-only. Report suspected vulnerabilities privately to
the repository owner. Do not include credentials, account data, wallet data, or
real financial information in a report or reproduction.

Security invariants:

- services bind exactly to `127.0.0.1`
- POST requests require an exact loopback Origin
- registered artifacts remain inside verified allowed roots
- model, training, financial, and real-world execution remain disabled
- Operator action receipts do not execute backend actions

No public deployment or real-money use is supported.
