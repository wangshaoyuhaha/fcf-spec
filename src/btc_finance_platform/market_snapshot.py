from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class PaperMarketSnapshot:
    symbol: str
    price: float
    source: str = "manual_paper_input"
    timestamp_utc: str = ""
    paper_only: bool = True
    real_exchange_api: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not data["timestamp_utc"]:
            data["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        return data


def create_paper_market_snapshot(symbol: str, price: float) -> dict[str, Any]:
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol is required")

    if price <= 0:
        raise ValueError("price must be positive")

    snapshot = PaperMarketSnapshot(
        symbol=symbol.upper(),
        price=float(price),
    )

    data = snapshot.to_dict()

    if data["paper_only"] is not True:
        raise AssertionError("market snapshot must remain paper-only")

    if data["real_exchange_api"] is not False:
        raise AssertionError("market snapshot must not use real exchange API")

    return data
