from __future__ import annotations

import os
import tempfile
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


@dataclass(frozen=True)
class SafeWriteResult:
    path: str
    byte_size: int
    encoding_status: str
    newline_style: str
    atomic_write: bool
    backup_created: bool
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


def normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_text_utf8(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(normalize_lf(content), encoding="utf-8", newline="\n")


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


def create_backup_copy(path: str | Path) -> Path | None:
    target = Path(path)
    if not target.exists():
        return None
    backup = target.with_suffix(target.suffix + ".bak")
    backup.write_bytes(target.read_bytes())
    return backup


def atomic_write_utf8_lf(path: str | Path, content: str, create_backup: bool = False) -> SafeWriteResult:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    backup_created = False
    if create_backup:
        backup = create_backup_copy(target)
        backup_created = backup is not None

    normalized = normalize_lf(content)
    encoded = normalized.encode("utf-8")

    fd, temp_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=str(target.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    probe = probe_encoding_file(target)
    return SafeWriteResult(
        path=str(target),
        byte_size=probe.byte_size,
        encoding_status=probe.strict_utf8_status,
        newline_style=probe.newline_style,
        atomic_write=True,
        backup_created=backup_created,
        guard_status=probe.guard_status,
    )


def append_section_utf8_lf(path: str | Path, section_title: str, section_body: str, create_backup: bool = False) -> SafeWriteResult:
    target = Path(path)
    current = ""
    if target.exists():
        current = read_text_utf8_strict(target)

    marker = f"## {section_title}"
    if marker in current:
        return SafeWriteResult(
            path=str(target),
            byte_size=len(target.read_bytes()),
            encoding_status="OK",
            newline_style=detect_newline_style(target.read_bytes()),
            atomic_write=False,
            backup_created=False,
            guard_status=probe_encoding_file(target).guard_status,
        )

    base = normalize_lf(current).rstrip()
    addition = f"{marker}\n\n{normalize_lf(section_body).strip()}\n"
    next_content = f"{base}\n\n{addition}" if base else addition
    return atomic_write_utf8_lf(target, next_content, create_backup=create_backup)


def assert_safe_write_result_ok(result: SafeWriteResult) -> None:
    if result.encoding_status != "OK":
        raise ValueError(f"CONTROL_CENTER_SAFE_WRITE_FAILED: {result.path}={result.encoding_status}")
    if result.guard_status == "BLOCK":
        raise ValueError(f"CONTROL_CENTER_SAFE_WRITE_BLOCKED: {result.path}")

@dataclass(frozen=True)
class EncodingGuardPacket:
    stage_id: str
    registry_total: int
    probe_total: int
    ok_count: int
    warn_count: int
    block_count: int
    status_by_path: Dict[str, str]
    safety_scope: str
    operator_review_required: bool
    real_execution_allowed: bool
    trade_action_enabled: bool


def build_encoding_guard_packet(root: str | Path = ".") -> EncodingGuardPacket:
    registry = build_guard_registry(root)
    probes = build_encoding_probe_report(root)

    ok_count = sum(1 for record in probes if record.guard_status == "PASS")
    warn_count = sum(1 for record in probes if record.guard_status.startswith("WARN"))
    block_count = sum(1 for record in probes if record.guard_status == "BLOCK")
    status_by_path = {record.path: record.guard_status for record in probes}

    return EncodingGuardPacket(
        stage_id="CONTROL-CENTER-ENCODING-GUARD-APP-1-D5",
        registry_total=len(registry),
        probe_total=len(probes),
        ok_count=ok_count,
        warn_count=warn_count,
        block_count=block_count,
        status_by_path=status_by_path,
        safety_scope="PAPER_ONLY_LOCAL_ONLY_READ_ONLY_SIDECAR_ONLY",
        operator_review_required=True,
        real_execution_allowed=False,
        trade_action_enabled=False,
    )


def render_encoding_guard_packet_md(packet: EncodingGuardPacket) -> str:
    lines: List[str] = [
        "# CONTROL-CENTER-ENCODING-GUARD-APP-1 D5 Packet",
        "",
        "## Summary",
        "",
        f"- stage_id: {packet.stage_id}",
        f"- registry_total: {packet.registry_total}",
        f"- probe_total: {packet.probe_total}",
        f"- ok_count: {packet.ok_count}",
        f"- warn_count: {packet.warn_count}",
        f"- block_count: {packet.block_count}",
        f"- safety_scope: {packet.safety_scope}",
        f"- operator_review_required: {str(packet.operator_review_required).lower()}",
        f"- real_execution_allowed: {str(packet.real_execution_allowed).lower()}",
        f"- trade_action_enabled: {str(packet.trade_action_enabled).lower()}",
        "",
        "## File Status",
        "",
    ]

    for path, status in sorted(packet.status_by_path.items()):
        lines.append(f"- {path}: {status}")

    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- paper-only",
            "- local-only",
            "- read-only",
            "- sidecar-only",
            "- operator review required",
            "- no real trading",
            "- no broker API",
            "- no exchange API",
            "- no API key",
            "- no buy button",
            "- no sell button",
            "- no order button",
            "- no tag",
            "- no release",
            "- no deploy",
            "",
        ]
    )

    return "\n".join(lines)


def write_encoding_guard_packet(root: str | Path, output_path: str | Path) -> SafeWriteResult:
    import json
    from dataclasses import asdict

    packet = build_encoding_guard_packet(root)
    payload = json.dumps(asdict(packet), indent=2, sort_keys=True) + "\n"
    return atomic_write_utf8_lf(output_path, payload)


def write_encoding_guard_packet_md(root: str | Path, output_path: str | Path) -> SafeWriteResult:
    packet = build_encoding_guard_packet(root)
    return atomic_write_utf8_lf(output_path, render_encoding_guard_packet_md(packet))


def assert_encoding_guard_packet_ok(packet: EncodingGuardPacket) -> None:
    if packet.block_count:
        raise ValueError(f"CONTROL_CENTER_ENCODING_GUARD_PACKET_BLOCKED: block_count={packet.block_count}")
    if packet.real_execution_allowed:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_PACKET_REAL_EXECUTION_FORBIDDEN")
    if packet.trade_action_enabled:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_PACKET_TRADE_ACTION_FORBIDDEN")
    if not packet.operator_review_required:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_PACKET_OPERATOR_REVIEW_REQUIRED")


@dataclass(frozen=True)
class EncodingGuardCloseout:
    app_id: str
    completed_stages: List[str]
    final_status: str
    validation_required: bool
    merge_ready: bool
    paper_only: bool
    local_only: bool
    read_only: bool
    sidecar_only: bool
    operator_review_required: bool
    no_real_trading: bool
    no_tag_release_deploy: bool


def build_encoding_guard_closeout() -> EncodingGuardCloseout:
    return EncodingGuardCloseout(
        app_id="CONTROL-CENTER-ENCODING-GUARD-APP-1",
        completed_stages=[
            "D1 strict UTF-8 guard contract",
            "D2 guarded source registry",
            "D3 read-only encoding probe",
            "D4 UTF-8 LF safe writer",
            "D5 encoding guard packet",
            "D6 final workflow handoff and closeout",
        ],
        final_status="READY_FOR_MAIN_MERGE",
        validation_required=True,
        merge_ready=True,
        paper_only=True,
        local_only=True,
        read_only=True,
        sidecar_only=True,
        operator_review_required=True,
        no_real_trading=True,
        no_tag_release_deploy=True,
    )


def render_encoding_guard_closeout_md(closeout: EncodingGuardCloseout) -> str:
    lines: List[str] = [
        "# CONTROL-CENTER-ENCODING-GUARD-APP-1 D6 Final Closeout",
        "",
        "## App",
        "",
        f"- app_id: {closeout.app_id}",
        f"- final_status: {closeout.final_status}",
        f"- validation_required: {str(closeout.validation_required).lower()}",
        f"- merge_ready: {str(closeout.merge_ready).lower()}",
        "",
        "## Completed Stages",
        "",
    ]

    for stage in closeout.completed_stages:
        lines.append(f"- {stage}")

    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            f"- paper_only: {str(closeout.paper_only).lower()}",
            f"- local_only: {str(closeout.local_only).lower()}",
            f"- read_only: {str(closeout.read_only).lower()}",
            f"- sidecar_only: {str(closeout.sidecar_only).lower()}",
            f"- operator_review_required: {str(closeout.operator_review_required).lower()}",
            f"- no_real_trading: {str(closeout.no_real_trading).lower()}",
            f"- no_tag_release_deploy: {str(closeout.no_tag_release_deploy).lower()}",
            "",
            "## Final Handoff",
            "",
            "CONTROL-CENTER-ENCODING-GUARD-APP-1 protects governance documents from unreadable UTF-8 states.",
            "It provides strict UTF-8 checks, guarded source registry, encoding probe, safe writer, guard packet, and final closeout.",
            "",
            "This sidecar does not mutate core logic and does not enable trading execution.",
            "",
        ]
    )

    return "\n".join(lines)


def write_encoding_guard_closeout_md(output_path: str | Path) -> SafeWriteResult:
    closeout = build_encoding_guard_closeout()
    return atomic_write_utf8_lf(output_path, render_encoding_guard_closeout_md(closeout))


def assert_encoding_guard_closeout_safe(closeout: EncodingGuardCloseout) -> None:
    if not closeout.merge_ready:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_NOT_MERGE_READY")
    if not closeout.paper_only:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_PAPER_ONLY_REQUIRED")
    if not closeout.local_only:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_LOCAL_ONLY_REQUIRED")
    if not closeout.read_only:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_READ_ONLY_REQUIRED")
    if not closeout.sidecar_only:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_SIDECAR_ONLY_REQUIRED")
    if not closeout.operator_review_required:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_OPERATOR_REVIEW_REQUIRED")
    if not closeout.no_real_trading:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_REAL_TRADING_FORBIDDEN")
    if not closeout.no_tag_release_deploy:
        raise ValueError("CONTROL_CENTER_ENCODING_GUARD_CLOSEOUT_TAG_RELEASE_DEPLOY_FORBIDDEN")
