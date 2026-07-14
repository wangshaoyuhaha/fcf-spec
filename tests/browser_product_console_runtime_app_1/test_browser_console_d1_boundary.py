
from dataclasses import replace
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY,
    ConsoleRuntimeConfig,
)


def test_d1_default_boundary_preserves_authority():
    boundary = BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY

    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority is True
    assert boundary.ai_advisory_only is True
    assert boundary.external_network_binding_allowed is False
    assert boundary.real_execution_allowed is False


def test_d1_boundary_rejects_external_network_binding():
    with pytest.raises(
        ValueError,
        match="prohibited console capability",
    ):
        replace(
            BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY,
            external_network_binding_allowed=True,
        )


def test_d1_config_requires_exact_ipv4_loopback(tmp_path: Path):
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        ConsoleRuntimeConfig(
            allowed_root=tmp_path,
            host="0.0.0.0",
        )


def test_d1_config_rejects_privileged_port(tmp_path: Path):
    with pytest.raises(ValueError, match="between 1024 and 65535"):
        ConsoleRuntimeConfig(
            allowed_root=tmp_path,
            port=80,
        )
