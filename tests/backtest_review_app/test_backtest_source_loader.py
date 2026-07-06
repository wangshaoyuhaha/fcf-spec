from pathlib import Path

from backtest_review_app.source_loader import (
    STAGE_ID,
    BacktestSourceSpec,
    build_backtest_source_manifest,
    default_backtest_source_specs,
    load_local_backtest_source_metadata,
)


def test_default_backtest_source_specs_include_required_source_kinds():
    kinds = {spec.source_kind for spec in default_backtest_source_specs()}
    assert kinds == {
        "report_archive_outputs",
        "market_scenario_outputs",
        "operator_review_outputs",
        "data_quality_ops_outputs",
        "ui_ai_stock_handoff_metadata",
    }


def test_load_local_backtest_source_metadata_discovers_matching_files(tmp_path: Path):
    report_dir = tmp_path / "runtime" / "report_archive_app"
    report_dir.mkdir(parents=True)
    report_file = report_dir / "archive_packet.json"
    report_file.write_text('{"id":"archive"}', encoding="utf-8")

    scenario_dir = tmp_path / "runtime" / "market_scenario_app"
    scenario_dir.mkdir(parents=True)
    scenario_file = scenario_dir / "scenario_packet.json"
    scenario_file.write_text('{"id":"scenario"}', encoding="utf-8")

    records = load_local_backtest_source_metadata(tmp_path)

    assert len(records) == 2
    assert {record.source_kind for record in records} == {
        "report_archive_outputs",
        "market_scenario_outputs",
    }
    assert {record.relative_path for record in records} == {
        "runtime/report_archive_app/archive_packet.json",
        "runtime/market_scenario_app/scenario_packet.json",
    }


def test_load_local_backtest_source_metadata_is_metadata_only(tmp_path: Path):
    source_dir = tmp_path / "runtime" / "operator_review_app"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "review_packet.json"
    source_file.write_text('{"secret":"not loaded"}', encoding="utf-8")

    records = load_local_backtest_source_metadata(tmp_path)
    record_dict = records[0].to_dict()

    assert record_dict["content_read_allowed"] is False
    assert "secret" not in record_dict
    assert "content" not in record_dict


def test_load_local_backtest_source_metadata_forbids_source_mutation_and_account_access(tmp_path: Path):
    source_dir = tmp_path / "runtime" / "data_quality_ops_app"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "ops_packet.json"
    source_file.write_text('{"id":"ops"}', encoding="utf-8")

    record = load_local_backtest_source_metadata(tmp_path)[0]

    assert record.source_content_mutation_allowed is False
    assert record.source_deletion_allowed is False
    assert record.source_overwrite_allowed is False
    assert record.real_account_access_allowed is False
    assert record.real_position_access_allowed is False


def test_build_backtest_source_manifest_has_safety_flags(tmp_path: Path):
    source_dir = tmp_path / "runtime" / "stock_app"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "ranked_watchlist.json"
    source_file.write_text('{"id":"stock"}', encoding="utf-8")

    manifest = build_backtest_source_manifest(tmp_path)

    assert manifest["stage_id"] == STAGE_ID
    assert manifest["source_count"] == 1
    assert manifest["source_kinds_found"] == ["ui_ai_stock_handoff_metadata"]
    assert manifest["safety_flags"]["read_only"] is True
    assert manifest["safety_flags"]["content_read_allowed"] is False
    assert manifest["safety_flags"]["real_trading_allowed"] is False
    assert manifest["safety_flags"]["real_execution_allowed"] is False
    assert manifest["safety_flags"]["real_account_access_allowed"] is False
    assert manifest["safety_flags"]["real_position_access_allowed"] is False


def test_custom_backtest_source_spec_is_supported(tmp_path: Path):
    custom_dir = tmp_path / "runtime" / "custom_backtest"
    custom_dir.mkdir(parents=True)
    custom_file = custom_dir / "source.json"
    custom_file.write_text("{}", encoding="utf-8")

    records = load_local_backtest_source_metadata(
        tmp_path,
        specs=[
            BacktestSourceSpec(
                source_kind="custom_backtest_source",
                relative_globs=["runtime/custom_backtest/*.json"],
            )
        ],
    )

    assert len(records) == 1
    assert records[0].source_kind == "custom_backtest_source"
    assert records[0].relative_path == "runtime/custom_backtest/source.json"
    assert len(records[0].source_id) == 16
