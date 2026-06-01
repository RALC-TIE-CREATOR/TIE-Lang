import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from topology import (
    ClosedLoop,
    CubicLattice,
    PhaseFieldBridge,
    PhaseStabilityReport,
    TopologicalRuntimePreview,
    apply_local_interaction,
    classify_interaction,
    make_square_loop,
)


def test_square_loop_length_and_winding():
    lattice = CubicLattice(12, 12, 1)
    loop = make_square_loop(lattice, origin=(1, 1, 0), side=2)
    assert loop.length == 8
    assert loop.winding == 1


def test_translation_preserves_topology():
    lattice = CubicLattice(12, 12, 1)
    loop = make_square_loop(lattice, origin=(1, 1, 0), side=2, clockwise=True)
    moved = loop.translated(dx=3, dy=4)
    assert moved.length == loop.length
    assert moved.winding == loop.winding


def test_runtime_write_read_and_not():
    runtime = TopologicalRuntimePreview(CubicLattice(12, 12, 1))
    runtime.write_bit("q0", 1, origin=(1, 1, 0))
    assert runtime.read_bit("q0") == 1
    assert runtime.read_charge("q0") == 1

    runtime.topological_not("q0")
    assert runtime.read_bit("q0") == 0
    assert runtime.read_charge("q0") == -1


def test_runtime_translation_preserves_bit():
    runtime = TopologicalRuntimePreview(CubicLattice(12, 12, 1))
    runtime.write_bit("q1", 0, origin=(2, 2, 0))
    runtime.translate("q1", dx=5, dy=1)
    assert runtime.read_bit("q1") == 0
    assert runtime.read_charge("q1") == -1


def test_invalid_loop_is_rejected():
    lattice = CubicLattice(8, 8, 1)
    try:
        ClosedLoop(
            lattice,
            (
                (0, 0, 0),
                (1, 0, 0),
                (1, 1, 0),
                (0, 0, 0),
            ),
        )
    except ValueError:
        return
    raise AssertionError("Se esperaba ValueError para un lazo invalido")


def test_same_charge_loops_repel():
    lattice = CubicLattice(14, 14, 1)
    left = make_square_loop(lattice, origin=(2, 2, 0), side=2)
    right = make_square_loop(lattice, origin=(5, 2, 0), side=2)
    result = apply_local_interaction(left, right, near_threshold=4.0)
    assert result["action"] == "repel"
    assert result["charge_before"] == 2
    assert result["charge_after"] == 2


def test_opposite_charge_loops_annihilate():
    lattice = CubicLattice(14, 14, 1)
    left = make_square_loop(lattice, origin=(2, 2, 0), side=2)
    right = make_square_loop(lattice, origin=(5, 2, 0), side=2, clockwise=True)
    assert classify_interaction(left, right, near_threshold=4.0) == "annihilate"
    result = apply_local_interaction(left, right, near_threshold=4.0)
    assert result["loops"] == []
    assert result["charge_before"] == 0
    assert result["charge_after"] == 0


def test_runtime_interaction_annihilates_cells():
    runtime = TopologicalRuntimePreview(CubicLattice(14, 14, 1))
    runtime.write_bit("a", 1, origin=(2, 2, 0))
    runtime.write_bit("b", 0, origin=(5, 2, 0))
    result = runtime.interact("a", "b", near_threshold=4.0)
    assert result["action"] == "annihilate"
    assert runtime.cells == {}


def test_phase_bridge_preserves_positive_winding():
    loop = make_square_loop(CubicLattice(12, 12, 1), origin=(2, 2, 0), side=2)
    bridge = PhaseFieldBridge()
    projection = bridge.project_loop(loop, pasos=10, dt=0.08)
    assert projection["input_winding"] == 1
    assert projection["measured_winding"] == 1
    assert projection["energy_final"] >= 0.0


def test_runtime_phase_projection_reports_cells():
    runtime = TopologicalRuntimePreview(CubicLattice(12, 12, 1))
    runtime.write_bit("q0", 1, origin=(1, 1, 0))
    runtime.write_bit("q1", 0, origin=(6, 6, 0))
    result = runtime.phase_projection(pasos=8, dt=0.08)
    assert set(result) == {"q0", "q1"}
    assert result["q0"]["measured_winding"] == 1
    assert result["q1"]["measured_winding"] == -1


def test_runtime_register_write_and_read_value():
    runtime = TopologicalRuntimePreview(CubicLattice(24, 24, 1))
    runtime.write_value("acc", 13, origin=(1, 1, 0))
    assert runtime.read_value("acc") == 13
    assert runtime.read_bits("acc") == [1, 0, 1, 1]
    snapshot = runtime.snapshot()["acc"]
    assert snapshot["value"] == 13
    assert snapshot["bits"] == [1, 0, 1, 1]
    assert snapshot["planes"] == 4


def test_runtime_phase_projection_reports_register_planes():
    runtime = TopologicalRuntimePreview(CubicLattice(24, 24, 1))
    runtime.write_value("acc", 5, origin=(1, 1, 0))
    result = runtime.phase_projection(pasos=8, dt=0.08)
    assert result["acc"]["bits"] == [1, 0, 1, 0]
    assert result["acc"]["measured_bits"] == [1, 0, 1, 0]
    assert result["acc"]["measured_value"] == 5
    assert result["acc"]["energy_final"] >= 0.0
    assert set(result["acc"]["planes"]) == {"b0", "b1", "b2", "b3"}


def test_phase_bridge_projects_register_as_shared_field():
    runtime = TopologicalRuntimePreview(CubicLattice(24, 24, 1))
    register = runtime.write_value("acc", 10, origin=(1, 1, 0))
    bridge = PhaseFieldBridge()
    projection = bridge.project_register(register, pasos=8, dt=0.08)
    assert projection["bits"] == [0, 1, 0, 1]
    assert projection["measured_bits"] == [0, 1, 0, 1]
    assert projection["measured_value"] == 10
    assert projection["planes"]["b0"]["input_winding"] == -1
    assert projection["planes"]["b1"]["input_winding"] == 1
    assert projection["energy_initial"] >= projection["energy_final"]
    assert projection["stability"]["stable"] is True
    assert projection["stability"]["bit_errors"] == 0


def test_phase_stability_report_detects_bit_errors():
    report = PhaseStabilityReport(
        value=7,
        measured_value=3,
        bits=[1, 1, 1, 0],
        measured_bits=[1, 1, 0, 0],
        energy_initial=10.0,
        energy_final=7.5,
    )
    assert report.bit_errors == 1
    assert report.energy_delta == -2.5
    assert report.stable is False


def test_stable_register_layout_spreads_planes():
    runtime = TopologicalRuntimePreview(CubicLattice(32, 32, 1))
    register = runtime.write_value("acc", 5, origin=(1, 1, 0), layout="stable")
    assert register.layout == "stable"
    assert [plane.loop.center_grid for plane in register.planes] == [
        (2, 2, 0),
        (10, 2, 0),
        (2, 10, 0),
        (10, 10, 0),
    ]
