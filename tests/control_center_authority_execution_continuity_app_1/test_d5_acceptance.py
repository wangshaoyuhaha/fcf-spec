from pathlib import Path

from scripts.control_center_active_authority_sync_guard import (
    AuthorityBaseline,
    assert_authority_sync_pass,
    build_authority_sync_report,
    inspect_active_authority,
)
from scripts.v2_implementation_order_registry import (
    validate_implementation_order,
)


ROOT = Path(__file__).resolve().parents[2]


def test_d5_complete_governance_acceptance():
    baseline = AuthorityBaseline(
        phase_id="BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1",
        main_merge_commit="2cfe860ac8c9847819557da1fbb405b7e3952eaa",
        d6_commit="7083f16e7a1bb030f03f09b63f53c9fc7a110f83",
        final_marker=(
            "BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1 "
            "FINAL SYNC START"
        ),
    )
    sync_report = build_authority_sync_report(
        inspect_active_authority(ROOT, baseline)
    )
    order_report = validate_implementation_order()

    assert_authority_sync_pass(sync_report)
    assert order_report.status == "PASS"
    assert (
        ROOT
        / "FCF_CURRENT_STATE_BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_APP_1_FINAL.md"
    ).is_file()
