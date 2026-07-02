from btc_finance_platform.safe_boundary import assert_safe_boundary, get_safe_boundary


def run_paper_runtime_check() -> dict:
    assert_safe_boundary()
    return {
        "ok": True,
        "project": "btc_finance_platform",
        "mode": "paper",
        "safe_boundary": get_safe_boundary(),
    }
