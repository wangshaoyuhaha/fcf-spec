from pathlib import Path
from typing import Iterable

from apps.browser_product_console_runtime_app_1 import BrowserConsoleRuntime
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    LocalCSVPreview,
    build_localized_browser_console_runtime,
)

from .application import MarketDataDiagnosticsConsoleApplication
from .readiness import MarketDataAdapterReadinessSnapshot


def build_market_data_diagnostics_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    snapshot: MarketDataAdapterReadinessSnapshot,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
    local_csv_previews: Iterable[LocalCSVPreview] = (),
) -> BrowserConsoleRuntime:
    base = build_localized_browser_console_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        port=port,
        title=title,
        locale_id=locale_id,
        local_csv_previews=local_csv_previews,
    )
    application = MarketDataDiagnosticsConsoleApplication(
        base_application=base.application,
        snapshot=snapshot,
    )
    return BrowserConsoleRuntime(
        config=base.config,
        index_path=base.index_path,
        application=application,
    )
