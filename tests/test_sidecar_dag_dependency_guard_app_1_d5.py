from sidecars.sidecar_dag_dependency_guard_app_1 import (
    DependencyGuardPacket,
    build_dependency_guard_packet,
    default_dependency_edges,
    default_sidecar_nodes,
    validate_dependency_guard_packet,
)


def test_d5_builds_ready_guard_packet():
    packet = build_dependency_guard_packet(
        packet_id="PACKET-SIDECAR-DAG-D5",
        nodes=default_sidecar_nodes(),
        edges=default_dependency_edges(),
        file_text_by_path={
            "sidecars/example_app/__init__.py": "paper_only = True\nread_only = True\n",
            "tests/test_example.py": "assert True\n",
        },
    )

    assert packet.packet_id == "PACKET-SIDECAR-DAG-D5"
    assert packet.graph_report.valid is True
    assert packet.import_scan_report.valid is True
    assert packet.operator_review_required is True
    assert packet.paper_only is True
    assert packet.local_only is True
    assert packet.read_only is True
    assert packet.sidecar_only is True
    assert packet.release_allowed is False
    assert packet.deploy_allowed is False
    assert packet.status == "ready_for_operator_review"


def test_d5_blocks_packet_when_import_scan_finds_violation():
    packet = build_dependency_guard_packet(
        packet_id="PACKET-SIDECAR-DAG-D5-BLOCKED",
        nodes=default_sidecar_nodes(),
        edges=default_dependency_edges(),
        file_text_by_path={
            "core/example.py": "import sidecars\n",
        },
    )

    assert packet.status == "blocked"
    assert packet.import_scan_report.valid is False


def test_d5_validates_guard_packet():
    packet = build_dependency_guard_packet(
        packet_id="PACKET-SIDECAR-DAG-D5",
        nodes=default_sidecar_nodes(),
        edges=default_dependency_edges(),
        file_text_by_path={"tests/test_example.py": "assert True\n"},
    )

    valid, issues = validate_dependency_guard_packet(packet)

    assert valid is True
    assert issues == ()


def test_d5_rejects_release_enabled_packet():
    packet = build_dependency_guard_packet(
        packet_id="PACKET-SIDECAR-DAG-D5",
        nodes=default_sidecar_nodes(),
        edges=default_dependency_edges(),
        file_text_by_path={"tests/test_example.py": "assert True\n"},
    )
    invalid = DependencyGuardPacket(
        packet_id=packet.packet_id,
        graph_report=packet.graph_report,
        import_scan_report=packet.import_scan_report,
        operator_review_required=packet.operator_review_required,
        paper_only=packet.paper_only,
        local_only=packet.local_only,
        read_only=packet.read_only,
        sidecar_only=packet.sidecar_only,
        release_allowed=True,
        deploy_allowed=packet.deploy_allowed,
        status=packet.status,
    )

    valid, issues = validate_dependency_guard_packet(invalid)

    assert valid is False
    assert "release_allowed_must_be_false" in issues


def test_d5_rejects_operator_review_bypass():
    packet = build_dependency_guard_packet(
        packet_id="PACKET-SIDECAR-DAG-D5",
        nodes=default_sidecar_nodes(),
        edges=default_dependency_edges(),
        file_text_by_path={"tests/test_example.py": "assert True\n"},
    )
    invalid = DependencyGuardPacket(
        packet_id=packet.packet_id,
        graph_report=packet.graph_report,
        import_scan_report=packet.import_scan_report,
        operator_review_required=False,
        paper_only=packet.paper_only,
        local_only=packet.local_only,
        read_only=packet.read_only,
        sidecar_only=packet.sidecar_only,
        release_allowed=packet.release_allowed,
        deploy_allowed=packet.deploy_allowed,
        status=packet.status,
    )

    valid, issues = validate_dependency_guard_packet(invalid)

    assert valid is False
    assert "operator_review_not_required" in issues
