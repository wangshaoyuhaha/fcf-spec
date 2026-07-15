from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

from .artifact_index import LoadedConsoleArtifactIndex, load_console_artifact_index
from .launcher import BrowserConsoleRuntime, build_browser_console_runtime


APP_ID = "BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1"
LAUNCH_STAGE_ID = "D1"
STARTER_PACKAGE_STAGE_ID = "D2"
GUIDED_LAUNCH_STAGE_ID = "D3"
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


@dataclass(frozen=True)
class StarterArtifactPackage:
    correlation_id: str
    artifact_count: int
    artifact_ids: tuple[str, ...]
    artifact_types: tuple[str, ...]
    data_classification: str = STARTER_DATA_CLASSIFICATION
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not self.correlation_id.strip():
            raise ValueError("correlation_id is required")
        if self.artifact_count < 1:
            raise ValueError("starter package must contain artifacts")
        if self.artifact_count != len(self.artifact_ids):
            raise ValueError("starter artifact count mismatch")
        if len(set(self.artifact_ids)) != len(self.artifact_ids):
            raise ValueError("starter artifact ids must be unique")
        if self.data_classification != STARTER_DATA_CLASSIFICATION:
            raise ValueError("starter data must remain demonstrative")
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")


@dataclass(frozen=True)
class OperatorLaunchSession:
    profile: OperatorLaunchProfile
    runtime: BrowserConsoleRuntime
    artifact_count: int

    def __post_init__(self) -> None:
        if self.runtime.config.host != "127.0.0.1":
            raise ValueError("operator launch must remain exact loopback")
        if self.runtime.config.port != self.profile.port:
            raise ValueError("operator launch port mismatch")
        if self.artifact_count < 1:
            raise ValueError("operator launch requires registered artifacts")

    @property
    def url(self) -> str:
        return self.profile.url

    def create_server(self):
        return self.runtime.create_server()


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


def load_starter_artifact_package(
    profile: OperatorLaunchProfile,
) -> tuple[StarterArtifactPackage, LoadedConsoleArtifactIndex]:
    loaded = load_console_artifact_index(
        profile.index_path,
        profile.allowed_root,
    )

    for artifact in loaded.artifacts:
        payload = artifact.payload
        if payload.get("data_classification") != STARTER_DATA_CLASSIFICATION:
            raise ValueError(
                "starter artifact must be classified DEMONSTRATION_ONLY"
            )
        if payload.get("operator_review_required") is not True:
            raise ValueError("starter artifact must require Operator review")

    package = StarterArtifactPackage(
        correlation_id=loaded.index.correlation_id,
        artifact_count=len(loaded.artifacts),
        artifact_ids=tuple(
            artifact.registration.artifact_id
            for artifact in loaded.artifacts
        ),
        artifact_types=tuple(
            sorted(
                {
                    artifact.registration.artifact_type
                    for artifact in loaded.artifacts
                }
            )
        ),
    )
    return package, loaded


def prepare_operator_launch(
    profile: OperatorLaunchProfile,
) -> OperatorLaunchSession:
    if profile.data_classification == STARTER_DATA_CLASSIFICATION:
        package, _ = load_starter_artifact_package(profile)
        artifact_count = package.artifact_count
    else:
        loaded = load_console_artifact_index(
            profile.index_path,
            profile.allowed_root,
        )
        artifact_count = len(loaded.artifacts)

    runtime = build_browser_console_runtime(
        allowed_root=profile.allowed_root,
        index_path=profile.index_path,
        port=profile.port,
        title=profile.title,
    )
    return OperatorLaunchSession(
        profile=profile,
        runtime=runtime,
        artifact_count=artifact_count,
    )


def open_operator_browser(
    url: str,
    *,
    opener: Callable[[str], object],
) -> bool:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != "/"
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("browser URL must remain exact local loopback")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("browser URL contains an invalid port") from exc
    if port is None or not 1024 <= port <= 65535:
        raise ValueError("browser URL must contain an allowed loopback port")
    return bool(opener(url))
