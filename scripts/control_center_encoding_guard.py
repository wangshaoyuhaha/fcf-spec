from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List


DEFAULT_GUARDED_FILES: List[str] = [
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
]


def read_text_utf8_strict(path: str | Path) -> str:
    target = Path(path)
    return target.read_text(encoding="utf-8")


def check_utf8_readable(paths: Iterable[str | Path]) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for item in paths:
        target = Path(item)
        try:
            target.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            results[str(target)] = f"UTF8_DECODE_ERROR:{exc.start}:{exc.end}"
        except FileNotFoundError:
            results[str(target)] = "MISSING"
        else:
            results[str(target)] = "OK"
    return results


def assert_utf8_readable(paths: Iterable[str | Path]) -> None:
    results = check_utf8_readable(paths)
    bad = {name: status for name, status in results.items() if status != "OK"}
    if bad:
        details = "; ".join(f"{name}={status}" for name, status in sorted(bad.items()))
        raise ValueError(f"CONTROL_CENTER_ENCODING_GUARD_FAILED: {details}")


def write_text_utf8(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
