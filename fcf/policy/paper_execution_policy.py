from typing import Any, Dict, List, Optional, Tuple

GATE_NAME = "paper_execution_policy"
GATE_VERSION = "0.1.0"

DECISION_ALLOWED = "allowed"
DECISION_DENIED = "denied"

ERROR_TYPE_POLICY_DENY = "PolicyDeny"

DENY_RULES = {
    "real_execution_requested": "real execution is not allowed",
    "real_order": "real order is not allowed",
    "real_exchange_api": "real exchange API access is not allowed",
    "save_api_key_requested": "saving exchange API keys is not allowed",
    "read_private_key_requested": "reading wallet private keys is not allowed",
    "bypass_risk_requested": "bypassing risk controls is not allowed",
    "force_execute_requested": "force execution is not allowed",
    "convert_paper_to_real_requested": "converting paper order to real order is not allowed",
    "place_real_order_requested": "placing real orders is not allowed",
    "connect_exchange_requested": "connecting to real exchange is not allowed",
}

SAFE_BOUNDARY = {
    "execution_mode": "paper",
    "real_order": False,
    "real_execution": False,
    "real_exchange_api": False,
    "real_money_impact": False,
    "no_real_exchange_api": True,
    "no_real_order_placement": True,
    "no_secret_storage": True,
    "policy_gate_required": True,
}


def describe_paper_execution_policy() -> Dict[str, Any]:
    return {
        "gate": GATE_NAME,
        "gate_version": GATE_VERSION,
        "deny_rules": dict(DENY_RULES),
        "decision_values": [
            DECISION_ALLOWED,
            DECISION_DENIED,
        ],
        "stable_response_fields": [
            "ok",
            "gate",
            "gate_version",
            "decision",
            "error",
            "data",
        ],
        "safe_boundary": dict(SAFE_BOUNDARY),
    }


def _truthy(value: Any) -> bool:
    if value is True:
        return True

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "y",
            "1",
            "on",
        }

    if isinstance(value, (int, float)):
        return value == 1

    return False


def _candidate_containers(request: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    containers: List[Tuple[str, Dict[str, Any]]] = [
        ("request", request),
    ]

    metadata = request.get("metadata")
    if isinstance(metadata, dict):
        containers.append(("request.metadata", metadata))

    raw_order = request.get("raw_order")
    if isinstance(raw_order, dict):
        containers.append(("raw_order", raw_order))

        raw_order_metadata = raw_order.get("metadata")
        if isinstance(raw_order_metadata, dict):
            containers.append(("raw_order.metadata", raw_order_metadata))

    return containers


def _find_policy_violation(request: Dict[str, Any]) -> Optional[Dict[str, str]]:
    for location, container in _candidate_containers(request):
        for field, message in DENY_RULES.items():
            if _truthy(container.get(field)):
                return {
                    "field": field,
                    "location": location,
                    "message": message,
                }

    return None


def _allowed_response(request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "gate": GATE_NAME,
        "gate_version": GATE_VERSION,
        "decision": DECISION_ALLOWED,
        "error": None,
        "data": {
            "policy_allowed": True,
            "checked_fields": sorted(DENY_RULES.keys()),
            "safe_boundary": dict(SAFE_BOUNDARY),
            "request_summary": {
                "has_raw_order": isinstance(request.get("raw_order"), dict),
                "has_metadata": isinstance(request.get("metadata"), dict),
            },
        },
    }


def _denied_response(violation: Dict[str, str]) -> Dict[str, Any]:
    return {
        "ok": False,
        "gate": GATE_NAME,
        "gate_version": GATE_VERSION,
        "decision": DECISION_DENIED,
        "error": {
            "type": ERROR_TYPE_POLICY_DENY,
            "message": violation["message"],
        },
        "data": None,
        "policy_violation": {
            "field": violation["field"],
            "location": violation["location"],
            "message": violation["message"],
        },
        "safe_boundary": dict(SAFE_BOUNDARY),
    }


def evaluate_paper_execution_policy(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return {
            "ok": False,
            "gate": GATE_NAME,
            "gate_version": GATE_VERSION,
            "decision": DECISION_DENIED,
            "error": {
                "type": ERROR_TYPE_POLICY_DENY,
                "message": "policy request must be a dict",
            },
            "data": None,
            "policy_violation": {
                "field": "request",
                "location": "request",
                "message": "policy request must be a dict",
            },
            "safe_boundary": dict(SAFE_BOUNDARY),
        }

    violation = _find_policy_violation(request)
    if violation is not None:
        return _denied_response(violation)

    return _allowed_response(request)
