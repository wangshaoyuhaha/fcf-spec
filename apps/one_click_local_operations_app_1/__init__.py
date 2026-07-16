"""One-click local operations for the governed FCF Web Console."""

from .acceptance import (
    OneClickLocalOperationsAcceptance,
    build_one_click_local_operations_acceptance,
)
from .boundary import (
    ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY,
    OneClickLocalOperationsBoundary,
)
from .contracts import (
    LocalLifecycleState,
    LocalOperationReceipt,
    LocalOperationsProfile,
    LocalPreflightReport,
    LocalRuntimeState,
)
from .controller import (
    OneClickLocalOperationsController,
    probe_health,
    process_is_alive,
)
from .preflight import run_local_operations_preflight
from .snapshot import (
    OperationalSnapshotReceipt,
    OperationalSnapshotService,
)
from .state_store import LocalOperationsStateStore

__all__ = [
    "LocalLifecycleState",
    "LocalOperationReceipt",
    "LocalOperationsProfile",
    "LocalOperationsStateStore",
    "LocalPreflightReport",
    "LocalRuntimeState",
    "ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY",
    "OneClickLocalOperationsAcceptance",
    "OneClickLocalOperationsBoundary",
    "OneClickLocalOperationsController",
    "OperationalSnapshotReceipt",
    "OperationalSnapshotService",
    "build_one_click_local_operations_acceptance",
    "probe_health",
    "process_is_alive",
    "run_local_operations_preflight",
]
