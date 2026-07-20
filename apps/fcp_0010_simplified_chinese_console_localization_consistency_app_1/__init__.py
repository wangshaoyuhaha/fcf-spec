from .application import SimplifiedChineseConsoleApplication
from .boundary import FCP_0010_BOUNDARY, ConsoleLocalizationConsistencyBoundary
from .catalog import AUDITED_UI_LABELS, REGISTERED_HTML_ROUTES
from .coverage import LocalizationCoverageReport, audit_simplified_chinese_document
from .launcher import build_simplified_chinese_console_runtime
from .localization import localize_consistent_html

__all__ = (
    "AUDITED_UI_LABELS",
    "FCP_0010_BOUNDARY",
    "REGISTERED_HTML_ROUTES",
    "ConsoleLocalizationConsistencyBoundary",
    "LocalizationCoverageReport",
    "SimplifiedChineseConsoleApplication",
    "audit_simplified_chinese_document",
    "build_simplified_chinese_console_runtime",
    "localize_consistent_html",
)
