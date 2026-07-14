from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .evidence_audit_explorer import EvidenceRelation
from .evidence_audit_graph import EvidenceArtifactGraph
from .read_model import ConsoleArtifactRecord, ConsoleReadModel


_SAFE_VALUE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_SAFE_PAYLOAD_KEY_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$"
)

_RISK_FIELDS = (
    "risk_flags",
    "risk_flag",
    "risk_codes",
    "risk_code",
)
_CONTRADICTION_FIELDS = (
    "contradiction_codes",
    "contradiction_code",
)
_AI_ARTIFACT_TYPES = frozenset(
    {
        "ai_explanation",
        "ai_evaluation",
    }
)


def _require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _safe_text(value: object, field_name: str) -> str:
    normalized = _require_text(value, field_name)
    if not _SAFE_VALUE_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{field_name} contains a prohibited character"
        )
    return normalized


def _explicit_values(
    value: object,
    field_name: str,
) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_values = (value,)
    elif isinstance(value, (tuple, list)):
        raw_values = tuple(value)
    else:
        raise ValueError(
            f"{field_name} must be text or an array"
        )

    normalized = tuple(
        _safe_text(item, field_name)
        for item in raw_values
    )
    return tuple(sorted(set(normalized)))


def _values_from_fields(
    payload: Mapping[str, Any],
    fields: Tuple[str, ...],
) -> Tuple[str, ...]:
    values = []
    for field_name in fields:
        values.extend(
            _explicit_values(
                payload.get(field_name),
                field_name,
            )
        )
    return tuple(sorted(set(values)))


def _payload_label(
    payload: Mapping[str, Any],
    keys: Tuple[str, ...],
    default: str,
) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (str, int, float, bool)):
            normalized = str(value).strip()
            if normalized:
                return normalized
    return default


def _payload_keys(
    payload: Mapping[str, Any],
) -> Tuple[str, ...]:
    return tuple(
        sorted(
            key
            for key in (
                str(item).strip()
                for item in payload.keys()
            )
            if _SAFE_PAYLOAD_KEY_PATTERN.fullmatch(key)
        )
    )


@dataclass(frozen=True)
class EvidenceRiskFinding:
    artifact_id: str
    artifact_type: str
    subject: str
    risk_flags: Tuple[str, ...]
    severity: str
    relative_path: str
    content_sha256: str
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        artifact_id = _safe_text(
            self.artifact_id,
            "artifact_id",
        )
        artifact_type = _safe_text(
            self.artifact_type,
            "artifact_type",
        )
        subject = _safe_text(self.subject, "subject")
        risk_flags = _explicit_values(
            self.risk_flags,
            "risk_flags",
        )
        if not risk_flags:
            raise ValueError(
                "risk finding must contain an explicit risk flag"
            )
        severity = _safe_text(
            self.severity,
            "severity",
        )
        relative_path = _require_text(
            self.relative_path,
            "relative_path",
        )
        digest = _require_text(
            self.content_sha256,
            "content_sha256",
        ).lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError(
                "content_sha256 must be a SHA-256 digest"
            )
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "risk evidence must remain "
                "registered-artifact-only and read-only"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )

        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(
            self,
            "artifact_type",
            artifact_type,
        )
        object.__setattr__(self, "subject", subject)
        object.__setattr__(
            self,
            "risk_flags",
            risk_flags,
        )
        object.__setattr__(self, "severity", severity)
        object.__setattr__(
            self,
            "relative_path",
            relative_path,
        )
        object.__setattr__(
            self,
            "content_sha256",
            digest,
        )


@dataclass(frozen=True)
class EvidenceContradictionFinding:
    artifact_id: str
    artifact_type: str
    contradiction_codes: Tuple[str, ...]
    target_artifact_ids: Tuple[str, ...]
    status: str
    relative_path: str
    content_sha256: str
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        artifact_id = _safe_text(
            self.artifact_id,
            "artifact_id",
        )
        artifact_type = _safe_text(
            self.artifact_type,
            "artifact_type",
        )
        codes = _explicit_values(
            self.contradiction_codes,
            "contradiction_codes",
        )
        if not codes:
            raise ValueError(
                "contradiction finding must contain an explicit code"
            )
        targets = _explicit_values(
            self.target_artifact_ids,
            "target_artifact_ids",
        )
        status = _safe_text(self.status, "status")
        relative_path = _require_text(
            self.relative_path,
            "relative_path",
        )
        digest = _require_text(
            self.content_sha256,
            "content_sha256",
        ).lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError(
                "content_sha256 must be a SHA-256 digest"
            )
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "contradiction evidence must remain "
                "registered-artifact-only and read-only"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )

        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(
            self,
            "artifact_type",
            artifact_type,
        )
        object.__setattr__(
            self,
            "contradiction_codes",
            codes,
        )
        object.__setattr__(
            self,
            "target_artifact_ids",
            targets,
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(
            self,
            "relative_path",
            relative_path,
        )
        object.__setattr__(
            self,
            "content_sha256",
            digest,
        )


@dataclass(frozen=True)
class EvidenceAIDrilldown:
    artifact_id: str
    artifact_type: str
    model_label: str
    prompt_version: str
    evaluation_state: str
    evidence_keys: Tuple[str, ...]
    relative_path: str
    content_sha256: str
    registered_artifact_only: bool = True
    read_only: bool = True
    ai_advisory_only: bool = True
    deterministic_authority: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        artifact_id = _safe_text(
            self.artifact_id,
            "artifact_id",
        )
        if self.artifact_type not in _AI_ARTIFACT_TYPES:
            raise ValueError(
                "unsupported AI evidence artifact type"
            )
        model_label = _require_text(
            self.model_label,
            "model_label",
        )
        prompt_version = _require_text(
            self.prompt_version,
            "prompt_version",
        )
        evaluation_state = _require_text(
            self.evaluation_state,
            "evaluation_state",
        )
        evidence_keys = tuple(
            sorted(set(self.evidence_keys))
        )
        if any(
            not _SAFE_PAYLOAD_KEY_PATTERN.fullmatch(item)
            for item in evidence_keys
        ):
            raise ValueError(
                "AI evidence key contains a prohibited character"
            )
        relative_path = _require_text(
            self.relative_path,
            "relative_path",
        )
        digest = _require_text(
            self.content_sha256,
            "content_sha256",
        ).lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError(
                "content_sha256 must be a SHA-256 digest"
            )

        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "AI evidence must remain "
                "registered-artifact-only and read-only"
            )
        if not self.ai_advisory_only:
            raise ValueError("AI must remain advisory-only")
        if not self.deterministic_authority:
            raise ValueError(
                "Deterministic Engine authority must remain enabled"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )

        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(
            self,
            "model_label",
            model_label,
        )
        object.__setattr__(
            self,
            "prompt_version",
            prompt_version,
        )
        object.__setattr__(
            self,
            "evaluation_state",
            evaluation_state,
        )
        object.__setattr__(
            self,
            "evidence_keys",
            evidence_keys,
        )
        object.__setattr__(
            self,
            "relative_path",
            relative_path,
        )
        object.__setattr__(
            self,
            "content_sha256",
            digest,
        )


@dataclass(frozen=True)
class EvidenceRiskAIDossier:
    correlation_id: str
    state: str
    risk_findings: Tuple[EvidenceRiskFinding, ...]
    contradiction_findings: Tuple[
        EvidenceContradictionFinding,
        ...,
    ]
    ai_evidence: Tuple[EvidenceAIDrilldown, ...]
    risk_flag_counts: Mapping[str, int]
    contradiction_code_counts: Mapping[str, int]
    ai_artifact_type_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    ai_advisory_only: bool = True
    deterministic_authority: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        correlation_id = _safe_text(
            self.correlation_id,
            "correlation_id",
        )
        if self.state not in {
            "AVAILABLE",
            "NO_REGISTERED_RISK_AI_EVIDENCE",
        }:
            raise ValueError(
                "unsupported risk and AI dossier state"
            )

        risk_findings = tuple(self.risk_findings)
        contradiction_findings = tuple(
            self.contradiction_findings
        )
        ai_evidence = tuple(self.ai_evidence)

        expected_state = (
            "AVAILABLE"
            if (
                risk_findings
                or contradiction_findings
                or ai_evidence
            )
            else "NO_REGISTERED_RISK_AI_EVIDENCE"
        )
        if self.state != expected_state:
            raise ValueError(
                "risk and AI dossier state mismatch"
            )

        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "risk and AI dossier must remain "
                "registered-artifact-only and read-only"
            )
        if not self.ai_advisory_only:
            raise ValueError("AI must remain advisory-only")
        if not self.deterministic_authority:
            raise ValueError(
                "Deterministic Engine authority must remain enabled"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )

        object.__setattr__(
            self,
            "correlation_id",
            correlation_id,
        )
        object.__setattr__(
            self,
            "risk_findings",
            risk_findings,
        )
        object.__setattr__(
            self,
            "contradiction_findings",
            contradiction_findings,
        )
        object.__setattr__(
            self,
            "ai_evidence",
            ai_evidence,
        )
        object.__setattr__(
            self,
            "risk_flag_counts",
            MappingProxyType(
                dict(sorted(self.risk_flag_counts.items()))
            ),
        )
        object.__setattr__(
            self,
            "contradiction_code_counts",
            MappingProxyType(
                dict(
                    sorted(
                        self.contradiction_code_counts.items()
                    )
                )
            ),
        )
        object.__setattr__(
            self,
            "ai_artifact_type_counts",
            MappingProxyType(
                dict(
                    sorted(
                        self.ai_artifact_type_counts.items()
                    )
                )
            ),
        )


def _risk_findings_for_record(
    record: ConsoleArtifactRecord,
) -> Tuple[EvidenceRiskFinding, ...]:
    findings = []

    direct_flags = _values_from_fields(
        record.payload,
        _RISK_FIELDS,
    )
    if direct_flags:
        findings.append(
            EvidenceRiskFinding(
                artifact_id=record.artifact_id,
                artifact_type=record.artifact_type,
                subject=_payload_label(
                    record.payload,
                    (
                        "symbol",
                        "subject",
                        "candidate_id",
                        "model_name",
                    ),
                    record.artifact_id,
                ),
                risk_flags=direct_flags,
                severity=_payload_label(
                    record.payload,
                    (
                        "risk_level",
                        "severity",
                        "risk_state",
                    ),
                    "UNSPECIFIED",
                ),
                relative_path=record.relative_path,
                content_sha256=record.content_sha256,
            )
        )

    if record.artifact_type == "ranked_watchlist":
        raw_candidates = record.payload.get("candidates", [])
        if not isinstance(raw_candidates, list):
            raise ValueError(
                "ranked_watchlist candidates must be an array"
            )
        for index, candidate in enumerate(raw_candidates):
            if not isinstance(candidate, Mapping):
                raise ValueError(
                    "ranked_watchlist candidate must be an object"
                )
            candidate_flags = _values_from_fields(
                candidate,
                _RISK_FIELDS,
            )
            if not candidate_flags:
                continue
            subject = _payload_label(
                candidate,
                (
                    "symbol",
                    "candidate_id",
                    "name",
                ),
                f"candidate-{index + 1}",
            )
            findings.append(
                EvidenceRiskFinding(
                    artifact_id=record.artifact_id,
                    artifact_type=record.artifact_type,
                    subject=subject,
                    risk_flags=candidate_flags,
                    severity=_payload_label(
                        candidate,
                        (
                            "risk_level",
                            "severity",
                            "risk_state",
                        ),
                        "UNSPECIFIED",
                    ),
                    relative_path=record.relative_path,
                    content_sha256=record.content_sha256,
                )
            )

    return tuple(
        sorted(
            findings,
            key=lambda item: (
                item.artifact_type,
                item.artifact_id,
                item.subject,
                item.risk_flags,
            ),
        )
    )


def _contradiction_finding_for_record(
    record: ConsoleArtifactRecord,
    graph: EvidenceArtifactGraph,
) -> EvidenceContradictionFinding | None:
    codes = _values_from_fields(
        record.payload,
        _CONTRADICTION_FIELDS,
    )
    if not codes:
        return None

    target_ids = tuple(
        sorted(
            relationship.target_artifact_id
            for relationship in graph.outgoing(
                record.artifact_id
            )
            if relationship.relation
            is EvidenceRelation.CONTRADICTS
        )
    )

    return EvidenceContradictionFinding(
        artifact_id=record.artifact_id,
        artifact_type=record.artifact_type,
        contradiction_codes=codes,
        target_artifact_ids=target_ids,
        status=_payload_label(
            record.payload,
            (
                "contradiction_status",
                "status",
                "state",
                "decision",
            ),
            "UNSPECIFIED",
        ),
        relative_path=record.relative_path,
        content_sha256=record.content_sha256,
    )


def _ai_evidence_for_record(
    record: ConsoleArtifactRecord,
) -> EvidenceAIDrilldown | None:
    if record.artifact_type not in _AI_ARTIFACT_TYPES:
        return None

    return EvidenceAIDrilldown(
        artifact_id=record.artifact_id,
        artifact_type=record.artifact_type,
        model_label=_payload_label(
            record.payload,
            (
                "model_name",
                "model_id",
                "provider",
                "model",
                "evaluator_model",
            ),
            "UNSPECIFIED",
        ),
        prompt_version=_payload_label(
            record.payload,
            (
                "prompt_version",
                "prompt_id",
                "prompt_model_version",
                "schema_version",
            ),
            "UNSPECIFIED",
        ),
        evaluation_state=_payload_label(
            record.payload,
            (
                "evaluation_status",
                "status",
                "result",
                "decision",
                "outcome",
            ),
            "UNSPECIFIED",
        ),
        evidence_keys=_payload_keys(record.payload),
        relative_path=record.relative_path,
        content_sha256=record.content_sha256,
    )


def _count_values(
    groups: Tuple[Tuple[str, ...], ...],
) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for group in groups:
        for value in group:
            counts[value] = counts.get(value, 0) + 1
    return MappingProxyType(dict(sorted(counts.items())))


def build_evidence_risk_ai_dossier(
    read_model: ConsoleReadModel,
    graph: EvidenceArtifactGraph,
) -> EvidenceRiskAIDossier:
    if graph.correlation_id != read_model.correlation_id:
        raise ValueError(
            "evidence graph and read model correlation mismatch"
        )

    graph_node_ids = {
        node.artifact_id for node in graph.nodes
    }
    record_ids = {
        record.artifact_id
        for record in read_model.artifact_records
    }
    if graph_node_ids != record_ids:
        raise ValueError(
            "evidence graph and read model artifact mismatch"
        )

    records = tuple(
        sorted(
            read_model.artifact_records,
            key=lambda item: (
                item.artifact_type,
                item.artifact_id,
            ),
        )
    )

    risk_findings = tuple(
        finding
        for record in records
        for finding in _risk_findings_for_record(record)
    )

    contradiction_findings = tuple(
        finding
        for finding in (
            _contradiction_finding_for_record(
                record,
                graph,
            )
            for record in records
        )
        if finding is not None
    )

    ai_evidence = tuple(
        item
        for item in (
            _ai_evidence_for_record(record)
            for record in records
        )
        if item is not None
    )

    ai_counts: dict[str, int] = {}
    for item in ai_evidence:
        ai_counts[item.artifact_type] = (
            ai_counts.get(item.artifact_type, 0) + 1
        )

    state = (
        "AVAILABLE"
        if (
            risk_findings
            or contradiction_findings
            or ai_evidence
        )
        else "NO_REGISTERED_RISK_AI_EVIDENCE"
    )

    return EvidenceRiskAIDossier(
        correlation_id=read_model.correlation_id,
        state=state,
        risk_findings=risk_findings,
        contradiction_findings=contradiction_findings,
        ai_evidence=ai_evidence,
        risk_flag_counts=_count_values(
            tuple(
                item.risk_flags
                for item in risk_findings
            )
        ),
        contradiction_code_counts=_count_values(
            tuple(
                item.contradiction_codes
                for item in contradiction_findings
            )
        ),
        ai_artifact_type_counts=ai_counts,
    )
