# Future Learning Roadmap Anchor

Status: planned, not implemented

Purpose:
- Record the future self-learning direction in the project skeleton.
- Keep the current development order unchanged.
- Do not implement autonomous learning or trading now.

Current rule:
- Continue P7 in order first.
- Learning is reserved for later phases.
- All learning must remain paper-only, auditable, versioned, and operator-reviewed.

Allowed future learning capabilities:
- paper-only analysis memory
- operator feedback dataset
- paper outcome tracking
- backtesting
- calibration of risk score and regime performance
- offline model or parameter training
- model version registry
- strategy version comparison
- learning result reports
- UI display of learning history and calibration results

Forbidden:
- no real exchange API
- no real brokerage API
- no real API key
- no wallet private key
- no real order
- no real execution
- no real balance
- no real position
- no real money impact
- no automatic live trading
- no bypass of operator review

Future phase mapping:
- P8: learning memory, feedback dataset, paper outcome tracking
- P9: backtest, calibration, regime/risk score evaluation
- P10: model registry, strategy versioning, offline paper model update
- P11: UI pages for operator console, reports, learning memory, calibration
- P12: final archive and delivery package

Safe learning loop:
- observe
- analyze
- operator review
- record feedback
- backtest and calibrate
- generate new paper model version
- human approval

Unsafe loop explicitly forbidden:
- observe
- self-learn
- self-trade

Architecture note:
- BTC remains the first implementation line.
- The broader target remains a general FCF-style finance platform for stocks and other markets.
- Future learning belongs to the paper-only intelligence layer, not to real execution.
