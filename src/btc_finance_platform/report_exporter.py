from pathlib import Path


def export_paper_report(report: str, output_path: str) -> dict:
    path = Path(output_path)

    if not report or not isinstance(report, str):
        raise ValueError("report is required")

    if "NO_LIVE_ACTION" not in report:
        raise AssertionError("paper report must include NO_LIVE_ACTION")

    if "no real order" not in report:
        raise AssertionError("paper report must include no real order safety text")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_report_export",
        "path": str(path),
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }
