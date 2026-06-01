# Changelog

## v0.3.0

Third public release of TIE-Lang, focused on the first experimental
topological execution backend.

Included in this version:

- first `topology/` backend preview with cubic lattice, closed loops, and
  topological runtime primitives
- source-level lowering path from a small TIE-Lang subset into a topological
  instruction stream
- experimental topological ALU with 4-plane register bundles
- arithmetic carry traces through `alu_trace`, including local loop interactions
- local interaction rules: repulsion, annihilation, and coexistence
- bridge from discrete loop/register states into the sine-Gordon-style phase
  substrate in `core/`
- shared phase-field projection for full topological registers, including
  reconstructed `measured_value`
- formal phase stability reports with `stable`, `bit_errors`, and `energy_delta`
- experimental wider `stable` register layout for phase projection experiments
- `tie-topology` runner via `python -m compiler.topological_run`
- `--phase` and `--stability` reporting for topological demos
- stronger compiler coverage, now including 37 runnable compiler programs
- language growth after `v0.2.0`: globals, richer expressions, `elif`,
  `break`, `continue`, arrays, symbols, and matrices

Notes:

- The normal `tie` compiler/CPU path remains the stable execution backend.
- The topological backend is experimental and intentionally limited.
- Phase stability is now measured, not assumed; some compact register layouts
  are expected to show instability under phase evolution.

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
