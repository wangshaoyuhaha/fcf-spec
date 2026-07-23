import json
from copy import deepcopy
from pathlib import Path

from scripts.control_center_future_capability_intake_guard import (
    ALLOWED_STATUSES,
    REQUIRED_SEEDED_PROPOSALS,
    build_future_capability_intake_guard_report,
    main,
    validate_intake_register,
)


ROOT = Path(__file__).resolve().parents[1]


def _proposal(**updates):
    values = {
        "proposal_id": "FCF-FCP-0001",
        "title": "Example future research module",
        "summary": "Preserve a future idea before architecture review.",
        "source": "operator",
        "submitted_at_utc": "2026-07-17T00:00:00Z",
        "status": "PROPOSED",
        "operator_decision": "PENDING",
        "architecture_refs": [],
        "adr_refs": [],
        "gap_refs": [],
        "evidence_refs": [],
        "phase_id": "NONE",
        "supersedes": [],
    }
    values.update(updates)
    return values


def _register(*proposals, next_sequence=2):
    return {
        "allowed_statuses": list(ALLOWED_STATUSES),
        "next_proposal_sequence": next_sequence,
        "proposals": list(proposals),
        "register_id": "FCF-FUTURE-CAPABILITY-INTAKE",
        "schema_version": 1,
    }


def test_future_capability_intake_guard_passes_repository():
    report = build_future_capability_intake_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_future_capability_intake_guard_main_passes():
    assert main() == 0


def test_registered_proposals_are_durable_and_non_authorizing():
    path = ROOT / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json"
    data = json.loads(path.read_text(encoding="ascii"))

    assert data["next_proposal_sequence"] == 91
    assert {
        item["proposal_id"]: item["status"] for item in data["proposals"]
    } == REQUIRED_SEEDED_PROPOSALS
    assert all(item["phase_id"] == "NONE" for item in data["proposals"])
    decisions = {
        item["proposal_id"]: item["operator_decision"]
        for item in data["proposals"]
    }
    assert all(
        decisions[proposal_id] == "PENDING"
        for proposal_id in ("FCF-FCP-0001", "FCF-FCP-0002", "FCF-FCP-0003")
    )
    assert decisions["FCF-FCP-0004"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0005"] == "PENDING"
    assert decisions["FCF-FCP-0006"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0007"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0008"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0009"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0010"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0011"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0012"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0013"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0014"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0015"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0016"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0017"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0018"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0019"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0020"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0021"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0022"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0023"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0024"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0025"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0026"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0027"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0028"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0029"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0030"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0031"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0032"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0033"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0034"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0035"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0036"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0037"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0038"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0039"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0040"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0041"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0042"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0043"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0044"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0045"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0046"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0047"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0048"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0049"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0050"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0051"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0052"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0053"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0054"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0055"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0056"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0057"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0058"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0059"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0060"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0061"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0062"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0063"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0064"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0065"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0066"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0067"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0068"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0069"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0070"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0071"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0072"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0073"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0074"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0075"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0076"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0077"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0078"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0079"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0080"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0081"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0082"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0083"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0084"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0085"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0086"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0087"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0088"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0089"] == "ACCEPTED_ARCHITECTURE"
    assert decisions["FCF-FCP-0090"] == "ACCEPTED_ARCHITECTURE"
    assert all(validate_intake_register(data).values())


def test_proposed_item_does_not_require_or_imply_phase_approval():
    register = json.loads(
        (ROOT / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
            encoding="ascii"
        )
    )
    proposal = _proposal(
        proposal_id="FCF-FCP-0091",
        submitted_at_utc="2026-07-23T06:01:00Z",
    )
    register["proposals"].append(proposal)
    register["next_proposal_sequence"] = 92
    checks = validate_intake_register(register)

    assert all(checks.values())


def test_approved_item_requires_operator_decision_and_named_phase():
    unsafe = _proposal(status="APPROVED_FOR_PHASE")
    checks = validate_intake_register(_register(unsafe))

    assert checks["approval_and_implementation_gates_valid"] is False


def test_implemented_item_requires_registered_evidence():
    unsafe = _proposal(
        status="IMPLEMENTED",
        operator_decision="APPROVED",
        phase_id="V2-R9",
    )
    checks = validate_intake_register(_register(unsafe))

    assert checks["approval_and_implementation_gates_valid"] is False


def test_proposal_ids_cannot_be_duplicated_or_have_a_deleted_gap():
    duplicate = _register(_proposal(), deepcopy(_proposal()), next_sequence=3)
    missing = _register(
        _proposal(proposal_id="FCF-FCP-0002"),
        next_sequence=3,
    )

    assert validate_intake_register(duplicate)[
        "proposal_ids_append_only_and_contiguous"
    ] is False
    assert validate_intake_register(missing)[
        "proposal_ids_append_only_and_contiguous"
    ] is False


def test_unknown_status_and_unsafe_reference_are_rejected():
    unknown = _register(_proposal(status="UNKNOWN"))
    unsafe = _register(_proposal(gap_refs=["unsafe reference"]))

    assert validate_intake_register(unknown)["proposal_rows_valid"] is False
    assert validate_intake_register(unsafe)["proposal_rows_valid"] is False
