"""Governed Stage 8 FCF Web Console sidecar."""

from .acceptance import (
    FCFWebConsoleAcceptance,
    build_fcf_web_console_acceptance,
)
from .application import FCFWebConsoleApplication, WebConsoleResponse
from .boundary import FCF_WEB_CONSOLE_BOUNDARY, FCFWebConsoleBoundary
from .contracts import (
    FCF_WEB_CONSOLE_ROUTES,
    ConsoleAction,
    ConsoleActionReceipt,
    IntakeDescriptor,
    IntakeKind,
    IntakeValidationReceipt,
    ProductRoute,
    WebConsoleSnapshot,
)
from .controls import GovernedConsoleActionService
from .intake import GovernedIntakeService
from .server import (
    FCFWebConsoleServerConfig,
    create_fcf_web_console_server,
)

__all__ = [
    "ConsoleAction",
    "ConsoleActionReceipt",
    "FCFWebConsoleAcceptance",
    "FCFWebConsoleApplication",
    "FCFWebConsoleBoundary",
    "FCFWebConsoleServerConfig",
    "FCF_WEB_CONSOLE_BOUNDARY",
    "FCF_WEB_CONSOLE_ROUTES",
    "GovernedConsoleActionService",
    "GovernedIntakeService",
    "IntakeDescriptor",
    "IntakeKind",
    "IntakeValidationReceipt",
    "ProductRoute",
    "WebConsoleResponse",
    "WebConsoleSnapshot",
    "build_fcf_web_console_acceptance",
    "create_fcf_web_console_server",
]
