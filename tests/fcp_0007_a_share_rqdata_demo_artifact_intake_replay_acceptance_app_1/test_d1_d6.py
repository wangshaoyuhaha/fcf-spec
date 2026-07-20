import hashlib
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.fcp_0007_a_share_rqdata_demo_artifact_intake_replay_acceptance_app_1 import (
    FCP_0007_BOUNDARY,
    RQDataDemoAcceptanceBoundary,
    RegisteredRQDataDemoArtifact,
    build_rqdata_demo_acceptance_packet,
    evaluate_rqdata_demo_acceptance,
    load_registered_rqdata_demo,
    validate_rqdata_demo_packet,
)


HEADER = (
    "order_book_id,date,low,open,high,limit_down,num_trades,close,"
    "limit_up,volume,total_turnover"
)
ROWS = (
    '"000001.XSHE","2022-01-04",16.18,16.48,16.66,14.83,99885,16.66,18.13,116925933,1918887050.94',
    '"000001.XSHE","2022-01-05",16.55,16.58,17.22,14.99,144646,17.15,18.33,196199817,3344124589.35',
    '"000001.XSHE","2022-01-06",17,17.11,17.27,15.44,76328,17.12,18.87,110788519,1896535837.6',
)


def demo_bytes(*, repeated_bom: bool = True) -> bytes:
    prefix = "\ufeff" if repeated_bom else ""
    return (HEADER + "\n" + "\n".join(prefix + row for row in ROWS) + "\n").encode(
        "utf-8"
    )


def registration(payload: bytes, **updates: object) -> RegisteredRQDataDemoArtifact:
    values = {
        "artifact_id": "rqdata-a-share-daily-demo-2022-01",
        "source_id": "rqdata-official-demo",
        "artifact_sha256": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
        "registered_at_utc": "2026-07-20T02:02:24Z",
    }
    values.update(updates)
    return RegisteredRQDataDemoArtifact(**values)  # type: ignore[arg-type]


def write_demo(tmp_path: Path, payload: bytes) -> Path:
    path = tmp_path / "rqdata-demo.csv"
    path.write_bytes(payload)
    return path


def load_demo(tmp_path: Path):
    payload = demo_bytes()
    return load_registered_rqdata_demo(
        write_demo(tmp_path, payload), registration(payload)
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0007_BOUNDARY.local_file_read_allowed is True
    assert FCP_0007_BOUNDARY.raw_redistribution_allowed is False
    assert FCP_0007_BOUNDARY.network_allowed is False
    assert FCP_0007_BOUNDARY.provider_selection_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0007_BOUNDARY.network_allowed = True  # type: ignore[misc]


def test_d1_boundary_rejects_provider_or_repository_authority() -> None:
    with pytest.raises(ValueError, match="fail closed"):
        RQDataDemoAcceptanceBoundary(provider_selection_allowed=True)
    with pytest.raises(ValueError, match="fail closed"):
        RQDataDemoAcceptanceBoundary(raw_repository_storage_allowed=True)


def test_d1_registration_preserves_unresolved_rights() -> None:
    payload = demo_bytes()
    item = registration(payload)
    assert item.usage_scope == "LOCAL_EVALUATION_ONLY"
    assert item.entitlement_state == "UNRESOLVED"
    assert item.retention_state == "UNRESOLVED"
    assert item.redistribution_allowed is False


def test_d1_registration_rejects_commercial_or_provider_claims() -> None:
    payload = demo_bytes()
    with pytest.raises(ValueError, match="unresolved"):
        registration(payload, entitlement_state="APPROVED")
    with pytest.raises(ValueError, match="provider authority"):
        registration(payload, provider_selected=True)


def test_d2_loader_verifies_exact_bytes_and_normalizes_bom_in_memory(
    tmp_path: Path,
) -> None:
    payload = demo_bytes()
    path = write_demo(tmp_path, payload)
    loaded = load_registered_rqdata_demo(path, registration(payload))
    assert path.read_bytes() == payload
    assert loaded.repeated_bom_count == 3
    assert len(loaded.rows) == 3
    assert loaded.rows[0].instrument_id == "000001.XSHE"


def test_d2_loader_rejects_digest_mismatch(tmp_path: Path) -> None:
    payload = demo_bytes()
    path = write_demo(tmp_path, payload + b" ")
    with pytest.raises(ValueError, match="byte length mismatch"):
        load_registered_rqdata_demo(path, registration(payload))


def test_d2_loader_rejects_unknown_schema(tmp_path: Path) -> None:
    payload = demo_bytes().replace(b"total_turnover", b"turnover")
    with pytest.raises(ValueError, match="columns are not exact"):
        load_registered_rqdata_demo(
            write_demo(tmp_path, payload), registration(payload)
        )


def test_d3_loader_rejects_duplicate_instrument_date(tmp_path: Path) -> None:
    text = HEADER + "\n" + ROWS[0] + "\n" + ROWS[0] + "\n"
    payload = text.encode("utf-8")
    with pytest.raises(ValueError, match="duplicate instrument dates"):
        load_registered_rqdata_demo(
            write_demo(tmp_path, payload), registration(payload)
        )


def test_d3_loader_rejects_invalid_ohlc(tmp_path: Path) -> None:
    payload = demo_bytes().replace(b"16.18,16.48,16.66", b"16.18,16.48,16.20")
    with pytest.raises(ValueError, match="OHLC invariant"):
        load_registered_rqdata_demo(
            write_demo(tmp_path, payload), registration(payload)
        )


def test_d3_loader_rejects_non_chronological_rows(tmp_path: Path) -> None:
    text = HEADER + "\n" + ROWS[1] + "\n" + ROWS[0] + "\n"
    payload = text.encode("utf-8")
    with pytest.raises(ValueError, match="chronologically ordered"):
        load_registered_rqdata_demo(
            write_demo(tmp_path, payload), registration(payload)
        )


def test_d4_replay_is_deterministic(tmp_path: Path) -> None:
    left = load_demo(tmp_path)
    right = load_registered_rqdata_demo(
        tmp_path / "rqdata-demo.csv", left.artifact
    )
    assert left.normalized_csv_sha256 == right.normalized_csv_sha256
    assert left.rowset_sha256 == right.rowset_sha256
    assert left.replay_sha256 == right.replay_sha256


def test_d4_bom_and_clean_csv_have_same_normalized_rowset(tmp_path: Path) -> None:
    bom_payload = demo_bytes(repeated_bom=True)
    clean_payload = demo_bytes(repeated_bom=False)
    bom_path = tmp_path / "bom.csv"
    clean_path = tmp_path / "clean.csv"
    bom_path.write_bytes(bom_payload)
    clean_path.write_bytes(clean_payload)
    bom = load_registered_rqdata_demo(bom_path, registration(bom_payload))
    clean = load_registered_rqdata_demo(clean_path, registration(clean_payload))
    assert bom.normalized_csv_sha256 == clean.normalized_csv_sha256
    assert bom.rowset_sha256 == clean.rowset_sha256
    assert bom.replay_sha256 != clean.replay_sha256


def test_d5_acceptance_exposes_ready_schema_and_blocked_product_evidence(
    tmp_path: Path,
) -> None:
    result = evaluate_rqdata_demo_acceptance(load_demo(tmp_path))
    assert result.schema_state == "READY_FOR_LOCAL_SCHEMA_REPLAY"
    assert result.product_evidence_state == "BLOCKED"
    assert result.row_count == 3
    assert "available-at" in result.missing_required_field_ids
    assert "COMMERCIAL_RIGHTS_UNRESOLVED" in result.finding_codes
    assert result.fcp_0005_readiness_claimed is False


def test_d5_packet_is_deeply_read_only_and_accepts(tmp_path: Path) -> None:
    loaded = load_demo(tmp_path)
    result = evaluate_rqdata_demo_acceptance(loaded)
    packet = build_rqdata_demo_acceptance_packet(loaded, result)
    assert isinstance(packet.payload, MappingProxyType)
    assert isinstance(packet.payload["artifact"], MappingProxyType)
    assert all(validate_rqdata_demo_packet(packet).values())
    with pytest.raises(TypeError):
        packet.payload["provider_selection_claimed"] = True  # type: ignore[index]


def test_d6_acceptance_never_claims_provider_or_product_authority(
    tmp_path: Path,
) -> None:
    result = evaluate_rqdata_demo_acceptance(load_demo(tmp_path))
    assert result.provider_selection_claimed is False
    assert result.product_phase_authorized is False
    assert result.fcp_0005_readiness_claimed is False
