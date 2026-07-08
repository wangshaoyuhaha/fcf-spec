from sidecars.sidecar_dag_dependency_guard_app_1 import scan_import_boundary_text


def test_d4_scanner_allows_safety_boundary_text():
    findings = scan_import_boundary_text(
        "docs/example.md",
        "- no real trading\n- no exchange API\n- no API key\n",
    )

    assert findings == ()


def test_d4_scanner_blocks_enabled_real_trading_assignment():
    findings = scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "real_trading = True\n",
    )

    assert len(findings) == 1
    assert findings[0].pattern == "real_trading"


def test_d4_scanner_blocks_enabled_exchange_api_assignment():
    findings = scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "exchange_api = True\n",
    )

    assert len(findings) == 1
    assert findings[0].pattern == "exchange_api"


def test_d4_scanner_blocks_api_key_assignment():
    findings = scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "api_key = 'forbidden'\n",
    )

    assert len(findings) == 1
    assert findings[0].pattern == "api_key"
