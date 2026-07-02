import subprocess


COMMANDS = [
    ["python", "scripts/run_safety_smoke.py"],
    ["python", "scripts/run_market_snapshot_smoke.py"],
    ["python", "scripts/run_decision_draft_smoke.py"],
    ["python", "scripts/run_operator_review_smoke.py"],
    ["python", "scripts/run_paper_pipeline_smoke.py"],
    ["python", "scripts/run_paper_analysis_report_smoke.py"],
    ["python", "scripts/run_integrated_report_smoke.py"],
    ["python", "scripts/run_analysis_flow_smoke.py"],
    ["python", "scripts/run_analysis_cli_smoke.py"],
    ["python", "scripts/run_paper_history_smoke.py"],
    ["python", "scripts/run_batch_analysis_smoke.py"],
    ["python", "scripts/run_batch_cli_smoke.py"],
    ["python", "scripts/run_batch_history_smoke.py"],
    ["python", "scripts/run_batch_quality_smoke.py"],
    ["python", "scripts/run_schema_validation_smoke.py"],
    ["python", "scripts/run_local_data_loader_smoke.py"],
    ["python", "scripts/run_local_data_bridge_smoke.py"],
    ["python", "main.py", "--symbol", "BTCUSDT", "--price", "65000"],
    ["python", "-m", "pytest", "-q"],
]


def run_command(command: list[str]) -> None:
    print("")
    print("== RUN:", " ".join(command), "==")
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    for command in COMMANDS:
        run_command(command)

    print("")
    print("== ALL CHECKS PASSED ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


