from scripts.v2_implementation_order_registry import (
    IMPLEMENTATION_STAGES,
    ImplementationStage,
    validate_implementation_order,
)


def test_d4_authoritative_order_passes():
    report = validate_implementation_order()

    assert report.status == "PASS"
    assert report.stage_count == 12
    assert IMPLEMENTATION_STAGES[0].stage_id == "READ-ONLY-DATA-GATEWAY-APP-1"
    assert IMPLEMENTATION_STAGES[-1].stage_id == "DEFERRED-LEARNING-P4"


def test_d4_invalid_order_is_blocked():
    invalid = (
        ImplementationStage(2, "SECOND", ("x",)),
        ImplementationStage(1, "FIRST", ("y",)),
    )

    report = validate_implementation_order(invalid)

    assert report.status == "BLOCKED"
    assert "NON_CONTIGUOUS_ORDER" in report.reason_codes
    assert "INVALID_FIRST_RUNTIME_STAGE" in report.reason_codes
