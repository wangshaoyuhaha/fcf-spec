# FCF Phase 1 Spine MVP

Financial Cognitive Framework Phase 1 reference implementation.

This version does **not** connect real exchanges, does **not** place real orders, and does **not** use LLMs.
It only verifies the golden spine:

Mock Market → Perception → Regime Detection → Cognitive Unit → Governor → Decision Proposal → Simulation → Meta → Shadow Execution → SQLite Audit.

## Run

```bash
python main.py
```

The script creates:

```text
fcf_events.db
```

and writes the full event chain with one shared `correlation_id`.

## Safety

Default execution mode is `SHADOW`.
No real capital is touched.
