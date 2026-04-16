# TIE-Lang

**Topological Infrastructure Language** — 
A programming language where computation is 
implemented through topological phase vortices 
in a discrete sine-Gordon network.

## What is this?

TIE-Lang is based on the Spatial Infrastructure 
Theory (TIE/SIT). The core insight:

> Matter is not a deformation of space.
> Matter is **information** encoded in the infrastructure.
> Therefore reality already has a programming language.
> TIE-Lang is an attempt to discover it.

TIE-Lang is both:

- a conceptual programming language derived from TIE/SIT
- a working Python implementation that compiles source code into a 4-bit virtual CPU

## Why TIE-Lang?

TIE-Lang is not meant to be just another toy syntax.
The project tries to connect:

- topological information primitives
- a concrete execution model
- a small but real source language
- a path from theory to executable computation

## How it works

Classical computers store bits as voltage (fragile).
TIE-Lang stores bits as topological winding numbers (robust).

| Property        | Silicon       | TIE-Lang         |
|-----------------|---------------|------------------|
| Data unit       | voltage       | winding number N |
| Noise immunity  | vulnerable    | topological      |
| Memory refresh  | every 64ms    | never needed     |
| Energy (compute)| dissipates    | 0.00 measured    |

## Alphabet

| Symbol | N  | Logical value |
|--------|----|---------------|
| Electron | 9 | 0             |
| Proton   | 8 | 1             |
| Neutrino | 4 | null/pointer  |
| W/Z boson| 7 | operator      |

## Current status: v1.0

- ✅ v0.1 Logic gates (NOT, AND, OR) — Turing complete
- ✅ v0.2 Arithmetic (Half/Full Adder, 4-bit)
- ✅ v0.3 Topological persistent memory
- ✅ v0.4 Complete ALU (7 operations, flags)
- ✅ v0.5 CPU (fetch/decode/execute, jumps, subroutines)
- ✅ v1.0 Compiler (source → lexer → AST → CPU)
- 🔵 v1.1 Topological Neural Network (next)

## Quick start

```python
from compiler.compiler import compile_and_run

compile_and_run("""
let x = 6
let y = 9
print x + y
""")
# Output: 15
```

Run a `.tie` file directly:

```bash
tie examples/fibonacci.tie
tie examples/funciones.tie
python -m compiler.run examples/fibonacci.tie
python -m compiler.run examples/fibonacci.tie --asm
python tie.py examples/fibonacci.tie
```

## Local install

Run directly from the repo:

```bash
python tie.py examples/fibonacci.tie
```

Install as a local command:

```bash
pip install -e .
tie examples/fibonacci.tie
```

`tie` is the primary public command for TIE-Lang.
`python -m compiler.run` and `python tie.py` remain supported execution paths.

## Syntax notes

- Blocks use Python-style indentation.
- Official v1.0 function syntax uses commas: `f(a, b)`.
- Legacy whitespace form `f(a b)` is intentionally retained for compatibility in v1.0.
- Arithmetic and storage are currently 4-bit at the CPU level.
- Negative subtraction wraps in 4 bits and also sets the `N` flag.

Example:

```tie
def max(a, b):
    if a > b:
        return a
    else:
        return b

let x = 6
let y = 9
print max(x, y)
```

## Results

All operations verified:
- Logic: 3/3 gates correct
- Arithmetic: all sums correct including carry
- Memory: 51/51 persistence checks, zero degradation
- ALU: 22/22 operations correct (100%)
- CPU: 4/4 programs correct
- Compiler: 7/7 programs correct

## Language spec

The current implementation now has a stable v1.0 execution model:

- Source syntax is indentation-based.
- Variables live in 4-bit RAM.
- Registers `R0`-`R3` are 4-bit.
- Arithmetic is modular at 4 bits in the CPU.
- Comparisons produce boolean values `1` or `0`.
- Function arguments currently support up to 4 positional values.
- Official syntax is `f(a, b)`, while `f(a b)` is intentionally preserved as legacy-compatible syntax in v1.0.

See `docs/spec.md` for the technical reference and
`docs/arquitectura.md` for the execution pipeline.

## Project layout

- `compiler/`: lexer, parser, compiler, runner
- `core/`: topological logic and arithmetic primitives
- `cpu/`: 4-bit virtual CPU and memory
- `examples/`: canonical `.tie` programs
- `tests/`: verification suites for compiler, CPU, ALU, runner and CLI

## Current limits

The current implementation is intentionally small and explicit:

- CPU model is 4-bit
- RAM model is 16 cells
- function calls support up to 4 positional arguments
- no arrays, strings or floating point yet
- variable storage is RAM-based and global to the compiled program model

These are implementation limits, not necessarily permanent design limits.

## Release notes

See `CHANGELOG.md` for implementation milestones and
`docs/distribution.md` for local packaging and publication notes.

## Roadmap

Near-term work after `v0.1.0`:

- improve public demos and release presentation
- expand the language beyond the current 4-bit baseline
- evaluate the next major layer: neural/topological learning components

## Theoretical foundation

Based on TIE (Teoría de la Infraestructura Espacial)
by Rubén A. Lecona Curto (R@LC), 2026.

## License

Apache License 2.0. See `LICENSE`.

## Authors

- R@LC — Theory and concept

## Next: Neural Networks

Topological weights cannot be corrupted by noise.
A neural network where weights are vortices N
would be inherently noise-immune without 
error correction overhead.

See `neural/` directory.
