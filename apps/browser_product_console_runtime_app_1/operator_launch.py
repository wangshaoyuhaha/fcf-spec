from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


APP_ID = "BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1"
LAUNCH_STAGE_ID = "D1"
STARTER_DATA_CLASSIFICATION = "DEMONSTRATION_ONLY"
DEFAULT_PORT = 8765
DEFAULT_TITLE = "FCF Browser Product Console - Demonstration Data"


@dataclass(frozen=True)
class OperatorLaunchBoundary:
    explicit_operator_invocation_required: bool = True
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    server_autostart_allowed: bool = False
    external_data_fetching_allowed: bool = False
    public_network_binding_allowed: bool = False
    financial_execution_allowed: bool = False
    automatic_learning_activation_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.explicit_operator_invocation_required,
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
        )
        if not all(required):
            raise ValueError("operator launch safety flags must remain enabled")

        prohibited = (
            self.server_autostart_allowed,
            self.external_data_fetching_allowed,
            self.public_network_binding_allowed,
            self.financial_execution_allowed,
            self.automatic_learning_activation_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited operator launch capability cannot be enabled")


OPERATOR_LAUNCH_BOUNDARY = OperatorLaunchBoundary()


@dataclass(frozen=True)
class OperatorLaunchProfile:
    allowed_root: Path
    index_path: Path
    port: int = DEFAULT_PORT
    title: str = DEFAULT_TITLE
    open_browser: bool = True
    data_classification: str = STARTER_DATA_CLASSIFICATION

    def __post_init__(self) -> None:
        root = Path(self.allowed_root)
        index = Path(self.index_path)
        title = str(self.title).strip()
        classification = str(self.data_classification).strip()

        if not title:
            raise ValueError("title is required")
        if not classification:
            raise ValueError("data_classification is required")
        if not 1024 <= int(self.port) <= 65535:
            raise ValueError("port must be between 1024 and 65535")

        object.__setattr__(self, "allowed_root", root)
        object.__setattr__(self, "index_path", index)
        object.__setattr__(self, "port", int(self.port))
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "data_classification", classification)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/"


def default_starter_root(project_root: Path | None = None) -> Path:
    root = (
        Path(project_root)
        if project_root is not None
        else Path(__file__).resolve().parents[2]
    )
    return root / "examples" / "browser_product_console_starter"


def build_default_operator_launch_profile(
    *,
    project_root: Path | None = None,
    port: int = DEFAULT_PORT,
    open_browser: bool = True,
) -> OperatorLaunchProfile:
    starter_root = default_starter_root(project_root)
    return OperatorLaunchProfile(
        allowed_root=starter_root,
        index_path=starter_root / "index.json",
        port=port,
        open_browser=open_browser,
    )
