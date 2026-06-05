# TIE-Lang Topology Preview

`topology/` is the first explicit `v0.3.0` layer.

Its goal is not to replace the stable compiler/CPU path yet.
Its goal is to introduce a real topological execution substrate where:

- information is stored as closed loops on a cubic lattice
- logical state is encoded by topological orientation
- translations preserve the stored state
- negation is modeled as orientation reversal
- nearby loops can interact through local discrete rules
- loop states can be projected into the sine-Gordon phase substrate in `core/`
- a first lowering path from a tiny TIE-Lang subset into this runtime

This preview is intentionally discrete and minimal.
It is the bridge between:

- the current executable language
- a future sine-Gordon or phase-field backend
- a genuinely topological machine model

## Main pieces

- `CubicLattice`: periodic cubic substrate
- `ClosedLoop`: self-avoiding closed path on that lattice
- `TopologicalMemoryCell`: minimal topological memory element
- `TopologicalRegister`: 4-plane topological value bundle
- `TopologicalRuntimePreview`: small experimental runtime
- `interactions.py`: local annihilation / repulsion rules
- `bridge.py`: projection into the phase-field backend
- `instructions.py`: instruction set intermedio del backend topologico
- `lowering.py`: first subset compiler/lowering into topological execution

## Example

```python
from topology import CubicLattice, TopologicalRuntimePreview

lattice = CubicLattice(12, 12, 1)
runtime = TopologicalRuntimePreview(lattice)

runtime.write_bit("q0", 1, origin=(1, 1, 0))
runtime.translate("q0", dx=3)
runtime.topological_not("q0")

print(runtime.snapshot())
```

## New v0.3.0 preview capabilities

- same-charge nearby loops can repel while preserving total charge
- opposite-charge nearby loops can annihilate
- runtime cells can be projected into `core.red.Red`
- the projected state is re-measured through `medir_N(...)`
- a small subset of TIE-Lang can now run on this backend
- that source subset is now lowered to topological instructions before execution

## Supported source subset

Current lowering support:

- `let x = 0`
- `let x = 1`
- `let x = true`
- `let x = false`
- `let y = x`
- `let y = not x`
- `print expr`
- `if expr: ... else: ...`
- `while expr: ...`
- `break`
- `continue`

Current expressions:

- integer literals `0..15`
- `0`, `1`
- `true`, `false`
- `id`
- `not expr`
- `~expr`
- `expr and expr`
- `expr or expr`
- `expr + expr`
- `expr - expr`
- `expr * expr`
- `expr & expr`
- `expr | expr`
- `expr ^ expr`
- simple chained comparisons over known values

## Intermediate instruction layer

The lowering path now emits a small topological instruction stream before
execution. This currently includes:

- stores
- unary boolean operations
- binary boolean operations
- arithmetic operations
- bitwise operations
- comparisons
- labels
- jumps
- conditional jumps

## Minimal ALU semantics

The current topological ALU is still discrete and 4-bit bounded, but it is now
less scalar than before:

- arithmetic values live in the range `0..15`
- every runtime value is now materialized as a 4-plane topological register
- `+`, `-`, `*`, `inc`, `dec`, and `~` wrap modulo `16`
- `&`, `|`, and `^` operate directly on those 4-bit values
- `+` and `-` are now resolved plane-by-plane through a small ripple-carry scheme
- `*` is currently built from repeated shifted additions on those same planes
- carry transitions record the local event that generated, propagated, killed, or
  ignored the carry between neighboring planes
- register phase projection now places all four planes in one shared `Red` field
  and measures the resulting value after damped phase evolution
- phase projection reports `stable`, `bit_errors`, and `energy_delta` for each
  register through a formal stability report
- registers can use a wider `stable` layout to separate planes before phase
  projection experiments
- this is still not a full lattice-native ALU, but it is already closer to one than
  a plain scalar VM fallback

Each arithmetic result may include an `alu_trace` in the execution snapshot. A
trace entry records:

- the source plane and next target plane
- input bits and `carry_in`
- `generate`, `propagate`, and `carry_out`
- the local loop interaction used by that step (`repel`, `annihilate`, or
  `coexist`)

The topological runner can also report register stability:

```bash
python -m compiler.topological_run examples/topologia_alu.tie --stability
```

## Phase-causal ALU preview

Work after `v0.3.0` begins the `v0.4.0` direction: the phase field can now
participate causally in ALU execution.

In opt-in mode, an ALU operation:

1. computes a tentative 4-plane register value
2. projects that register into the shared phase substrate
3. measures `measured_value`
4. commits that measured value back into the VM

Run it with:

```bash
python -m compiler.topological_run examples/topologia_phase_causal.tie --phase-causal
```

This is intentionally experimental. It means unstable compact layouts can change
program output, which is the point of this preview.
