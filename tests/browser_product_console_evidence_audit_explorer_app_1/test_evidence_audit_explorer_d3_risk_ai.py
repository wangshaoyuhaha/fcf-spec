from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    ConsoleArtifactRecord,
    ConsoleReadModel,
    EvidenceRelation,
    build_evidence_artifact_graph,
    build_evidence_risk_ai_dossier,
)


def _record(
    artifact_id: str,
    artifact_type: str,
    payload: dict,
) -> ConsoleArtifactRecord:
    return ConsoleArtifactRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        relative_path=f"registered/{artifact_id}.json",
        content_sha256="b" * 64,
        payload=payload,
    )


def _model(
    records: tuple[ConsoleArtifactRecord, ...],
) -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-d3",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=tuple(
            record.artifact_id for record in records
        ),
        artifact_records=records,
    )


def _dossier(
    records: tuple[ConsoleArtifactRecord, ...],
):
    model = _model(records)
    graph = build_evidence_artifact_graph(model)
    return build_evidence_risk_ai_dossier(
        model,
        graph,
    )


def test_d3_extracts_explicit_artifact_risk_flags():
    dossier = _dossier(
        (
            _record(
                "risk-1",
                "risk_review",
                {
                    "symbol": "BTCUSDT",
                    "risk_flags": [
                        "VOLATILITY_HIGH",
                        "LIQUIDITY_THIN",
                    ],
                    "risk_level": "HIGH",
                },
            ),
        )
    )

    assert dossier.state == "AVAILABLE"
    assert len(dossier.risk_findings) == 1
    finding = dossier.risk_findings[0]
    assert finding.artifact_id == "risk-1"
    assert finding.subject == "BTCUSDT"
    assert finding.risk_flags == (
        "LIQUIDITY_THIN",
        "VOLATILITY_HIGH",
    )
    assert finding.severity == "HIGH"
    assert finding.relative_path == "registered/risk-1.json"
    assert finding.content_sha256 == "b" * 64


def test_d3_extracts_candidate_risk_flags_without_inference():
    dossier = _dossier(
        (
            _record(
                "watchlist-1",
                "ranked_watchlist",
                {
                    "candidates": [
                        {
                            "symbol": "AAA",
                            "risk_flags": [
                                "DATA_GAP",
                                "VOLATILITY_HIGH",
                            ],
                            "risk_level": "HIGH",
                        },
                        {
                            "symbol": "BBB",
                            "warning": "not_an_explicit_risk_flag",
                        },
                    ]
                },
            ),
        )
    )

    assert tuple(
        (item.subject, item.risk_flags)
        for item in dossier.risk_findings
    ) == (
        (
            "AAA",
            ("DATA_GAP", "VOLATILITY_HIGH"),
        ),
    )
    assert dict(dossier.risk_flag_counts) == {
        "DATA_GAP": 1,
        "VOLATILITY_HIGH": 1,
    }


def test_d3_extracts_contradiction_codes_and_registered_targets():
    dossier = _dossier(
        (
            _record(
                "candidate-1",
                "ranked_watchlist",
                {"candidates": []},
            ),
            _record(
                "challenge-1",
                "ai_evaluation",
                {
                    "contradiction_codes": [
                        "THESIS_CONFLICT",
                        "DATA_CONFLICT",
                    ],
                    "contradiction_status": "OPEN",
                    "contradicts_artifact_id": "candidate-1",
                    "model_name": "evaluator-model",
                },
            ),
        )
    )

    assert len(dossier.contradiction_findings) == 1
    finding = dossier.contradiction_findings[0]
    assert finding.contradiction_codes == (
        "DATA_CONFLICT",
        "THESIS_CONFLICT",
    )
    assert finding.target_artifact_ids == (
        "candidate-1",
    )
    assert finding.status == "OPEN"
    assert dict(dossier.contradiction_code_counts) == {
        "DATA_CONFLICT": 1,
        "THESIS_CONFLICT": 1,
    }


def test_d3_contradiction_relationship_remains_typed_in_graph():
    model = _model(
        (
            _record("source-1", "manifest", {}),
            _record(
                "challenge-1",
                "ai_evaluation",
                {
                    "contradiction_code": "SOURCE_CONFLICT",
                    "contradicts_artifact_id": "source-1",
                },
            ),
        )
    )
    graph = build_evidence_artifact_graph(model)

    relationship = graph.outgoing("challenge-1")[0]
    assert relationship.relation is EvidenceRelation.CONTRADICTS

    dossier = build_evidence_risk_ai_dossier(
        model,
        graph,
    )
    assert dossier.contradiction_findings[
        0
    ].target_artifact_ids == ("source-1",)


def test_d3_ai_drilldown_preserves_registered_identity():
    dossier = _dossier(
        (
            _record(
                "explanation-1",
                "ai_explanation",
                {
                    "model_name": "advisory-model-a",
                    "prompt_version": "prompt-v2",
                    "status": "GENERATED",
                    "rationale": "registered rationale",
                },
            ),
            _record(
                "evaluation-1",
                "ai_evaluation",
                {
                    "evaluator_model": "evaluator-model-b",
                    "schema_version": "eval-v1",
                    "evaluation_status": "PASS_WITH_REVIEW",
                    "score": 0.81,
                },
            ),
        )
    )

    assert tuple(
        item.artifact_id
        for item in dossier.ai_evidence
    ) == (
        "evaluation-1",
        "explanation-1",
    )
    assert tuple(
        item.model_label
        for item in dossier.ai_evidence
    ) == (
        "evaluator-model-b",
        "advisory-model-a",
    )
    assert tuple(
        item.prompt_version
        for item in dossier.ai_evidence
    ) == (
        "eval-v1",
        "prompt-v2",
    )
    assert tuple(
        item.evaluation_state
        for item in dossier.ai_evidence
    ) == (
        "PASS_WITH_REVIEW",
        "GENERATED",
    )
    assert all(
        item.ai_advisory_only
        and item.deterministic_authority
        and item.operator_review_required
        for item in dossier.ai_evidence
    )
    assert dict(dossier.ai_artifact_type_counts) == {
        "ai_evaluation": 1,
        "ai_explanation": 1,
    }


def test_d3_ai_drilldown_exposes_keys_not_mutable_payload():
    dossier = _dossier(
        (
            _record(
                "explanation-1",
                "ai_explanation",
                {
                    "model_name": "model-a",
                    "prompt_version": "p1",
                    "status": "GENERATED",
                    "rationale": "text",
                },
            ),
        )
    )

    assert dossier.ai_evidence[0].evidence_keys == (
        "model_name",
        "prompt_version",
        "rationale",
        "status",
    )
    assert not hasattr(
        dossier.ai_evidence[0],
        "payload",
    )


def test_d3_does_not_infer_unregistered_warning_fields():
    dossier = _dossier(
        (
            _record(
                "note-1",
                "research_note",
                {
                    "warning": "VOLATILITY_HIGH",
                    "concern": "DATA_CONFLICT",
                },
            ),
        )
    )

    assert dossier.state == (
        "NO_REGISTERED_RISK_AI_EVIDENCE"
    )
    assert dossier.risk_findings == ()
    assert dossier.contradiction_findings == ()
    assert dossier.ai_evidence == ()


@pytest.mark.parametrize(
    "payload",
    (
        {"risk_flags": {"bad": "mapping"}},
        {"risk_flags": [""]},
        {"contradiction_codes": {"bad": "mapping"}},
        {"contradiction_codes": ["../unsafe"]},
    ),
)
def test_d3_rejects_malformed_explicit_evidence(payload):
    with pytest.raises(ValueError):
        _dossier(
            (
                _record(
                    "bad-1",
                    "risk_review",
                    payload,
                ),
            )
        )


def test_d3_rejects_graph_read_model_mismatch():
    model_a = _model(
        (_record("artifact-a", "manifest", {}),)
    )
    model_b = _model(
        (_record("artifact-b", "manifest", {}),)
    )
    graph_b = build_evidence_artifact_graph(model_b)

    with pytest.raises(
        ValueError,
        match="artifact mismatch",
    ):
        build_evidence_risk_ai_dossier(
            model_a,
            graph_b,
        )


def test_d3_dossier_keeps_authority_flags_enabled():
    dossier = _dossier(
        (
            _record(
                "ai-1",
                "ai_explanation",
                {
                    "model_name": "model-a",
                    "status": "GENERATED",
                },
            ),
        )
    )

    assert dossier.registered_artifact_only is True
    assert dossier.read_only is True
    assert dossier.ai_advisory_only is True
    assert dossier.deterministic_authority is True
    assert dossier.operator_review_required is True
