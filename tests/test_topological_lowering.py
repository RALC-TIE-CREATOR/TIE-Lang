import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from topology.lowering import run_topological_source


def test_topological_lowering_basic_bits():
    result = run_topological_source(
        """
let a = 1
let b = 0
print a
print b
"""
    )
    assert result.output == [1, 0]
    assert result.snapshot["a"]["bit"] == 1
    assert result.snapshot["b"]["bit"] == 0


def test_topological_lowering_not_and_copy():
    result = run_topological_source(
        """
let a = 1
let b = not a
let c = b
print b
print c
"""
    )
    assert result.output == [0, 0]
    assert result.snapshot["a"]["charge"] == 1
    assert result.snapshot["b"]["charge"] == -1
    assert result.snapshot["c"]["charge"] == -1


def test_topological_lowering_if():
    result = run_topological_source(
        """
let a = 1
let b = not a
if b:
    print 9
else:
    print 7
"""
    )
    assert result.output == [7]


def test_topological_lowering_phase_projection():
    result = run_topological_source(
        """
let a = 1
let b = not a
""",
        with_phase_projection=True,
    )
    assert result.phase_projection is not None
    assert result.phase_projection["a"]["measured_winding"] == 1
    assert result.phase_projection["b"]["measured_winding"] == -1


def test_topological_lowering_boolean_ops_and_compare():
    result = run_topological_source(
        """
let a = 1
let b = 0
print a and b
print a or b
if a == 1:
    print 6
else:
    print 2
"""
    )
    assert result.output == [0, 1, 6]


def test_topological_lowering_while():
    result = run_topological_source(
        """
let a = 1
while a:
    print a
    a = not a
print a
"""
    )
    assert result.output == [1, 0]


def test_topological_lowering_break_and_continue():
    result = run_topological_source(
        """
let a = 1
let b = 0
while a:
    if b:
        break
    b = 1
    continue
    print 9
print b
"""
    )
    assert result.output == [1]


def test_topological_lowering_arithmetic():
    result = run_topological_source(
        """
let x = 5
let y = 3
let z = x + y
let w = x - y
print z
print w
if z > y:
    print 4
else:
    print 1
"""
    )
    assert result.output == [8, 2, 4]
    assert result.snapshot["x"]["value"] == 5
    assert result.snapshot["z"]["value"] == 8
    assert result.snapshot["z"]["topological"] is True
    assert result.snapshot["z"]["bits"] == [0, 0, 0, 1]
    assert result.snapshot["z"]["alu_trace"][0]["interaction"] == "repel"


def test_topological_lowering_alu_extended():
    result = run_topological_source(
        """
let x = 6
let y = 3
print x * y
print x & y
print x | y
print x ^ y
print ~y
if (x * y) == 2:
    print 9
else:
    print 1
"""
    )
    assert result.output == [2, 2, 7, 5, 12, 9]
