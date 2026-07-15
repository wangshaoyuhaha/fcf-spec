# FCF Browser Product Console Operator Guide

## Fast start on Windows

Double-click `START_FCF_BROWSER_CONSOLE.cmd` in the repository root.

The launcher validates all registered starter artifacts, binds only to
`127.0.0.1:8765`, opens the default browser, and keeps the local console active
until the terminal window is closed or `Ctrl+C` is pressed.

The default pages display `DEMONSTRATION_ONLY`. They demonstrate the product
with A-share, US-equity, and BTC examples. They are not current market data,
investment advice, live signals, a real portfolio, or execution instructions.

## Preflight only

Run this command to validate the package and port without starting the server:

```powershell
python scripts/run_browser_product_console_runtime.py --check
```

## Start without opening a browser

```powershell
python scripts/run_browser_product_console_runtime.py --no-browser
```

Then open `http://127.0.0.1:8765/` manually.

## Use a custom registered artifact index

```powershell
python scripts/run_browser_product_console_runtime.py --allowed-root C:\path\to\registered-root --index index.json
```

Both custom arguments are required together. Every indexed artifact must stay
inside the allowed root and match its registered SHA-256 digest.

## Common startup guidance

- `FCF-LAUNCH-PORT-UNAVAILABLE`: stop the other local service or add a
  different port such as `--port 8766`.
- `FCF-LAUNCH-ARTIFACT-MISSING`: restore the registered package or choose a
  valid custom root and index.
- `FCF-LAUNCH-ARTIFACT-INTEGRITY`: restore the original artifact. Never bypass
  the registered digest.
- `FCF-LAUNCH-ARTIFACT-REGISTRATION`: verify the index schema, paths, artifact
  types, and correlation ID.

## Product authority

The console is a paper-only, read-only presentation surface. The Deterministic
Engine remains calculation authority, Registered Evidence remains evidence
authority, AI remains advisory, and Operator review remains mandatory. The
console has no broker, exchange, credential, account, balance, position,
wallet, order, or execution path.
