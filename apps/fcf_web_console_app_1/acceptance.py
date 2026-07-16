from dataclasses import dataclass
from typing import Tuple

from .boundary import FCF_WEB_CONSOLE_BOUNDARY
from .contracts import FCF_WEB_CONSOLE_ROUTES, ConsoleAction, IntakeKind


@dataclass(frozen=True)
class FCFWebConsoleAcceptance:
    status: str
    delivered_routes: Tuple[str, ...]
    delivered_input_kinds: Tuple[str, ...]
    delivered_actions: Tuple[str, ...]
    deferred_stage: str

    def __post_init__(self) -> None:
        if self.status != "D1_D6_ACCEPTED":
            raise ValueError("Stage 8 acceptance is incomplete")
        if self.deferred_stage != "ONE-CLICK-LOCAL-OPERATIONS-APP-1":
            raise ValueError("local operations stage must remain explicit")


def build_fcf_web_console_acceptance() -> FCFWebConsoleAcceptance:
    FCF_WEB_CONSOLE_BOUNDARY.__post_init__()
    return FCFWebConsoleAcceptance(
        status="D1_D6_ACCEPTED",
        delivered_routes=tuple(route.path for route in FCF_WEB_CONSOLE_ROUTES),
        delivered_input_kinds=tuple(kind.value for kind in IntakeKind),
        delivered_actions=tuple(action.value for action in ConsoleAction),
        deferred_stage="ONE-CLICK-LOCAL-OPERATIONS-APP-1",
    )
