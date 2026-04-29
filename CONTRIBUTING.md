# Contributing to TIE-Lang

Thanks for taking the project seriously enough to spend time on it.

## What helps most

The most useful contributions right now are:

- compiler and language behavior fixes
- tighter tests
- examples that clarify the public language
- documentation that makes the project easier to understand
- focused neural-layer experiments that stay aligned with the current repo style

## Development setup

Install locally:

```bash
pip install -e .
```

Run examples:

```bash
tie --list-examples
tie examples/fibonacci.tie
```

Run tests directly:

```bash
python tests/test_compiler.py
python tests/test_cpu.py
python tests/test_neural.py
```

## Style notes

- Keep changes small and intentional.
- Match the existing structure of the repo.
- Prefer examples and tests that make behavior obvious.
- Treat the 4-bit machine model as part of the current language contract.
- Use comma-separated function syntax in public-facing docs and new examples.

## Before opening a change

Please make sure:

- the relevant tests still pass
- new behavior is reflected in docs when needed
- examples stay readable for someone seeing TIE-Lang for the first time

## Scope

TIE-Lang currently contains both stable and experimental areas.

Stable for public use:

- compiler pipeline
- CPU model
- CLI entry points
- examples and tests

Experimental:

- neural layer
- roadmap-stage language growth beyond the current machine model
