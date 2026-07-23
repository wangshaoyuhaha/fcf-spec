from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = Path("FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json")
PROTOCOL_PATH = Path("docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
ALLOWED_STATUSES = (
    "PROPOSED",
    "NEEDS_RESEARCH",
    "ACCEPTED_ARCHITECTURE",
    "DEFERRED",
    "REJECTED",
    "OUTSIDE_CURRENT_AUTHORIZATION",
    "APPROVED_FOR_PHASE",
    "IMPLEMENTED",
    "SUPERSEDED",
)
REQUIRED_PROPOSAL_FIELDS = frozenset(
    {
        "proposal_id",
        "title",
        "summary",
        "source",
        "submitted_at_utc",
        "status",
        "operator_decision",
        "architecture_refs",
        "adr_refs",
        "gap_refs",
        "evidence_refs",
        "phase_id",
        "supersedes",
    }
)
_PROPOSAL_ID = re.compile(r"^FCF-FCP-([0-9]{4})$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
REQUIRED_SEEDED_PROPOSALS = {
    "FCF-FCP-0001": "NEEDS_RESEARCH",
    "FCF-FCP-0002": "NEEDS_RESEARCH",
    "FCF-FCP-0003": "NEEDS_RESEARCH",
    "FCF-FCP-0004": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0005": "NEEDS_RESEARCH",
    "FCF-FCP-0006": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0007": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0008": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0009": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0010": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0011": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0012": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0013": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0014": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0015": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0016": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0017": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0018": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0019": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0020": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0021": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0022": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0023": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0024": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0025": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0026": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0027": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0028": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0029": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0030": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0031": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0032": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0033": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0034": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0035": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0036": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0037": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0038": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0039": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0040": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0041": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0042": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0043": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0044": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0045": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0046": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0047": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0048": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0049": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0050": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0051": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0052": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0053": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0054": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0055": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0056": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0057": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0058": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0059": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0060": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0061": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0062": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0063": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0064": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0065": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0066": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0067": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0068": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0069": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0070": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0071": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0072": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0073": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0074": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0075": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0076": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0077": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0078": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0079": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0080": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0081": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0082": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0083": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0084": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0085": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0086": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0087": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0088": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0089": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0090": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0091": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0092": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0093": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0094": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0095": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0096": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0097": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0098": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0099": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0100": "ACCEPTED_ARCHITECTURE",
    "FCF-FCP-0101": "APPROVED_FOR_PHASE",
}


def _is_utc(value: object) -> bool:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return (
        parsed.tzinfo is not None
        and parsed.utcoffset() is not None
        and parsed.utcoffset().total_seconds() == 0
    )


def _safe_identifier_sequence(value: object) -> bool:
    return (
        isinstance(value, list)
        and value == sorted(set(value))
        and all(
            isinstance(item, str) and _SAFE_ID.fullmatch(item) is not None
            for item in value
        )
    )


def validate_intake_register(data: object) -> dict[str, bool]:
    if not isinstance(data, dict):
        return {"register_shape_valid": False}
    proposals = data.get("proposals")
    statuses = data.get("allowed_statuses")
    next_sequence = data.get("next_proposal_sequence")
    base = {
        "identity_exact": data.get("schema_version") == 1
        and data.get("register_id") == "FCF-FUTURE-CAPABILITY-INTAKE",
        "status_vocabulary_exact": statuses == list(ALLOWED_STATUSES),
        "proposals_are_list": isinstance(proposals, list),
        "next_sequence_is_positive": isinstance(next_sequence, int)
        and not isinstance(next_sequence, bool)
        and next_sequence >= 1,
    }
    if not all(base.values()):
        return base
    assert isinstance(proposals, list)
    assert isinstance(next_sequence, int)
    found_sequences: list[int] = []
    rows_valid = True
    approval_gate_valid = True
    for proposal in proposals:
        if not isinstance(proposal, dict):
            rows_valid = False
            continue
        if not REQUIRED_PROPOSAL_FIELDS.issubset(proposal):
            rows_valid = False
            continue
        match = _PROPOSAL_ID.fullmatch(str(proposal.get("proposal_id", "")))
        if match is None:
            rows_valid = False
            continue
        found_sequences.append(int(match.group(1)))
        title = str(proposal.get("title", "")).strip()
        summary = str(proposal.get("summary", "")).strip()
        status = proposal.get("status")
        phase_id = proposal.get("phase_id")
        operator_decision = proposal.get("operator_decision")
        if (
            not title
            or not summary
            or len(title) > 160
            or len(summary) > 2000
            or status not in ALLOWED_STATUSES
            or not _is_utc(proposal.get("submitted_at_utc"))
            or _SAFE_ID.fullmatch(str(proposal.get("source", ""))) is None
            or _SAFE_ID.fullmatch(str(operator_decision)) is None
            or _SAFE_ID.fullmatch(str(phase_id)) is None
            or not all(
                _safe_identifier_sequence(proposal.get(field_name))
                for field_name in (
                    "architecture_refs",
                    "adr_refs",
                    "gap_refs",
                    "evidence_refs",
                    "supersedes",
                )
            )
        ):
            rows_valid = False
        if status == "APPROVED_FOR_PHASE" and (
            phase_id == "NONE" or operator_decision != "APPROVED"
        ):
            approval_gate_valid = False
        if status == "IMPLEMENTED" and (
            phase_id == "NONE"
            or operator_decision != "APPROVED"
            or not proposal.get("evidence_refs")
        ):
            approval_gate_valid = False
    expected_sequences = list(range(1, next_sequence))
    proposal_statuses = {
        str(proposal.get("proposal_id")): proposal.get("status")
        for proposal in proposals
        if isinstance(proposal, dict)
    }
    return {
        **base,
        "proposal_rows_valid": rows_valid,
        "proposal_ids_append_only_and_contiguous": (
            sorted(found_sequences) == expected_sequences
            and len(found_sequences) == len(set(found_sequences))
        ),
        "approval_and_implementation_gates_valid": approval_gate_valid,
        "seeded_research_proposals_preserved": all(
            proposal_statuses.get(proposal_id) == status
            for proposal_id, status in REQUIRED_SEEDED_PROPOSALS.items()
        ),
    }


def build_future_capability_intake_guard_report(
    root: Path = ROOT,
) -> dict[str, object]:
    try:
        register_text = (root / REGISTER_PATH).read_text(encoding="ascii")
        protocol = (root / PROTOCOL_PATH).read_text(encoding="ascii")
        data = json.loads(register_text)
        ascii_and_json = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        register_text = ""
        protocol = ""
        data = {}
        ascii_and_json = False
    checks = {
        "files_ascii_and_json": ascii_and_json,
        "deterministic_json": register_text
        == json.dumps(data, indent=2, sort_keys=True) + "\n",
        "protocol_preserves_history": (
            "never reused, reordered, or deleted." in protocol
            and "An intake record alone cannot" in protocol
            and "APPROVED_FOR_PHASE" in protocol
        ),
        **validate_intake_register(data),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_future_capability_intake_guard_report()
    if report["ok"] is not True:
        raise SystemExit("future capability intake guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
