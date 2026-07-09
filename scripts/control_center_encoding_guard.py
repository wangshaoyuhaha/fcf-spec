from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


DEFAULT_GUARDED_FILES: List[str] = [
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
]

FINAL_AUDIT_FILES: List[str] = [
    "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md",
]


@dataclass(frozen=True)
class GuardedFileRecord:
    path: str
    file_kind: str
    exists: bool
    encoding_status: str
    write_policy: str
    safety_scope: str


@dataclass(frozen=True)
class EncodingProbeRecord:
    path: str
    exists: bool
    byte_size: int
    strict_utf8_status: str
    has_utf8_bom: bool
    newline_style: str
    guard_status: str


def _as_posix(path: str | Path) -> str:
    return Path(path).as_posix()


def read_text_utf8_strict(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


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


def classify_guarded_file(path: str | Path) -> str:
    normalized = _as_posix(path)
    name = Path(normalized).name
    if normalized == "docs/FCF_PROJECT_CONTROL_CENTER.md":
        return "CONTROL_CENTER"
    if name == "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md":
        return "BACKEND_HANDOFF"
    if name == "FCF_NEW_WINDOW_CHAT_PROMPT.md":
        return "NEW_WINDOW_PROMPT"
    if name == "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md":
        return "FINAL_AUDIT"
    if name.startswith("FCF_CURRENT_STATE_") and name.endswith(".md"):
        return "FINAL_CURRENT_STATE"
    return "GOVERNANCE_DOCUMENT"


def discover_final_current_state_files(root: str | Path = ".") -> List[str]:
    base = Path(root)
    return sorted(_as_posix(item.relative_to(base)) for item in base.glob("FCF_CURRENT_STATE_*.md") if item.is_file())


def discover_guarded_files(root: str | Path = ".") -> List[str]:
    candidates: List[str] = []
    candidates.extend(DEFAULT_GUARDED_FILES)
    candidates.extend(FINAL_AUDIT_FILES)
    candidates.extend(discover_final_current_state_files(root))

    unique: List[str] = []
    seen = set()
    for item in candidates:
        normalized = _as_posix(item)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return unique


def build_guard_registry(root: str | Path = ".") -> List[GuardedFileRecord]:
    base = Path(root)
    records: List[GuardedFileRecord] = []

    for relative_path in discover_guarded_files(base):
        target = base / relative_path
        status = check_utf8_readable([target])[str(target)]
        records.append(
            GuardedFileRecord(
                path=relative_path,
                file_kind=classify_guarded_file(relative_path),
                exists=target.exists(),
                encoding_status=status,
                write_policy="UTF8_LF_ONLY",
                safety_scope="PAPER_ONLY_LOCAL_ONLY_READ_ONLY_SIDECAR_ONLY",
            )
        )

    return records


def summarize_guard_registry(records: Iterable[GuardedFileRecord]) -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for record in records:
        summary[record.encoding_status] = summary.get(record.encoding_status, 0) + 1
    return summary


def assert_guard_registry_ok(records: Iterable[GuardedFileRecord]) -> None:
    bad = [record for record in records if record.encoding_status != "OK"]
    if bad:
        details = "; ".join(f"{record.path}={record.encoding_status}" for record in sorted(bad, key=lambda item: item.path))
        raise ValueError(f"CONTROL_CENTER_ENCODING_REGISTRY_FAILED: {details}")


def detect_newline_style(raw: bytes) -> str:
    if not raw:
        return "EMPTY"
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    cr = raw.count(b"\r") - crlf

    if cr > 0:
        return "MIXED_OR_CR"
    if crlf > 0 and crlf == lf:
        return "CRLF"
    if crlf > 0 and lf > crlf:
        return "MIXED"
    if lf > 0:
        return "LF"
    return "NO_NEWLINE"


def probe_encoding_file(path: str | Path) -> EncodingProbeRecord:
    target = Path(path)
    if not target.exists():
        return EncodingProbeRecord(
            path=str(target),
            exists=False,
            byte_size=0,
            strict_utf8_status="MISSING",
            has_utf8_bom=False,
            newline_style="UNKNOWN",
            guard_status="BLOCK",
        )

    raw = target.read_bytes()
    strict_status = check_utf8_readable([target])[str(target)]
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    newline_style = detect_newline_style(raw)

    guard_status = "PASS"
    if strict_status != "OK":
        guard_status = "BLOCK"
    elif has_bom:
        guard_status = "WARN_BOM"
    elif newline_style in {"CRLF", "MIXED", "MIXED_OR_CR"}:
        guard_status = "WARN_NEWLINE"

    return EncodingProbeRecord(
        path=str(target),
        exists=True,
        byte_size=len(raw),
        strict_utf8_status=strict_status,
        has_utf8_bom=has_bom,
        newline_style=newline_style,
        guard_status=guard_status,
    )


def build_encoding_probe_report(root: str | Path = ".") -> List[EncodingProbeRecord]:
    base = Path(root)
    records: List[EncodingProbeRecord] = []
    for relative_path in discover_guarded_files(base):
        target = base / relative_path
        probe = probe_encoding_file(target)
        records.append(
            EncodingProbeRecord(
                path=relative_path,
                exists=probe.exists,
                byte_size=probe.byte_size,
                strict_utf8_status=probe.strict_utf8_status,
                has_utf8_bom=probe.has_utf8_bom,
                newline_style=probe.newline_style,
                guard_status=probe.guard_status,
            )
        )
    return records


def assert_encoding_probe_no_block(records: Iterable[EncodingProbeRecord]) -> None:
    bad = [record for record in records if record.guard_status == "BLOCK"]
    if bad:
        details = "; ".join(f"{record.path}={record.strict_utf8_status}" for record in sorted(bad, key=lambda item: item.path))
        raise ValueError(f"CONTROL_CENTER_ENCODING_PROBE_BLOCKED: {details}")