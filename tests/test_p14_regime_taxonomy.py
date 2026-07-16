import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_regime_taxonomy import build_regime_taxonomy
from btc_finance_platform.p14_regime_taxonomy import classify_regime
from btc_finance_platform.p14_regime_taxonomy import write_regime_taxonomy


def test_regime_taxonomy_defines_core_buckets():
    taxonomy = build_regime_taxonomy()

    assert "trend_up" in taxonomy["regime_types"]
    assert "trend_down" in taxonomy["regime_types"]
    assert "range_chop" in taxonomy["regime_types"]
    assert "liquidity_stress" in taxonomy["regime_types"]


def test_regime_taxonomy_explains_why_regime_first():
    taxonomy = build_regime_taxonomy()

    assert taxonomy["why_regime_first"] == "expert trust scores must be conditioned by market environment"
    assert taxonomy["learning_engine_order"][0] == "define_regime_taxonomy"


def test_classify_regime_handles_basic_cases():
    assert classify_regime({"trend": "up", "volatility": "normal"})["regime"] == "trend_up"
    assert classify_regime({"trend": "down", "volatility": "normal"})["regime"] == "trend_down"
    assert classify_regime({"trend": "range", "volatility": "normal"})["regime"] == "range_chop"
    assert classify_regime({"liquidity": "stress"})["regime"] == "liquidity_stress"


def test_classify_regime_rejects_invalid_features():
    with pytest.raises(ValueError, match="features must be a dict"):
        classify_regime(None)
    with pytest.raises(ValueError, match="unsupported trend"):
        classify_regime({"trend": "sideways"})


def test_regime_taxonomy_preserves_paper_only_boundary():
    taxonomy = build_regime_taxonomy()

    assert taxonomy["paper_only"] is True
    assert taxonomy["local_only"] is True
    assert taxonomy["operator_review_required"] is True
    assert taxonomy["real_world_actions_allowed"] is False
    assert taxonomy["real_order"] is False
    assert taxonomy["real_execution"] is False


def test_write_regime_taxonomy_creates_json(tmp_path):
    output = tmp_path / "regime_taxonomy.json"
    result = write_regime_taxonomy(output)

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_learning_engine_regime_taxonomy"
    assert data["real_world_actions_allowed"] is False
