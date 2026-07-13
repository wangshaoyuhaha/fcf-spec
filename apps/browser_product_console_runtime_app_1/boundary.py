
from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from pathlib import Path


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def is_loopback_host(value: str) -> bool:
    normalized = _require_text(value, "host")
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return normalized.lower() == "localhost"


@dataclass(frozen=True)
class ConsoleRuntimeBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    server_autostart_allowed: bool = False
    external_network_binding_allowed: bool = False
    remote_browser_access_allowed: bool = False
    public_internet_exposure_allowed: bool = False
    credential_storage_allowed: bool = False
    broker_or_exchange_connection_allowed: bool = False
    account_balance_position_wallet_access_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_authority,
            self.ai_advisory_only,
        )
        if not all(required):
            raise ValueError("console safety authority flags must remain enabled")

        prohibited = (
            self.server_autostart_allowed,
            self.external_network_binding_allowed,
            self.remote_browser_access_allowed,
            self.public_internet_exposure_allowed,
            self.credential_storage_allowed,
            self.broker_or_exchange_connection_allowed,
            self.account_balance_position_wallet_access_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited console capability cannot be enabled")


BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY = ConsoleRuntimeBoundary()


@dataclass(frozen=True)
class ConsoleRuntimeConfig:
    allowed_root: Path
    host: str = "127.0.0.1"
    port: int = 8765
    title: str = "FCF Browser Product Console"
    route_prefix: str = "/"

    def __post_init__(self) -> None:
        host = _require_text(self.host, "host")
        if host != "127.0.0.1":
            raise ValueError("host must be exactly 127.0.0.1")
        if not is_loopback_host(host):
            raise ValueError("host must be loopback")
        if not 1024 <= int(self.port) <= 65535:
            raise ValueError("port must be between 1024 and 65535")
        object.__setattr__(self, "host", host)
        object.__setattr__(self, "port", int(self.port))
        object.__setattr__(self, "title", _require_text(self.title, "title"))
        if self.route_prefix != "/":
            raise ValueError("route_prefix must remain /")

    def resolve_allowed_root(self) -> Path:
        root = Path(self.allowed_root)
        if root.is_symlink():
            raise ValueError("symbolic allowed roots are not permitted")
        resolved = root.resolve(strict=True)
        if not resolved.is_dir():
            raise ValueError("allowed_root must be a directory")
        return resolved
