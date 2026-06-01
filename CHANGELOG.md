# Changelog

## v0.2.0

Second public release of TIE-Lang, focused on language maturity,
experimental neural groundwork, and a cleaner public repository surface.

Included in this version:

- experimental neural layer with trainable perceptron and minimal MLP support
- richer neural datasets, including boolean, geometric, and temporal examples
- textual visualization of multilayer training history
- compiler support for function-local scope with global reads when not shadowed
- stronger compiler regression coverage, now including scope behavior
- improved README, roadmap, and contributor-facing documentation

Notes:

- The compiler now supports function-local scope at compile time.
- The neural layer is public and demonstrable, but remains experimental.
- The core machine model remains the same documented 4-bit execution baseline.

## Unreleased

Current work on `main` after `v0.2.0` includes:

- further language growth after the v0.2.0 baseline
- explicit global writes from functions through `global name = expr`
- richer expressions with `*`, `not`, `and`, and `or`
- chained comparisons and boolean literals `true` / `false`
- `elif`, `break`, and `continue`
- fixed-size arrays with literals, indexed reads, and indexed writes
- array arguments passed into functions by copy
- array builtins: `len`, `first`, and `last`
- lightweight symbol literals such as `@inicio`
- rectangular 2D matrices with nested literals and `m[i][j]` access
- matrix arguments passed into functions by copy
- stronger compiler coverage, now including 37 runnable compiler programs
- array scope and shadowing semantics aligned with function and block-local bindings
- first `v0.3.0` topological execution preview in `topology/`
- topological ALU registers represented as 4-plane lattice bundles
- local carry propagation traces for arithmetic results through `alu_trace`
- shared phase-field projection for full topological registers, including
  reconstructed `measured_value`
- formal phase stability reports with `stable`, `bit_errors`, and `energy_delta`
- experimental wider `stable` register layout for phase projection experiments
- `tie-topology --stability` report mode
- cubic lattice, closed-loop, and topological memory runtime primitives
- design documentation for the new topological backend direction
- local loop interaction rules: repulsion, annihilation, coexistence
- first bridge from loop states into the sine-Gordon-style phase substrate

## v0.1.0

Initial public-ready local distribution layer for TIE-Lang.

Included in this version:

- stable compiler pipeline from source to CPU execution
- normalized boolean comparisons
- function parameters stored into RAM on function entry
- 4-bit CPU semantics documented as the v1.0 machine model
- official module runner: `python -m compiler.run`
- official root launcher: `python tie.py`
- local package metadata via `pyproject.toml`
- canonical example set for Fibonacci, functions, comparisons and search
- tests for compiler, CPU, ALU, runner and root CLI

Notes:

- Official public syntax is comma-separated function arguments.
- Legacy whitespace-separated argument syntax remains accepted in v1.0 for compatibility.
- Arithmetic is defined by the current 4-bit CPU model.
# Unreleased

## Added
- Extended the experimental topological VM with a first minimal ALU covering `*`,
  `~`, `&`, `|`, and `^` in addition to the existing `+`, `-`, `inc`, and `dec`.
- Added `examples/topologia_alu.tie` as a source-level demo for the experimental
  topological ALU path.
- Materialized experimental ALU values as 4-plane topological registers instead
  of leaving non-bit temporals as plain scalar VM-only values.
- Added per-plane `alu_trace` data for arithmetic results, including carry
  generation, propagation, target plane, and local loop interaction.

## Verified
- Added execution tests for extended topological ALU instructions and lowering.
- Added topology tests for register snapshots and per-plane phase projection.
- Added regression coverage for local carry propagation across neighboring
  topological register planes.
