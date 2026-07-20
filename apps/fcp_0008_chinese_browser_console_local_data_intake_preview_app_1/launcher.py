from pathlib import Path
from typing import Iterable

from apps.browser_product_console_runtime_app_1 import (
    BrowserConsoleRuntime,
    build_browser_console_runtime,
)

from .application import LocalizedBrowserConsoleApplication
from .contracts import ConsoleLocale, LocalCSVPreview


def build_localized_browser_console_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
    local_csv_previews: Iterable[LocalCSVPreview] = (),
) -> BrowserConsoleRuntime:
    base = build_browser_console_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        port=port,
        title=title,
    )
    localized = LocalizedBrowserConsoleApplication(
        base_application=base.application,
        default_locale=ConsoleLocale(locale_id),
        local_csv_previews=tuple(local_csv_previews),
    )
    return BrowserConsoleRuntime(
        config=base.config,
        index_path=base.index_path,
        application=localized,
    )
