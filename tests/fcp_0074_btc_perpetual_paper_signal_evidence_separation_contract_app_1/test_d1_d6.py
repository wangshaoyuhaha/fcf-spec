from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0074_btc_perpetual_paper_signal_evidence_separation_contract_app_1 as fcp_0074
from apps.fcp_0074_btc_perpetual_paper_signal_evidence_separation_contract_app_1 import (
    EVIDENCE_DOMAIN_ORDER,
    BTCPerpetualPaperEvidenceReference,
    build_btc_perpetual_paper_signal_evidence_separation_contract,
)


def _references():
    return tuple(
        BTCPerpetualPaperEvidenceReference(
            artifact_id=f"btc-evidence-{index}",
            artifact_hash=f"{index:x}" * 64,
            domain=domain,
            observed_at_utc=f"2026-07-22T13:{index:02d}:00Z",
        )
        for index, domain in enumerate(EVIDENCE_DOMAIN_ORDER, start=1)
    )


def _contract(references=None, **changes):
    values = {
        "references": _references() if references is None else references,
        "created_at_utc": "2026-07-22T14:00:00Z",
    }
    values.update(changes)
    return build_btc_perpetual_paper_signal_evidence_separation_contract(**values)


def test_closed_domain_order_is_exact():
    assert EVIDENCE_DOMAIN_ORDER == (
        "REUSABLE_MARKET_SIGNAL",
        "CONTRACT_SEMANTICS",
        "LEVERAGE_MARGIN",
        "COST_FUNDING_EXECUTION",
        "LIQUIDATION_RISK",
        "OUTCOME_ACCOUNTING",
    )


def test_complete_contract_preserves_reference_order_and_hashes():
    references = _references()
    contract = _contract(references)
    assert contract.references == references
    assert contract.reference_hashes == tuple(item.reference_hash for item in references)
    assert len(contract.contract_hash) == 64


def test_only_market_signal_domain_is_reusable():
    contract = _contract()
    assert contract.reusable_reference_hashes == (contract.references[0].reference_hash,)
    assert contract.derivative_reference_hashes == tuple(
        item.reference_hash for item in contract.references[1:]
    )


def test_reference_and_contract_are_deterministic():
    assert _references() == _references()
    assert _contract().contract_hash == _contract().contract_hash


def test_contract_hash_changes_with_registered_reference():
    references = list(_references())
    references[0] = replace(references[0], artifact_id="btc-evidence-revised")
    assert _contract().contract_hash != _contract(tuple(references)).contract_hash


@pytest.mark.parametrize("field,value", (("artifact_id", "unsafe value"), ("artifact_hash", "0" * 63)))
def test_reference_rejects_invalid_identity(field, value):
    values = {
        "artifact_id": "btc-evidence-1",
        "artifact_hash": "1" * 64,
        "domain": EVIDENCE_DOMAIN_ORDER[0],
        "observed_at_utc": "2026-07-22T13:01:00Z",
    }
    values[field] = value
    with pytest.raises(ValueError):
        BTCPerpetualPaperEvidenceReference(**values)


def test_reference_rejects_unknown_domain():
    with pytest.raises(ValueError, match="domain is not registered"):
        replace(_references()[0], domain="DERIVED_SIGNAL")


def test_reference_rejects_unregistered_artifact():
    with pytest.raises(ValueError, match="registered artifact"):
        replace(_references()[0], registered_artifact=False)


def test_contract_rejects_untyped_reference():
    with pytest.raises(ValueError, match="exact typed references"):
        _contract((object(),))


def test_contract_rejects_missing_domain():
    with pytest.raises(ValueError, match="complete closed domain order"):
        _contract(_references()[:-1])


def test_contract_rejects_reordered_domains():
    references = list(_references())
    references[0], references[1] = references[1], references[0]
    with pytest.raises(ValueError, match="complete closed domain order"):
        _contract(tuple(references))


@pytest.mark.parametrize("field", ("artifact_id", "artifact_hash"))
def test_contract_rejects_duplicate_artifact_identity(field):
    references = list(_references())
    references[1] = replace(references[1], **{field: getattr(references[0], field)})
    with pytest.raises(ValueError, match="must be unique"):
        _contract(tuple(references))


def test_contract_rejects_time_regression():
    with pytest.raises(ValueError, match="cannot precede"):
        _contract(created_at_utc="2026-07-22T13:05:30Z")


@pytest.mark.parametrize(
    "field,value",
    (
        ("complete_domain_coverage", False),
        ("separation_only", False),
        ("signal_calculation_allowed", True),
        ("factor_promotion_allowed", True),
        ("strategy_selection_allowed", True),
        ("profitability_claim_allowed", True),
        ("account_state_allowed", True),
        ("order_allowed", True),
        ("execution_allowed", True),
        ("gap_closed", True),
    ),
)
def test_contract_rejects_authority_escalation(field, value):
    with pytest.raises(ValueError, match="cannot calculate, promote, select, claim, act, or close"):
        replace(_contract(), **{field: value})


@pytest.mark.parametrize(
    "field,value",
    (
        ("calculation_authority", "AI"),
        ("evidence_authority", "UNREGISTERED"),
        ("ai_role", "DECISION_AUTHORITY"),
    ),
)
def test_contract_rejects_authority_identity_substitution(field, value):
    with pytest.raises(ValueError, match="authority identities"):
        replace(_contract(), **{field: value})


def test_contract_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _contract().contract_id = "changed"


def test_package_exports_are_closed():
    assert fcp_0074.__all__ == [
        "EVIDENCE_DOMAIN_ORDER",
        "BTCPerpetualPaperEvidenceReference",
        "BTCPerpetualPaperSignalEvidenceSeparationContract",
        "build_btc_perpetual_paper_signal_evidence_separation_contract",
    ]
