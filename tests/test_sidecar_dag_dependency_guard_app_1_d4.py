from sidecars.sidecar_dag_dependency_guard_app_1 import (
    build_import_boundary_scan_report,
    classify_import_boundary_path,
    scan_import_boundary_text,
)


def test_d4_classifies_core_path():
    assert classify_import_boundary_path("core/example.py") == "core"


def test_d4_classifies_sidecar_path():
    assert classify_import_boundary_path("sidecars/example_app/__init__.py") == "sidecar"


def test_d4_core_importing_sidecars_is_blocked():
    findings = scan_import_boundary_text(
        "core/example.py",
        "from sidecars.example_app import helper\n",
    )

    assert len(findings) >= 1
    assert findings[0].finding_type == "core_sidecar_import_violation"


def test_d4_sidecar_importing_sidecar_keyword_is_allowed():
    findings = scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "from sidecars.other_app import helper\n",
    )

    assert findings == ()


def test_d4_blocks_real_trading_keyword():
    findings = scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "real_trading = True\n",
    )

    assert len(findings) == 1
    assert findings[0].pattern == "real_trading"


def test_d4_blocks_api_key_keyword():
    findings = scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "api_key = 'forbidden'\n",
    )

    assert len(findings) == 1
    assert findings[0].pattern == "api_key"


def test_d4_builds_valid_scan_report():
    report = build_import_boundary_scan_report(
        {
            "sidecars/example_app/__init__.py": "paper_only = True\nread_only = True\n",
            "tests/test_example.py": "assert True\n",
        }
    )

    assert report.valid is True
    assert report.scanned_file_count == 2
    assert report.finding_count == 0
    assert report.findings == ()


def test_d4_builds_invalid_scan_report():
    report = build_import_boundary_scan_report(
        {
            "core/example.py": "import sidecars\n",
            "sidecars/example_app/__init__.py": "exchange_api = True\n",
        }
    )

    assert report.valid is False
    assert report.scanned_file_count == 2
    assert report.finding_count >= 2
