import hashlib
import json
import os
import re
import time
from decimal import Decimal, InvalidOperation


BRIDGE_ID = "fcf-qmt-internal-read-only-market-bridge-v1"
SCHEMA_VERSION = "fcf-qmt-quote-v1"
SOURCE_KIND = "GUOJIN_QMT_INTERNAL_QUOTE"
VOLUME_UNIT = "QMT_NATIVE_UNCALIBRATED"
CONFIG_NAME = "fcf_qmt_bridge_config.json"
SYMBOL_PATTERN = re.compile(r"^[0-9]{6}\.(?:SH|SZ|BJ)$")
REQUIRED_QUOTE_KEYS = (
    "amount",
    "high",
    "lastPrice",
    "low",
    "open",
    "time",
    "volume",
)
_STATE = {
    "config": None,
    "last_emit_ns": {},
    "sequences": {},
    "subscriptions": [],
}


def _config_candidates():
    candidates = []
    script_path = globals().get("__file__")
    if isinstance(script_path, str) and script_path:
        candidates.append(
            os.path.join(os.path.dirname(os.path.abspath(script_path)), CONFIG_NAME)
        )
    working_dir = os.path.abspath(os.getcwd())
    candidates.extend(
        (
            os.path.join(working_dir, CONFIG_NAME),
            os.path.join(working_dir, "python", CONFIG_NAME),
            os.path.join(os.path.dirname(working_dir), "python", CONFIG_NAME),
        )
    )
    unique = []
    for candidate in candidates:
        normalized = os.path.abspath(candidate)
        if normalized not in unique:
            unique.append(normalized)
    return tuple(unique)


def _canonical(payload):
    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _decimal_text(value, name, positive):
    if isinstance(value, bool):
        raise ValueError(name + " must be numeric")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(name + " must be numeric")
    if not parsed.is_finite():
        raise ValueError(name + " must be finite")
    text = format(parsed, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text == "-0":
        text = "0"
    if not text or text.startswith("-") or (positive and text == "0"):
        raise ValueError(name + " is outside the safe range")
    return text


def _load_config():
    config_path = next(
        (
            candidate
            for candidate in _config_candidates()
            if os.path.isfile(candidate)
            and not os.path.islink(candidate)
            and not candidate.startswith("\\\\")
        ),
        None,
    )
    if config_path is None:
        raise ValueError("bridge config is not in a registered local path")
    with open(config_path, "r", encoding="ascii") as stream:
        config = json.load(stream)
    if tuple(sorted(config)) != (
        "bridge_root",
        "max_events_per_second",
        "period",
        "symbols",
    ):
        raise ValueError("bridge config does not match the closed schema")
    root = os.path.abspath(config["bridge_root"])
    if root.startswith("\\\\") or os.path.islink(root):
        raise ValueError("bridge_root must be a regular local path")
    symbols = tuple(config["symbols"])
    if (
        symbols != tuple(sorted(set(symbols)))
        or not symbols
        or len(symbols) > 64
        or any(not SYMBOL_PATTERN.fullmatch(item) for item in symbols)
    ):
        raise ValueError("symbols are outside the closed registry")
    if config["period"] != "tick":
        raise ValueError("period must be tick")
    rate = config["max_events_per_second"]
    if type(rate) is not int or not 1 <= rate <= 10:
        raise ValueError("max_events_per_second is outside the safe range")
    spool = os.path.join(root, "incoming")
    os.makedirs(spool, exist_ok=True)
    if os.path.islink(spool):
        raise ValueError("incoming spool must not be a link")
    return {
        "bridge_root": root,
        "max_events_per_second": rate,
        "period": "tick",
        "spool": spool,
        "symbols": symbols,
    }


def _quote_payload(symbol, quote, sequence, received_at_ms):
    if not isinstance(quote, dict):
        raise ValueError("quote must be a mapping")
    if any(key not in quote for key in REQUIRED_QUOTE_KEYS):
        raise ValueError("quote is missing a required market field")
    event_time_ms = int(quote["time"])
    if event_time_ms <= 0:
        raise ValueError("quote time must be positive")
    payload = {
        "amount_cny": _decimal_text(quote["amount"], "amount", False),
        "bridge_id": BRIDGE_ID,
        "event_time_ms": event_time_ms,
        "high": _decimal_text(quote["high"], "high", True),
        "last": _decimal_text(quote["lastPrice"], "lastPrice", True),
        "low": _decimal_text(quote["low"], "low", True),
        "open": _decimal_text(quote["open"], "open", True),
        "previous_close": _decimal_text(
            quote.get("lastClose", quote["lastPrice"]),
            "lastClose",
            True,
        ),
        "received_at_ms": received_at_ms,
        "schema_version": SCHEMA_VERSION,
        "sequence": sequence,
        "source_kind": SOURCE_KIND,
        "symbol": symbol,
        "volume_native": _decimal_text(quote["volume"], "volume", False),
        "volume_unit": VOLUME_UNIT,
    }
    payload["event_hash"] = hashlib.sha256(_canonical(payload)).hexdigest()
    return payload


def _write_event(config, payload):
    symbol_token = payload["symbol"].replace(".", "-")
    name = "quote-{0}-{1:013d}-{2:012d}.json".format(
        symbol_token,
        payload["received_at_ms"],
        payload["sequence"],
    )
    target = os.path.join(config["spool"], name)
    temporary = target + ".tmp-{0}".format(os.getpid())
    raw = _canonical(payload)
    if len(raw) > 4096:
        raise ValueError("quote event exceeds the safe byte limit")
    with open(temporary, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, target)
    return target


def _on_quote(datas):
    config = _STATE["config"]
    if config is None or not isinstance(datas, dict):
        return
    now_ns = int(time.monotonic() * 1_000_000_000)
    received_at_ms = int(time.time() * 1000)
    minimum_ns = 1_000_000_000 // config["max_events_per_second"]
    for symbol in config["symbols"]:
        quote = datas.get(symbol)
        if not isinstance(quote, dict):
            continue
        previous_ns = _STATE["last_emit_ns"].get(symbol, 0)
        if now_ns - previous_ns < minimum_ns:
            continue
        sequence = _STATE["sequences"].get(symbol, 0) + 1
        payload = _quote_payload(symbol, quote, sequence, received_at_ms)
        _write_event(config, payload)
        _STATE["last_emit_ns"][symbol] = now_ns
        _STATE["sequences"][symbol] = sequence


def init(ContextInfo):
    config = _load_config()
    ContextInfo.set_universe(list(config["symbols"]))
    subscriptions = []
    for symbol in config["symbols"]:
        subscription = ContextInfo.subscribe_quote(
            symbol,
            period=config["period"],
            dividend_type="none",
            result_type="dict",
            callback=_on_quote,
        )
        if type(subscription) is not int or subscription <= 0:
            raise RuntimeError("QMT quote subscription failed")
        subscriptions.append(subscription)
    _STATE["config"] = config
    _STATE["last_emit_ns"] = {}
    _STATE["sequences"] = {}
    _STATE["subscriptions"] = subscriptions


def handlebar(ContextInfo):
    return None
