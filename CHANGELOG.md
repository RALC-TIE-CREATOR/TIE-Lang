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
