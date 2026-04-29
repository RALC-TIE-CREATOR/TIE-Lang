# TIE-Lang

**Topological Infrastructure Language** is a programming language project inspired by TIE/SIT and implemented as a working toolchain.

Today, the repository contains a real executable pipeline:

`source -> lexer -> parser -> compiler -> 4-bit CPU -> execution`

TIE-Lang is therefore two things at once:

- a conceptual language derived from the TIE framework
- a runnable implementation with examples, tests, CLI tooling, and an experimental neural layer

## Why this repo exists

The project starts from a simple claim:

> Matter is not a deformation of space.  
> Matter is information encoded in infrastructure.  
> If reality already computes, it should have a language.

TIE-Lang explores that claim by turning it into code.

## What works today

The current repository already supports:

- a lexer, parser, and compiler for a small indentation-based language
- a 4-bit virtual CPU with RAM, flags, jumps, calls, and returns
- arithmetic, logic, comparisons, `if`, `while`, `print`, and functions
- function-local scope with global reads when names are not shadowed
- explicit global writes from inside functions through `global name = expr`
- official CLI execution through `tie`
- canonical example programs
- an experimental neural layer with trainable perceptrons and minimal MLPs

## Quick start

Install locally:

```bash
pip install -e .
```

Run a program:

```bash
tie examples/fibonacci.tie
tie examples/funciones.tie
tie examples/estado_global.tie
tie --list-examples
```

You can also run through the module or root launcher:

```bash
python -m compiler.run examples/fibonacci.tie
python tie.py examples/fibonacci.tie
```

## First example

```tie
let x = 6
let y = 9
print x + y
```

```tie
def max(a, b):
    if a > b:
        return a
    else:
        return b

print max(6, 9)
```

## Language snapshot

- Blocks use Python-style indentation.
- Public v1.0 function syntax uses commas: `f(a, b)`.
- Legacy whitespace syntax `f(a b)` still works in v1.0 for compatibility.
- Registers and RAM are currently 4-bit.
- Comparisons return normalized booleans: `1` or `0`.
- Function scope is static and compiler-managed in the current implementation.
- Global writes inside functions are explicit: `global total = expr`.

## Current status

Implemented milestones:

- `v0.1` logic gates
- `v0.2` arithmetic
- `v0.3` persistent memory
- `v0.4` ALU
- `v0.5` CPU
- `v1.0` compiler and runnable language
- `v1.1` experimental neural layer groundwork

Verification currently included in the repo:

- Logic: `3/3`
- Memory: `51/51`
- ALU: `22/22`
- CPU programs: `4/4`
- Compiler programs: `12/12`

## Repo guide

- `compiler/` - lexer, parser, compiler, CLI runner
- `core/` - topological logic and arithmetic primitives
- `cpu/` - 4-bit virtual CPU and memory
- `examples/` - canonical `.tie` programs
- `tests/` - verification suites
- `neural/` - experimental learning layer
- `docs/` - specification, architecture, roadmap, and distribution notes

## Read next

- [Language spec](/C:/Users/ralc0/Downloads/TIE-Lang/docs/spec.md)
- [Architecture](/C:/Users/ralc0/Downloads/TIE-Lang/docs/arquitectura.md)
- [Examples](/C:/Users/ralc0/Downloads/TIE-Lang/examples/README.md)
- [Roadmap](/C:/Users/ralc0/Downloads/TIE-Lang/docs/roadmap.md)
- [Changelog](/C:/Users/ralc0/Downloads/TIE-Lang/CHANGELOG.md)
- [Contributing](/C:/Users/ralc0/Downloads/TIE-Lang/CONTRIBUTING.md)

## Current limits

The current implementation is intentionally compact:

- 4-bit registers and RAM cells
- 16 RAM cells in the present CPU model
- up to 4 positional function arguments
- no arrays, strings, or floating point yet
- no full dynamic stack-frame model yet
- recursion is not guaranteed by the current scope and RAM allocation strategy

These are implementation limits, not a final statement about the language.

## Public status

The repo is public-ready as an executable research language prototype.
It should be read as:

- a serious implementation
- a compact machine model
- an evolving language
- an experimental bridge between theory and computation

## License

Apache License 2.0. See [LICENSE](/C:/Users/ralc0/Downloads/TIE-Lang/LICENSE).
