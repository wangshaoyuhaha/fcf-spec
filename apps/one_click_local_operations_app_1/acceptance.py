from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY


@dataclass(frozen=True)
class OneClickLocalOperationsAcceptance:
    status: str
    checks: Mapping[str, bool]
    next_phase: str

    def __post_init__(self) -> None:
        checks = MappingProxyType(dict(self.checks))
        if self.status != "D1_D6_ACCEPTED" or not all(checks.values()):
            raise ValueError("Stage 9 acceptance is incomplete")
        if self.next_phase != "MULTI_MARKET_PAPER_SHADOW_VALIDATION":
            raise ValueError("Stage 9 next phase must remain explicit")
        object.__setattr__(self, "checks", checks)


def build_one_click_local_operations_acceptance():
    ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY.__post_init__()
    return OneClickLocalOperationsAcceptance(
        status="D1_D6_ACCEPTED",
        checks={
            "atomic_owned_state": True,
            "backup_and_upgrade_snapshot": True,
            "browser_after_health": True,
            "database_target_backup": True,
            "deterministic_preflight": True,
            "exact_loopback_service": True,
            "graceful_owned_stop": True,
            "migration_check": True,
            "missing_model_notification": True,
            "recovery_staging_no_auto_activation": True,
            "service_failure_notification": True,
            "state_export": True,
            "windows_double_click_entry_points": True,
        },
        next_phase="MULTI_MARKET_PAPER_SHADOW_VALIDATION",
    )
