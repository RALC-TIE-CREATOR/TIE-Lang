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

## Results

All operations verified:
- Logic: 3/3 gates correct
- Arithmetic: all sums correct including carry
- Memory: 51/51 persistence checks, zero degradation
- ALU: 22/22 operations correct (100%)
- CPU: 4/4 programs correct
- Compiler: 5/5 programs correct

## Key finding
