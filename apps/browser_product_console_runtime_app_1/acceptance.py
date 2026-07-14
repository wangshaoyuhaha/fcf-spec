from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from .boundary import BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY
from .operator_commands import BROWSER_CONSOLE_OPERATOR_COMMAND_BOUNDARY


@dataclass(frozen=True)
class BrowserConsoleRuntimeAcceptance:
    phase: str
    status: str
    checks: Mapping[str, bool]
    delivered_capabilities: Tuple[str, ...]
    permanent_restrictions: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.phase != "BROWSER-PRODUCT-CONSOLE-RUNTIME-APP-1":
            raise ValueError("unexpected acceptance phase")
        if self.status != "READY_FOR_MAIN_MERGE":
            raise ValueError("unexpected acceptance status")
        if not self.checks or not all(self.checks.values()):
            raise ValueError("every browser console acceptance check must pass")
        if len(set(self.delivered_capabilities)) != len(
            self.delivered_capabilities
        ):
            raise ValueError("delivered capabilities must be unique")
        if len(set(self.permanent_restrictions)) != len(
            self.permanent_restrictions
        ):
            raise ValueError("permanent restrictions must be unique")
        required = {
            "paper-only",
            "local-only",
            "loopback-only",
            "sidecar-only",
            "operator-review-required",
            "no-real-execution",
            "no-order-path",
            "no-automatic-approval",
            "no-automatic-promotion",
            "no-automatic-baseline-replacement",
            "no-automatic-learning-activation",
            "no-automatic-archive",
            "no-p48",
            "p1-p47-frozen",
        }
        if not required.issubset(set(self.permanent_restrictions)):
            raise ValueError("required permanent restrictions are missing")


def build_browser_console_runtime_acceptance() -> BrowserConsoleRuntimeAcceptance:
    runtime = BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY
    commands = BROWSER_CONSOLE_OPERATOR_COMMAND_BOUNDARY

    checks = MappingProxyType(
        {
            "ai_advisory_only": runtime.ai_advisory_only,
            "artifact_hash_verification": runtime.registered_artifact_only,
            "deterministic_authority": runtime.deterministic_authority,
            "external_network_binding_blocked": (
                not runtime.external_network_binding_allowed
            ),
            "loopback_only": runtime.loopback_only,
            "operator_command_auto_approval_blocked": (
                not commands.automatic_approval_allowed
            ),
            "operator_command_auto_archive_blocked": (
                not commands.automatic_archive_allowed
            ),
            "operator_command_auto_learning_blocked": (
                not commands.automatic_learning_activation_allowed
            ),
            "operator_command_auto_promotion_blocked": (
                not commands.automatic_promotion_allowed
            ),
            "operator_present_required": commands.operator_present_required,
            "operator_review_required": runtime.operator_review_required,
            "order_path_blocked": not runtime.order_path_allowed,
            "paper_only": runtime.paper_only,
            "public_internet_exposure_blocked": (
                not runtime.public_internet_exposure_allowed
            ),
            "read_only_presentation": runtime.read_only_presentation,
            "real_execution_blocked": not runtime.real_execution_allowed,
            "registered_artifact_only": runtime.registered_artifact_only,
            "remote_browser_access_blocked": (
                not runtime.remote_browser_access_allowed
            ),
            "server_autostart_blocked": not runtime.server_autostart_allowed,
            "sidecar_only": runtime.sidecar_only,
        }
    )

    return BrowserConsoleRuntimeAcceptance(
        phase="BROWSER-PRODUCT-CONSOLE-RUNTIME-APP-1",
        status="READY_FOR_MAIN_MERGE",
        checks=checks,
        delivered_capabilities=(
            "loopback-http-runtime",
            "registered-artifact-index",
            "sha256-artifact-verification",
            "deterministic-console-read-model",
            "stock-candidate-ranked-watchlist",
            "score-breakdown-presentation",
            "reason-code-presentation",
            "risk-flag-presentation",
            "paper-and-shadow-validation-presentation",
            "operator-review-presentation",
            "report-and-archive-presentation",
            "governed-operator-command-validation",
            "deterministic-operator-review-receipts",
            "atomic-local-audit-bundles",
            "idempotent-exact-reuse",
            "tamper-and-collision-rejection",
            "explicit-operator-launcher",
        ),
        permanent_restrictions=(
            "p1-p47-frozen",
            "no-p48",
            "paper-only",
            "local-only",
            "loopback-only",
            "sidecar-only",
            "registered-artifact-only",
            "operator-review-required",
            "deterministic-authority",
            "ai-advisory-only",
            "no-public-network-exposure",
            "no-broker-or-exchange-connection",
            "no-credentials",
            "no-account-balance-position-or-wallet-access",
            "no-order-path",
            "no-real-execution",
            "no-automatic-approval",
            "no-automatic-promotion",
            "no-automatic-baseline-replacement",
            "no-automatic-learning-activation",
            "no-automatic-archive",
            "no-tag",
            "no-release",
            "no-deployment",
        ),
    )
