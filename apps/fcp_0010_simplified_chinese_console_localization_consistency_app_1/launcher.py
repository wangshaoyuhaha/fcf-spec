from pathlib import Path
from typing import Iterable

from apps.browser_product_console_runtime_app_1 import BrowserConsoleRuntime
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    ConsoleLocale,
    LocalCSVPreview,
)
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataAdapterReadinessSnapshot,
    build_market_data_diagnostics_runtime,
)

from .application import SimplifiedChineseConsoleApplication


def build_simplified_chinese_console_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    snapshot: MarketDataAdapterReadinessSnapshot,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
    local_csv_previews: Iterable[LocalCSVPreview] = (),
) -> BrowserConsoleRuntime:
    base = build_market_data_diagnostics_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        snapshot=snapshot,
        port=port,
        title=title,
        locale_id="en",
        local_csv_previews=local_csv_previews,
    )
    application = SimplifiedChineseConsoleApplication(
        base_application=base.application,
        default_locale=ConsoleLocale(locale_id),
    )
    return BrowserConsoleRuntime(
        config=base.config,
        index_path=base.index_path,
        application=application,
    )
