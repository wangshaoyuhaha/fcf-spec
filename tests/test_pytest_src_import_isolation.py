from __future__ import annotations

import tomllib
from pathlib import Path

import fcf


ROOT = Path(__file__).resolve().parents[1]


def test_pytest_declares_src_import_path() -> None:
    configuration = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="ascii")
    )

    assert configuration["tool"]["pytest"]["ini_options"]["pythonpath"] == [
        "src"
    ]


def test_fcf_import_resolves_inside_repository_src() -> None:
    package_paths = {Path(path).resolve() for path in fcf.__path__}

    assert (ROOT / "src" / "fcf").resolve() in package_paths
