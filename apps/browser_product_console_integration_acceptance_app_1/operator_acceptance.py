from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from .contracts import REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS


_ALLOWED_MATRIX_STATUSES = frozenset({"BLOCKED", "PASSED"})
_REQUIRED_RESTRICTIONS = frozenset(
    {
        "p1-p47-frozen",
        "no-p48",
        "paper-only",
        "local-only",
        "loopback-only",
        "sidecar-only",
        "registered-artifact-only",
        "read-only-product-presentation",
        "operator-review-required",
        "deterministic-engine-authority",
        "registered-evidence-authority",
        "ai-advisory-only",
        "no-order-path",
        "no-real-execution",
        "no-automatic-approval",
        "no-automatic-promotion",
        "no-automatic-learning-activation",
        "no-tag",
        "no-release",
        "no-deployment",
    }
)


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _normalized_items(values: object, name: str) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a tuple of text")

    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise ValueError(f"{name} must be iterable") from exc

    for value in normalized:
        if (
            not isinstance(value, str)
            or not value
            or value != value.strip()
            or "\r" in value
            or "\n" in value
        ):
            raise ValueError(f"{name} must contain normalized text")

    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must not contain duplicates")

    return normalized


@dataclass(frozen=True)
class IntegrationValidationSummary:
    targeted_passed: int
    targeted_skipped: int
    full_passed: int
    full_skipped: int
    run_all_checks_passed: bool
    generated_outputs_restored: bool
    exact_changed_files_verified: bool
    diff_check_passed: bool

    def __post_init__(self) -> None:
        for name in (
            "targeted_passed",
            "targeted_skipped",
            "full_passed",
            "full_skipped",
        ):
            object.__setattr__(self, name, _count(getattr(self, name), name))

        if self.targeted_passed == 0 or self.full_passed == 0:
            raise ValueError("validation pass counts must be positive")

        for name in (
            "run_all_checks_passed",
            "generated_outputs_restored",
            "exact_changed_files_verified",
            "diff_check_passed",
        ):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be boolean")

    @property
    def ok(self) -> bool:
        return all(
            (
                self.run_all_checks_passed,
                self.generated_outputs_restored,
                self.exact_changed_files_verified,
                self.diff_check_passed,
            )
        )

    def to_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "targeted_passed": self.targeted_passed,
                "targeted_skipped": self.targeted_skipped,
                "full_passed": self.full_passed,
                "full_skipped": self.full_skipped,
                "run_all_checks_passed": self.run_all_checks_passed,
                "generated_outputs_restored": self.generated_outputs_restored,
                "exact_changed_files_verified": (
                    self.exact_changed_files_verified
                ),
                "diff_check_passed": self.diff_check_passed,
                "ok": self.ok,
            }
        )


@dataclass(frozen=True)
class BrowserConsoleIntegrationOperatorAcceptance:
    phase: str
    stage: str
    status: str
    matrix_results: Tuple[Tuple[str, str], ...]
    validation_summary: IntegrationValidationSummary
    unresolved_items: Tuple[str, ...]
    permanent_restrictions: Tuple[str, ...]
    operator_review_required: bool = True
    read_only: bool = True
    automatic_approval_allowed: bool = False

    def __post_init__(self) -> None:
        if self.phase != (
            "BROWSER-PRODUCT-CONSOLE-INTEGRATION-ACCEPTANCE-APP-1"
        ):
            raise ValueError("unexpected Operator acceptance phase")
        if self.stage != "D5":
            raise ValueError("unexpected Operator acceptance stage")
        if not isinstance(
            self.validation_summary,
            IntegrationValidationSummary,
        ):
            raise ValueError("invalid validation summary")

        matrix_results = tuple(tuple(item) for item in self.matrix_results)
        if tuple(item[0] for item in matrix_results) != (
            REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
        ):
            raise ValueError("Operator acceptance matrix changed")
        if any(
            len(item) != 2 or item[1] not in _ALLOWED_MATRIX_STATUSES
            for item in matrix_results
        ):
            raise ValueError("invalid Operator acceptance matrix status")

        unresolved_items = _normalized_items(
            self.unresolved_items,
            "unresolved_items",
        )
        restrictions = _normalized_items(
            self.permanent_restrictions,
            "permanent_restrictions",
        )
        if not _REQUIRED_RESTRICTIONS.issubset(set(restrictions)):
            raise ValueError("required permanent restrictions are missing")

        ready = (
            all(item[1] == "PASSED" for item in matrix_results)
            and self.validation_summary.ok
            and not unresolved_items
        )
        expected_status = (
            "READY_FOR_OPERATOR_REVIEW" if ready else "BLOCKED"
        )
        if self.status != expected_status:
            raise ValueError("Operator acceptance status is inconsistent")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or self.automatic_approval_allowed is not False
        ):
            raise ValueError("Operator acceptance authority changed")

        object.__setattr__(self, "matrix_results", matrix_results)
        object.__setattr__(self, "unresolved_items", unresolved_items)
        object.__setattr__(self, "permanent_restrictions", restrictions)

    @property
    def ready_for_operator_review(self) -> bool:
        return self.status == "READY_FOR_OPERATOR_REVIEW"

    def to_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "phase": self.phase,
                "stage": self.stage,
                "status": self.status,
                "matrix_results": tuple(
                    {
                        "matrix_id": matrix_id,
                        "status": status,
                    }
                    for matrix_id, status in self.matrix_results
                ),
                "validation_summary": dict(
                    self.validation_summary.to_payload()
                ),
                "unresolved_items": self.unresolved_items,
                "permanent_restrictions": self.permanent_restrictions,
                "operator_review_required": self.operator_review_required,
                "read_only": self.read_only,
                "automatic_approval_allowed": (
                    self.automatic_approval_allowed
                ),
            }
        )


def build_browser_console_integration_operator_acceptance(
    validation_summary: IntegrationValidationSummary,
    *,
    blocked_matrix_ids: Tuple[str, ...] = (),
    unresolved_items: Tuple[str, ...] = (),
) -> BrowserConsoleIntegrationOperatorAcceptance:
    blocked = _normalized_items(blocked_matrix_ids, "blocked_matrix_ids")
    unknown = set(blocked).difference(
        REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
    )
    if unknown:
        raise ValueError("unknown blocked matrix id")

    matrix_results = tuple(
        (
            matrix_id,
            "BLOCKED" if matrix_id in blocked else "PASSED",
        )
        for matrix_id in REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
    )
    normalized_unresolved = _normalized_items(
        unresolved_items,
        "unresolved_items",
    )
    ready = (
        not blocked
        and validation_summary.ok
        and not normalized_unresolved
    )

    return BrowserConsoleIntegrationOperatorAcceptance(
        phase=(
            "BROWSER-PRODUCT-CONSOLE-INTEGRATION-ACCEPTANCE-APP-1"
        ),
        stage="D5",
        status=(
            "READY_FOR_OPERATOR_REVIEW" if ready else "BLOCKED"
        ),
        matrix_results=matrix_results,
        validation_summary=validation_summary,
        unresolved_items=normalized_unresolved,
        permanent_restrictions=tuple(sorted(_REQUIRED_RESTRICTIONS)),
    )
