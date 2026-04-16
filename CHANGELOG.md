# Changelog

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
