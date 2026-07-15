from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping, Optional
from urllib.parse import urlsplit

from .artifact_index import LoadedConsoleArtifactIndex, load_console_artifact_index
from .launcher import BrowserConsoleRuntime, build_browser_console_runtime


APP_ID = "BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1"
LAUNCH_STAGE_ID = "D1"
STARTER_PACKAGE_STAGE_ID = "D2"
GUIDED_LAUNCH_STAGE_ID = "D3"
DIAGNOSTIC_STAGE_ID = "D4"
PRODUCT_ACCEPTANCE_STAGE_ID = "D5"
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


class OperatorLaunchDiagnosticCode(str, Enum):
    READY = "FCF-LAUNCH-READY"
    ARTIFACT_MISSING = "FCF-LAUNCH-ARTIFACT-MISSING"
    ARTIFACT_INTEGRITY_FAILURE = "FCF-LAUNCH-ARTIFACT-INTEGRITY"
    ARTIFACT_REGISTRATION_FAILURE = "FCF-LAUNCH-ARTIFACT-REGISTRATION"
    FILE_ACCESS_DENIED = "FCF-LAUNCH-FILE-ACCESS"
    PORT_UNAVAILABLE = "FCF-LAUNCH-PORT-UNAVAILABLE"
    STARTUP_REJECTED = "FCF-LAUNCH-STARTUP-REJECTED"


@dataclass(frozen=True)
class OperatorLaunchPreflight:
    status: str
    code: OperatorLaunchDiagnosticCode
    message: str
    remediation: str
    session: Optional[OperatorLaunchSession] = None

    def __post_init__(self) -> None:
        if self.status not in {"READY", "BLOCKED"}:
            raise ValueError("invalid preflight status")
        if not self.message.strip() or not self.remediation.strip():
            raise ValueError("preflight guidance is required")
        if self.status == "READY":
            if self.code is not OperatorLaunchDiagnosticCode.READY:
                raise ValueError("ready preflight requires ready code")
            if self.session is None:
                raise ValueError("ready preflight requires a launch session")
        elif self.session is not None:
            raise ValueError("blocked preflight cannot contain a session")


@dataclass(frozen=True)
class OperatorLaunchAcceptance:
    app_id: str
    stage_id: str
    status: str
    checks: Mapping[str, bool]
    permanent_restrictions: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.app_id != APP_ID or self.stage_id != PRODUCT_ACCEPTANCE_STAGE_ID:
            raise ValueError("operator launch acceptance identity mismatch")
        if self.status != "READY_FOR_OPERATOR_USE":
            raise ValueError("operator launch acceptance status mismatch")
        if not self.checks or not all(self.checks.values()):
            raise ValueError("operator launch acceptance checks must pass")
        object.__setattr__(self, "checks", MappingProxyType(dict(self.checks)))


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


def classify_operator_launch_error(
    error: BaseException,
) -> tuple[OperatorLaunchDiagnosticCode, str, str]:
    message = str(error)
    cause: BaseException = error
    while cause.__cause__ is not None:
        cause = cause.__cause__
    if isinstance(error, FileNotFoundError):
        return (
            OperatorLaunchDiagnosticCode.ARTIFACT_MISSING,
            "A required registered artifact or index is missing.",
            "Restore the registered package or select a valid custom root and index.",
        )
    if isinstance(error, PermissionError):
        return (
            OperatorLaunchDiagnosticCode.FILE_ACCESS_DENIED,
            "The registered artifact package is not readable.",
            "Grant read access to the local package and run the preflight again.",
        )
    if (
        message == "console loopback port is unavailable"
        or (
            isinstance(cause, OSError)
            and (
                getattr(cause, "winerror", None) == 10048
                or getattr(cause, "errno", None) in {48, 98, 10048}
            )
        )
    ):
        return (
            OperatorLaunchDiagnosticCode.PORT_UNAVAILABLE,
            "The selected loopback port is already in use.",
            "Stop the other local service or choose another port with --port.",
        )
    if "SHA-256" in message or "tampered" in message.lower():
        return (
            OperatorLaunchDiagnosticCode.ARTIFACT_INTEGRITY_FAILURE,
            "Registered artifact integrity validation failed.",
            "Restore the original registered artifact package; do not bypass the digest.",
        )
    if isinstance(error, ValueError) and (
        "artifact" in message.lower()
        or "index" in message.lower()
        or "allowed_root" in message.lower()
    ):
        return (
            OperatorLaunchDiagnosticCode.ARTIFACT_REGISTRATION_FAILURE,
            "The artifact root or registration index is invalid.",
            "Use a contained registered index with supported artifact contracts.",
        )
    return (
        OperatorLaunchDiagnosticCode.STARTUP_REJECTED,
        "The local read-only console startup was rejected.",
        "Review the launch profile and run --check before starting the server.",
    )


def build_operator_launch_preflight(
    profile: OperatorLaunchProfile,
    *,
    check_port: bool = True,
) -> OperatorLaunchPreflight:
    try:
        session = prepare_operator_launch(profile)
        if check_port:
            server = session.create_server()
            server.server_close()
    except (OSError, RuntimeError, ValueError) as exc:
        code, message, remediation = classify_operator_launch_error(exc)
        return OperatorLaunchPreflight(
            status="BLOCKED",
            code=code,
            message=message,
            remediation=remediation,
        )
    return OperatorLaunchPreflight(
        status="READY",
        code=OperatorLaunchDiagnosticCode.READY,
        message="Registered artifacts and exact loopback startup are ready.",
        remediation="Run the explicit Operator launch command to open the console.",
        session=session,
    )


def build_operator_launch_acceptance() -> OperatorLaunchAcceptance:
    return OperatorLaunchAcceptance(
        app_id=APP_ID,
        stage_id=PRODUCT_ACCEPTANCE_STAGE_ID,
        status="READY_FOR_OPERATOR_USE",
        checks={
            "explicit_operator_launch": True,
            "registered_starter_package": True,
            "demonstration_label_visible": True,
            "a_share_us_equity_btc_visible": True,
            "exact_loopback_http": True,
            "read_only_routes": True,
            "deterministic_diagnostics": True,
            "browser_open_operator_invoked": True,
            "operator_runbook_present": True,
        },
        permanent_restrictions=(
            "p1-p47-frozen",
            "no-p48",
            "paper-only",
            "local-only",
            "loopback-only",
            "registered-artifact-only",
            "read-only-presentation",
            "operator-review-required",
            "deterministic-authority-preserved",
            "registered-evidence-authority-preserved",
            "ai-advisory-only",
            "no-real-execution",
            "no-automatic-learning-activation",
        ),
    )
