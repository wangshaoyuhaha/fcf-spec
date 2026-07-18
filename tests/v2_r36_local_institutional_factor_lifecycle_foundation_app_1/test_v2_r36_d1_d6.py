from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorDefinition
from apps.v2_r36_local_institutional_factor_lifecycle_foundation_app_1 import (
    InstitutionalFactorCandidate,
    LocalInstitutionalFactorLifecycleRegistry,
    OperatorLifecycleDecision,
    V2_R36_LOCAL_INSTITUTIONAL_FACTOR_LIFECYCLE_BOUNDARY,
    V2R36LocalInstitutionalFactorLifecycleBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_factor_lifecycle,
)


def _definition(**changes: object) -> FactorDefinition:
    values: dict[str, object] = {"factor_id": "institutional-liquidity", "version": "v1", "family": "FLOW", "lifecycle": "RESEARCH", "source_type": "REGISTERED_DERIVATION", "calculation_spec_hash": "a" * 64, "output_unit": "basis-points", "asset_scopes": ("a-share",), "input_field_ids": ("registered-flow",)}
    values.update(changes)
    return FactorDefinition(**values)  # type: ignore[arg-type]


def _candidate(**changes: object) -> InstitutionalFactorCandidate:
    values: dict[str, object] = {"candidate_id": "institutional-liquidity-candidate", "factor_definition": _definition(), "hypothesis_id": "institutional-liquidity-hypothesis", "submitted_at_utc": "2026-07-18T01:00:00Z", "expires_at_utc": "2026-08-18T01:00:00Z", "supporting_evidence_hashes": ("b" * 64,), "negative_evidence_hashes": ("c" * 64,)}
    values.update(changes)
    return InstitutionalFactorCandidate(**values)  # type: ignore[arg-type]


def _decision(index: int, source: str, target: str, predecessor: str | None = None) -> OperatorLifecycleDecision:
    return OperatorLifecycleDecision(decision_id=f"lifecycle-decision-{index}", candidate_id="institutional-liquidity-candidate", from_state=source, to_state=target, decided_at_utc=f"2026-07-{18 + index:02d}T02:00:00Z", operator_id="primary-operator", rationale_codes=(f"registered-review-{index}",), predecessor_decision_hash=predecessor)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R36_LOCAL_INSTITUTIONAL_FACTOR_LIFECYCLE_BOUNDARY
    assert not boundary.factor_activation_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R36LocalInstitutionalFactorLifecycleBoundary(automatic_approval_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.factor_activation_allowed = True  # type: ignore[misc]


def test_d2_candidate_requires_r11_definition():
    with pytest.raises(ValueError, match="R11 FactorDefinition"):
        _candidate(factor_definition=object())


def test_d2_candidate_cannot_activate_or_score():
    with pytest.raises(ValueError, match="cannot activate"):
        _candidate(calculation_activation_allowed=True)


def test_d2_decision_must_be_operator_authored():
    with pytest.raises(ValueError, match="Operator-authored"):
        replace(_decision(1, "RESEARCH_PROPOSAL", "CONTRACT_DEFINED"), automatic_decision=True)


def test_d3_illegal_transition_is_rejected():
    with pytest.raises(ValueError, match="illegal"):
        _decision(1, "RESEARCH_PROPOSAL", "OPERATOR_APPROVED")


def test_d3_predecessor_chain_is_required():
    first = _decision(1, "RESEARCH_PROPOSAL", "CONTRACT_DEFINED")
    second = _decision(2, "CONTRACT_DEFINED", "DATA_AVAILABLE", "a" * 64)
    with pytest.raises(ValueError, match="predecessor mismatch"):
        LocalInstitutionalFactorLifecycleRegistry((_candidate(),), (first, second))


def test_d3_registry_and_history_are_immutable():
    first = _decision(1, "RESEARCH_PROPOSAL", "CONTRACT_DEFINED")
    registry = LocalInstitutionalFactorLifecycleRegistry().append_candidate(_candidate()).append_decision(first)
    assert registry.history("institutional-liquidity-candidate") == (first,)
    with pytest.raises(FrozenInstanceError):
        registry.decisions = ()  # type: ignore[misc]


def test_d4_missing_candidate_state():
    snapshot = resolve_factor_lifecycle(LocalInstitutionalFactorLifecycleRegistry(), candidate_id="missing-candidate", as_of_utc="2026-07-20T00:00:00Z")
    assert snapshot.state == "MISSING"


def test_d4_current_state_uses_only_visible_decisions():
    first = _decision(1, "RESEARCH_PROPOSAL", "CONTRACT_DEFINED")
    registry = LocalInstitutionalFactorLifecycleRegistry((_candidate(),), (first,))
    snapshot = resolve_factor_lifecycle(registry, candidate_id="institutional-liquidity-candidate", as_of_utc="2026-07-18T12:00:00Z")
    assert snapshot.state == "RESEARCH_PROPOSAL" and not snapshot.decisions


def test_d5_rejection_history_is_preserved():
    rejection = _decision(1, "RESEARCH_PROPOSAL", "REJECTED")
    registry = LocalInstitutionalFactorLifecycleRegistry((_candidate(),), (rejection,))
    snapshot = resolve_factor_lifecycle(registry, candidate_id="institutional-liquidity-candidate", as_of_utc="2026-07-20T00:00:00Z")
    assert snapshot.state == "REJECTED" and snapshot.terminal and "REJECTED_HISTORY_PRESERVED" in snapshot.reason_codes


def test_d5_expiry_needs_operator_review_not_automatic_decision():
    snapshot = resolve_factor_lifecycle(LocalInstitutionalFactorLifecycleRegistry((_candidate(),)), candidate_id="institutional-liquidity-candidate", as_of_utc="2026-09-01T00:00:00Z")
    assert snapshot.state == "RESEARCH_PROPOSAL" and "EXPIRY_OPERATOR_REVIEW_REQUIRED" in snapshot.reason_codes


def test_d5_operator_approval_still_cannot_activate_factor():
    states = ("RESEARCH_PROPOSAL", "CONTRACT_DEFINED", "DATA_AVAILABLE", "POINT_IN_TIME_VALIDATED", "BACKTESTED", "ROBUSTNESS_REVIEWED", "OPERATOR_APPROVED")
    decisions = []
    predecessor = None
    for index, (source, target) in enumerate(zip(states, states[1:]), 1):
        item = _decision(index, source, target, predecessor)
        decisions.append(item)
        predecessor = item.decision_hash
    registry = LocalInstitutionalFactorLifecycleRegistry((_candidate(),), tuple(decisions))
    snapshot = resolve_factor_lifecycle(registry, candidate_id="institutional-liquidity-candidate", as_of_utc="2026-07-30T00:00:00Z")
    assert snapshot.state == "OPERATOR_APPROVED" and "NO_FACTOR_ACTIVATION" in snapshot.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    registry = LocalInstitutionalFactorLifecycleRegistry((_candidate(),))
    snapshot = resolve_factor_lifecycle(registry, candidate_id="institutional-liquidity-candidate", as_of_utc="2026-07-20T00:00:00Z")
    model, acceptance = build_read_model(registry), build_operator_acceptance(snapshot)
    assert isinstance(model.payload, MappingProxyType) and acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["factor_activation"] = True  # type: ignore[index]
