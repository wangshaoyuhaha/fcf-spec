import csv
import json
from pathlib import Path
from typing import Any


def load_paper_batch_from_json(path: str) -> list[dict[str, Any]]:
    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        items = data.get("items")
    else:
        items = data

    if not isinstance(items, list):
        raise ValueError("json batch must be a list or contain items list")

    return items


def load_paper_batch_from_csv(path: str) -> list[dict[str, Any]]:
    file_path = Path(path)

    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError("csv batch must not be empty")

    payloads: list[dict[str, Any]] = []
    for row in rows:
        payloads.append({
            "symbol": row.get("symbol", ""),
            "price": float(row.get("price", "0")),
            "reference_price": float(row.get("reference_price", "0")),
        })

    return payloads


def load_paper_batch_file(path: str, file_format: str = "auto") -> list[dict[str, Any]]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    selected_format = file_format.lower()
    if selected_format == "auto":
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            selected_format = "json"
        elif suffix == ".csv":
            selected_format = "csv"
        else:
            raise ValueError("unsupported batch file extension")

    if selected_format == "json":
        return load_paper_batch_from_json(str(file_path))

    if selected_format == "csv":
        return load_paper_batch_from_csv(str(file_path))

    raise ValueError("unsupported batch file format")
