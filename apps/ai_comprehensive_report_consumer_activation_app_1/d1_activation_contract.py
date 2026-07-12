"""D1 production entry-point discovery and activation contract.

This module performs deterministic read-only repository discovery.
It does not invoke a model, execute a prompt, route automatically,
approve operator decisions, or write archive artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

PHASE_ID = "AI-COMPREHENSIVE-REPORT-CONSUMER-ACTIVATION-APP-1"
SOURCE_BINDING_PACKAGE = (
    "apps.ai_comprehensive_report_consumer_binding_app_1"
)

OPERATOR_REVIEW_SURFACE = "operator_review"
UI_SURFACE = "ui"
REPORT_ARCHIVE_SURFACE = "report_archive"

ACTIVATION_SURFACES = (
    OPERATOR_REVIEW_SURFACE,
    UI_SURFACE,
    REPORT_ARCHIVE_SURFACE,
)

PRODUCTION_ROOTS = ("app", "apps", "operator_review_app", "report_archive_app")

_EXCLUDED_PARTS = {
    "__pycache__",
    "tests",
    "ai_comprehensive_report_consumer_binding_app_1",
    "ai_comprehensive_report_consumer_activation_app_1",
}

_SURFACE_TOKENS = {
    OPERATOR_REVIEW_SURFACE: (
        "operator_review",
        "review_packet",
    ),
    UI_SURFACE: (
        "ui_",
        "_ui",
        "dashboard",
        "ui/",
    ),
    REPORT_ARCHIVE_SURFACE: (
        "report_archive",
        "archive",
    ),
}


@dataclass(frozen=True)
class ActivationEntryPointCandidate:
    """Read-only candidate for later explicit activation."""

    surface: str
    relative_path: str
    module_path: str
    entry_point_kind: str = "python_module_candidate"
    registered_artifact_required: bool = True
    operator_review_required: bool = True
    manual_archive_authorization_required: bool = True
    automatic_activation_allowed: bool = False


@dataclass(frozen=True)
class ActivationContract:
    """Boundary contract for deterministic consumer activation."""

    phase_id: str
    source_binding_package: str
    production_roots: tuple[str, ...]
    required_surfaces: tuple[str, ...]
    candidates: tuple[ActivationEntryPointCandidate, ...]
    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    deterministic_only: bool = True
    registered_artifacts_only: bool = True
    operator_review_required: bool = True
    manual_archive_authorization_required: bool = True
    frozen_core_mutation_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_archive_allowed: bool = False
    archive_write_allowed: bool = False
    runtime_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_routing_allowed: bool = False
    real_execution_allowed: bool = False

    def candidate_count_by_surface(self) -> dict[str, int]:
        """Return deterministic candidate counts by required surface."""

        return {
            surface: sum(
                1 for candidate in self.candidates
                if candidate.surface == surface
            )
            for surface in self.required_surfaces
        }

    def validate(self) -> tuple[str, ...]:
        """Return contract validation errors without mutating state."""

        errors: list[str] = []

        if self.phase_id != PHASE_ID:
            errors.append("phase_id_mismatch")

        if self.source_binding_package != SOURCE_BINDING_PACKAGE:
            errors.append("source_binding_package_mismatch")

        if self.required_surfaces != ACTIVATION_SURFACES:
            errors.append("required_surfaces_mismatch")

        if not self.paper_only:
            errors.append("paper_only_required")

        if not self.local_only:
            errors.append("local_only_required")

        if not self.read_only:
            errors.append("read_only_required")

        if not self.sidecar_only:
            errors.append("sidecar_only_required")

        if not self.deterministic_only:
            errors.append("deterministic_only_required")

        if not self.registered_artifacts_only:
            errors.append("registered_artifacts_only_required")

        if not self.operator_review_required:
            errors.append("operator_review_required")

        if not self.manual_archive_authorization_required:
            errors.append("manual_archive_authorization_required")

        forbidden_flags = {
            "frozen_core_mutation_allowed":
                self.frozen_core_mutation_allowed,
            "automatic_approval_allowed":
                self.automatic_approval_allowed,
            "automatic_archive_allowed":
                self.automatic_archive_allowed,
            "archive_write_allowed":
                self.archive_write_allowed,
            "runtime_model_invocation_allowed":
                self.runtime_model_invocation_allowed,
            "prompt_execution_allowed":
                self.prompt_execution_allowed,
            "automatic_routing_allowed":
                self.automatic_routing_allowed,
            "real_execution_allowed":
                self.real_execution_allowed,
        }

        for name, value in forbidden_flags.items():
            if value:
                errors.append(f"{name}_must_be_false")

        counts = self.candidate_count_by_surface()

        for surface in self.required_surfaces:
            if counts[surface] == 0:
                errors.append(f"missing_candidate_surface:{surface}")

        for candidate in self.candidates:
            if candidate.surface not in self.required_surfaces:
                errors.append(
                    f"unexpected_candidate_surface:{candidate.surface}"
                )

            if not candidate.registered_artifact_required:
                errors.append(
                    f"registered_artifact_required:{candidate.relative_path}"
                )

            if not candidate.operator_review_required:
                errors.append(
                    f"operator_review_required:{candidate.relative_path}"
                )

            if not candidate.manual_archive_authorization_required:
                errors.append(
                    "manual_archive_authorization_required:"
                    f"{candidate.relative_path}"
                )

            if candidate.automatic_activation_allowed:
                errors.append(
                    f"automatic_activation_forbidden:{candidate.relative_path}"
                )

        return tuple(sorted(set(errors)))

    def to_dict(self) -> dict[str, object]:
        """Return a serializable deterministic contract representation."""

        result = asdict(self)
        result["candidate_count_by_surface"] = (
            self.candidate_count_by_surface()
        )
        result["validation_errors"] = list(self.validate())
        result["valid"] = not self.validate()
        return result


def _is_excluded(relative_path: Path) -> bool:
    lowered_parts = {part.lower() for part in relative_path.parts}

    return bool(lowered_parts.intersection(_EXCLUDED_PARTS))


def _module_path(relative_path: Path) -> str:
    return ".".join(relative_path.with_suffix("").parts)


def discover_production_entry_point_candidates(
    repo_root: str | Path,
) -> tuple[ActivationEntryPointCandidate, ...]:
    """Discover deterministic production candidates by repository path."""

    root = Path(repo_root)
    candidates: list[ActivationEntryPointCandidate] = []

    for production_root_name in PRODUCTION_ROOTS:
        production_root = root / production_root_name

        if not production_root.is_dir():
            continue

        for path in sorted(production_root.rglob("*.py")):
            relative_path = path.relative_to(root)

            if _is_excluded(relative_path):
                continue

            normalized = relative_path.as_posix().lower()

            for surface in ACTIVATION_SURFACES:
                tokens = _SURFACE_TOKENS[surface]

                if not any(token in normalized for token in tokens):
                    continue

                candidates.append(
                    ActivationEntryPointCandidate(
                        surface=surface,
                        relative_path=relative_path.as_posix(),
                        module_path=_module_path(relative_path),
                    )
                )

    return tuple(
        sorted(
            candidates,
            key=lambda item: (
                item.surface,
                item.relative_path,
                item.module_path,
            ),
        )
    )


def build_activation_contract(
    repo_root: str | Path,
) -> ActivationContract:
    """Build the D1 activation contract from read-only discovery."""

    contract = ActivationContract(
        phase_id=PHASE_ID,
        source_binding_package=SOURCE_BINDING_PACKAGE,
        production_roots=PRODUCTION_ROOTS,
        required_surfaces=ACTIVATION_SURFACES,
        candidates=discover_production_entry_point_candidates(repo_root),
    )

    errors = contract.validate()

    if errors:
        raise ValueError(
            "Invalid activation contract: " + ", ".join(errors)
        )

    return contract
