from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from .artifact_index import load_console_artifact_index
from .boundary import ConsoleRuntimeConfig
from .read_model import build_console_read_model
from .web_console import (
    BrowserProductConsoleApplication,
    create_loopback_server,
)


@dataclass(frozen=True)
class BrowserConsoleRuntime:
    config: ConsoleRuntimeConfig
    index_path: str
    application: BrowserProductConsoleApplication

    def __post_init__(self) -> None:
        if self.config.host != "127.0.0.1":
            raise ValueError("runtime host must remain exactly 127.0.0.1")
        if not self.index_path.strip():
            raise ValueError("index_path is required")
        model = self.application.read_model
        if not model.paper_only or not model.read_only:
            raise ValueError("runtime model must remain paper-only and read-only")
        if not model.operator_review_required:
            raise ValueError("Operator review must remain required")

    def create_server(self):
        return create_loopback_server(self.config, self.application)


def build_browser_console_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
) -> BrowserConsoleRuntime:
    config = ConsoleRuntimeConfig(
        allowed_root=Path(allowed_root),
        host="127.0.0.1",
        port=port,
        title=title,
    )
    resolved_root = config.resolve_allowed_root()
    candidate = Path(index_path)
    if not candidate.is_absolute():
        candidate = resolved_root / candidate
    loaded = load_console_artifact_index(candidate, resolved_root)
    model = build_console_read_model(loaded)
    application = BrowserProductConsoleApplication(model)
    return BrowserConsoleRuntime(
        config=config,
        index_path=loaded.index_path,
        application=application,
    )


def serve_browser_console_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
) -> NoReturn:
    runtime = build_browser_console_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        port=port,
        title=title,
    )
    server = runtime.create_server()
    try:
        server.serve_forever()
    finally:
        server.server_close()
