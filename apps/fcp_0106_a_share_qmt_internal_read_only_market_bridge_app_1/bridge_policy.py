from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
from pathlib import Path
import stat


ALLOWED_IMPORT_ROOTS = frozenset(
    {"__future__", "decimal", "hashlib", "json", "os", "re", "time"}
)
ALLOWED_CONTEXT_CALLS = frozenset({"set_universe", "subscribe_quote"})
FORBIDDEN_CALLS = frozenset(
    {
        "buy",
        "cancel_order",
        "get_trade_detail_data",
        "order_shares",
        "order_target",
        "order_target_value",
        "order_value",
        "passorder",
        "sell",
        "set_account",
        "subscribe_whole_quote",
    }
)
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "http",
        "requests",
        "socket",
        "urllib",
        "websocket",
        "xtquant",
    }
)


def _is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


@dataclass(frozen=True)
class BridgeSourcePolicyReport:
    source_sha256: str
    imported_roots: tuple[str, ...]
    context_calls: tuple[str, ...]
    forbidden_calls: tuple[str, ...]
    forbidden_imports: tuple[str, ...]
    has_init: bool
    has_quote_callback: bool
    ok: bool


def inspect_bridge_source(source: str) -> BridgeSourcePolicyReport:
    if not isinstance(source, str):
        raise TypeError("source must be text")
    source.encode("ascii")
    tree = ast.parse(source)
    imported: set[str] = set()
    context_calls: set[str] = set()
    forbidden_calls: set[str] = set()
    functions: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
        elif isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".", 1)[0])
        elif isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "ContextInfo"
                ):
                    context_calls.add(name)
            if name in FORBIDDEN_CALLS:
                forbidden_calls.add(name)
    forbidden_imports = imported.intersection(FORBIDDEN_IMPORT_ROOTS)
    unregistered_imports = imported.difference(ALLOWED_IMPORT_ROOTS)
    bad_context_calls = context_calls.difference(ALLOWED_CONTEXT_CALLS)
    has_init = "init" in functions
    has_quote_callback = "_on_quote" in functions
    ok = not any(
        (
            forbidden_calls,
            forbidden_imports,
            unregistered_imports,
            bad_context_calls,
            not has_init,
            not has_quote_callback,
            context_calls != ALLOWED_CONTEXT_CALLS,
        )
    )
    return BridgeSourcePolicyReport(
        source_sha256=hashlib.sha256(source.encode("ascii")).hexdigest(),
        imported_roots=tuple(sorted(imported)),
        context_calls=tuple(sorted(context_calls)),
        forbidden_calls=tuple(sorted(forbidden_calls)),
        forbidden_imports=tuple(sorted(forbidden_imports | unregistered_imports)),
        has_init=has_init,
        has_quote_callback=has_quote_callback,
        ok=ok,
    )


def inspect_bridge_file(path: Path) -> BridgeSourcePolicyReport:
    candidate = path.absolute()
    if str(candidate).startswith("\\\\"):
        raise ValueError("bridge source must not use a network path")
    for component in (candidate, *candidate.parents):
        if str(component) == component.anchor:
            continue
        if component.is_symlink() or _is_reparse_point(component):
            raise ValueError("bridge source must be a regular local file")
    target = candidate.resolve(strict=True)
    if (
        not target.is_file()
        or target.is_symlink()
        or _is_reparse_point(target)
    ):
        raise ValueError("bridge source must be a regular local file")
    if str(target).startswith("\\\\"):
        raise ValueError("bridge source must not use a network path")
    return inspect_bridge_source(target.read_text(encoding="ascii"))
