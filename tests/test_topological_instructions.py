import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from topology.instructions import TopologicalInstruction, TopologicalInstructionMachine
from topology.lowering import TopologicalLowerer


def test_instruction_machine_store_and_print():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("a", 1)),
            TopologicalInstruction("STORE_NOT", ("b", "a")),
            TopologicalInstruction("PRINT_VAR", ("a",)),
            TopologicalInstruction("PRINT_VAR", ("b",)),
        ]
    )
    assert result.output == [1, 0]
    assert result.snapshot["a"]["charge"] == 1
    assert result.snapshot["b"]["charge"] == -1
    assert result.snapshot["a"]["bits"] == [1, 0, 0, 0]


def test_instruction_machine_phase_projection():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [TopologicalInstruction("STORE_CONST", ("a", 1))],
        with_phase_projection=True,
    )
    assert result.phase_projection is not None
    assert result.phase_projection["a"]["measured_winding"] == 1
    assert result.phase_projection["a"]["measured_bits"] == [1, 0, 0, 0]


def test_lowerer_emits_instruction_stream():
    lowerer = TopologicalLowerer()
    result = lowerer.run_source(
        """
let a = 1
let b = not a
print a
print b
"""
    )
    assert result.output == [1, 0]
    assert len(lowerer.instructions) == 4
    assert lowerer.instructions[0].op == "STORE_CONST"
    assert lowerer.instructions[1].op == "STORE_NOT"
    assert lowerer.instructions[2].op == "PRINT_VAR"
    assert lowerer.instructions[3].op == "PRINT_VAR"


def test_instruction_machine_boolean_and_compare():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("a", 1)),
            TopologicalInstruction("STORE_CONST", ("b", 0)),
            TopologicalInstruction("STORE_BINARY", ("c", "and", ("var", "a"), ("var", "b"))),
            TopologicalInstruction("STORE_COMPARE", ("d", ("var", "a"), "==", ("const", 1))),
            TopologicalInstruction("PRINT_VAR", ("c",)),
            TopologicalInstruction("PRINT_VAR", ("d",)),
        ]
    )
    assert result.output == [0, 1]


def test_instruction_machine_jump_loop():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("a", 1)),
            TopologicalInstruction("LABEL", ("loop1",)),
            TopologicalInstruction("PRINT_VAR", ("a",)),
            TopologicalInstruction("STORE_NOT", ("a", "a")),
            TopologicalInstruction("JUMP_IF_FALSE", (("var", "a"), "end1")),
            TopologicalInstruction("JUMP", ("loop1",)),
            TopologicalInstruction("LABEL", ("end1",)),
        ]
    )
    assert result.output == [1]


def test_instruction_machine_arithmetic():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("x", 5)),
            TopologicalInstruction("STORE_CONST", ("y", 3)),
            TopologicalInstruction("STORE_BINARY", ("z", "+", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("STORE_BINARY", ("w", "-", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("STORE_UNARY", ("u", "inc", ("var", "y"))),
            TopologicalInstruction("STORE_UNARY", ("v", "dec", ("var", "y"))),
            TopologicalInstruction("PRINT_VAR", ("z",)),
            TopologicalInstruction("PRINT_VAR", ("w",)),
            TopologicalInstruction("PRINT_VAR", ("u",)),
            TopologicalInstruction("PRINT_VAR", ("v",)),
        ]
    )
    assert result.output == [8, 2, 4, 2]
    assert result.snapshot["x"]["value"] == 5
    assert result.snapshot["z"]["value"] == 8
    assert result.snapshot["z"]["topological"] is True
    assert result.snapshot["z"]["bits"] == [0, 0, 0, 1]
    assert result.snapshot["z"]["alu_trace"][0]["generate"] == 1
    assert result.snapshot["z"]["alu_trace"][0]["interaction"] == "repel"


def test_instruction_machine_alu_bitwise_and_multiply():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("x", 6)),
            TopologicalInstruction("STORE_CONST", ("y", 3)),
            TopologicalInstruction("STORE_BINARY", ("mul", "*", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("STORE_BINARY", ("band", "&", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("STORE_BINARY", ("bor", "|", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("STORE_BINARY", ("bxor", "^", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("STORE_UNARY", ("inv", "~", ("var", "y"))),
            TopologicalInstruction("PRINT_VAR", ("mul",)),
            TopologicalInstruction("PRINT_VAR", ("band",)),
            TopologicalInstruction("PRINT_VAR", ("bor",)),
            TopologicalInstruction("PRINT_VAR", ("bxor",)),
            TopologicalInstruction("PRINT_VAR", ("inv",)),
        ]
    )
    assert result.output == [2, 2, 7, 5, 12]
    assert result.snapshot["mul"]["value"] == 2
    assert result.snapshot["band"]["value"] == 2
    assert result.snapshot["inv"]["value"] == 12
    assert "alu_trace" in result.snapshot["mul"]
    assert "alu_trace" in result.snapshot["band"]
    assert "alu_trace" in result.snapshot["bor"]
    assert "alu_trace" in result.snapshot["bxor"]
    assert "alu_trace" in result.snapshot["inv"]
    assert result.snapshot["band"]["alu_trace"][0]["interaction"] == "logic"
    assert result.snapshot["inv"]["alu_trace"][0]["interaction"] == "logic"
    assert any(step["carry_out"] == 1 for step in result.snapshot["mul"]["alu_trace"])


def test_instruction_machine_local_carry_propagation_trace():
    machine = TopologicalInstructionMachine()
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("x", 7)),
            TopologicalInstruction("STORE_CONST", ("y", 1)),
            TopologicalInstruction("STORE_BINARY", ("z", "+", ("var", "x"), ("var", "y"))),
        ]
    )
    trace = result.snapshot["z"]["alu_trace"]
    assert result.snapshot["z"]["value"] == 8
    assert [step["carry_out"] for step in trace] == [1, 1, 1, 0]
    assert trace[0]["generate"] == 1
    assert trace[0]["target_plane"] == 1
    assert trace[1]["propagate"] == 1
    assert trace[1]["target_plane"] == 2
    assert trace[2]["propagate"] == 1
    assert trace[2]["target_plane"] == 3
    assert trace[3]["target_plane"] is None
    assert trace[3]["interaction"] == "annihilate"


def test_instruction_machine_phase_causal_alu_commits_measured_value():
    machine = TopologicalInstructionMachine(phase_causal_alu=True)
    result = machine.execute(
        [
            TopologicalInstruction("STORE_CONST", ("x", 6)),
            TopologicalInstruction("STORE_CONST", ("y", 1)),
            TopologicalInstruction("STORE_BINARY", ("z", "+", ("var", "x"), ("var", "y"))),
            TopologicalInstruction("PRINT_VAR", ("z",)),
        ]
    )
    report = result.snapshot["z"]["phase_causal"]
    assert report["operation"] == "+"
    assert report["input_value"] == 7
    assert report["committed_value"] == result.output[0]
    assert report["committed_value"] == result.snapshot["z"]["value"]
