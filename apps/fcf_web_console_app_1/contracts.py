from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple


def require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def require_sha256(value: object, field_name: str) -> str:
    digest = require_text(value, field_name).lower()
    if len(digest) != 64 or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise ValueError(f"{field_name} must be a SHA-256 digest")
    return digest


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class IntakeKind(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"
    JSON = "JSON"
    TEXT = "TEXT"
    URL = "URL"
    LOCAL_FILE = "LOCAL_FILE"


class ConsoleAction(str, Enum):
    ASK_RESEARCH_QUESTION = "ASK_RESEARCH_QUESTION"
    APPROVE_FOR_RESEARCH_ARCHIVE = "APPROVE_FOR_RESEARCH_ARCHIVE"
    REJECT = "REJECT"
    REQUEST_REANALYSIS = "REQUEST_REANALYSIS"
    REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
    MARK_DATA_UNTRUSTED = "MARK_DATA_UNTRUSTED"
    COMPARE_MODELS = "COMPARE_MODELS"
    OVERRIDE_WITH_REASON = "OVERRIDE_WITH_REASON"
    FREEZE_REPORT = "FREEZE_REPORT"
    EXPORT = "EXPORT"
    START_WORKFLOW = "START_WORKFLOW"
    STOP_WORKFLOW = "STOP_WORKFLOW"


@dataclass(frozen=True)
class ProductRoute:
    path: str
    title: str
    capability: str
    navigation_order: int

    def __post_init__(self) -> None:
        path = require_text(self.path, "path")
        if not path.startswith("/"):
            raise ValueError("product route must be absolute")
        if self.navigation_order < 0:
            raise ValueError("navigation_order must be non-negative")
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "title", require_text(self.title, "title"))
        object.__setattr__(
            self,
            "capability",
            require_text(self.capability, "capability"),
        )


FCF_WEB_CONSOLE_ROUTES = (
    ProductRoute("/", "Overview", "product_overview", 0),
    ProductRoute("/intake", "Evidence Intake", "governed_intake", 1),
    ProductRoute(
        "/conversation",
        "Research Conversation",
        "controlled_research",
        2,
    ),
    ProductRoute("/workflows", "Workflow Monitor", "workflow_monitoring", 3),
    ProductRoute("/evidence", "Evidence", "evidence_inspection", 4),
    ProductRoute("/models", "Model Comparison", "model_comparison", 5),
    ProductRoute("/risk", "Risk and Policy", "risk_visibility", 6),
    ProductRoute(
        "/portfolio",
        "Portfolio Construction",
        "portfolio_construction",
        7,
    ),
    ProductRoute(
        "/paper-portfolio",
        "Paper Portfolio",
        "paper_portfolio",
        8,
    ),
    ProductRoute("/reports", "Reports", "comprehensive_reports", 9),
    ProductRoute(
        "/operator-review",
        "Operator Review",
        "operator_governance",
        10,
    ),
    ProductRoute(
        "/operations",
        "Local Operations",
        "workflow_control_requests",
        11,
    ),
)


@dataclass(frozen=True)
class IntakeDescriptor:
    item_id: str
    kind: IntakeKind
    display_name: str
    media_type: str
    size_bytes: int
    content_sha256: str
    source_reference: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "item_id",
            require_text(self.item_id, "item_id"),
        )
        kind = self.kind if isinstance(self.kind, IntakeKind) else IntakeKind(self.kind)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(
            self,
            "display_name",
            require_text(self.display_name, "display_name"),
        )
        object.__setattr__(
            self,
            "media_type",
            require_text(self.media_type, "media_type"),
        )
        if int(self.size_bytes) < 0 or int(self.size_bytes) > 25_000_000:
            raise ValueError("size_bytes must be between 0 and 25000000")
        object.__setattr__(self, "size_bytes", int(self.size_bytes))
        object.__setattr__(
            self,
            "content_sha256",
            require_sha256(self.content_sha256, "content_sha256"),
        )
        object.__setattr__(
            self,
            "source_reference",
            str(self.source_reference).strip(),
        )


@dataclass(frozen=True)
class IntakeValidationReceipt:
    request_id: str
    correlation_id: str
    operator_id: str
    descriptors: Tuple[IntakeDescriptor, ...]
    request_sha256: str
    status: str = "QUARANTINED_PENDING_EVIDENCE_REGISTRATION"
    network_retrieval_performed: bool = False
    evidence_registered: bool = False
    authoritative_input: bool = False

    def __post_init__(self) -> None:
        if self.status != "QUARANTINED_PENDING_EVIDENCE_REGISTRATION":
            raise ValueError("intake receipt must remain quarantined")
        if (
            self.network_retrieval_performed
            or self.evidence_registered
            or self.authoritative_input
        ):
            raise ValueError("intake validation cannot create authority")


@dataclass(frozen=True)
class ConsoleActionReceipt:
    request_id: str
    correlation_id: str
    operator_id: str
    action: ConsoleAction
    target_artifact_id: str
    reason: str
    request_sha256: str
    status: str = "VALIDATED_OPERATOR_REQUEST"
    automatic_transition_allowed: bool = False
    authority_mutated: bool = False
    execution_performed: bool = False

    def __post_init__(self) -> None:
        if self.status != "VALIDATED_OPERATOR_REQUEST":
            raise ValueError("unsupported action receipt status")
        if (
            self.automatic_transition_allowed
            or self.authority_mutated
            or self.execution_performed
        ):
            raise ValueError("console requests cannot mutate authority")


@dataclass(frozen=True)
class WebConsoleSnapshot:
    correlation_id: str
    sections: Mapping[str, Tuple[Mapping[str, Any], ...]]
    source_artifact_ids: Tuple[str, ...]
    paper_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "correlation_id",
            require_text(self.correlation_id, "correlation_id"),
        )
        frozen_sections = {}
        for section_name, payloads in self.sections.items():
            name = require_text(section_name, "section_name")
            frozen_sections[name] = tuple(
                MappingProxyType(dict(payload)) for payload in payloads
            )
        object.__setattr__(
            self,
            "sections",
            MappingProxyType(dict(sorted(frozen_sections.items()))),
        )
        artifact_ids = tuple(
            require_text(value, "source_artifact_id")
            for value in self.source_artifact_ids
        )
        if len(set(artifact_ids)) != len(artifact_ids):
            raise ValueError("source_artifact_ids must be unique")
        object.__setattr__(self, "source_artifact_ids", artifact_ids)
        if not self.paper_only or not self.operator_review_required:
            raise ValueError("snapshot must remain paper-only and reviewed")

    @classmethod
    def from_console_read_model(cls, read_model: object) -> "WebConsoleSnapshot":
        return cls(
            correlation_id=getattr(read_model, "correlation_id"),
            sections=getattr(read_model, "sections"),
            source_artifact_ids=getattr(read_model, "source_artifact_ids"),
            paper_only=bool(getattr(read_model, "paper_only")),
            operator_review_required=bool(
                getattr(read_model, "operator_review_required")
            ),
        )
