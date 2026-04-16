# TIE-Lang — Distribution Notes

## Current local distribution model

TIE-Lang can now be used in three ways:

1. As a Python library:
   `from compiler.compiler import compile_and_run`

2. As a module runner:
   `python -m compiler.run examples/fibonacci.tie`

3. As a root launcher:
   `python tie.py examples/fibonacci.tie`

## Editable install

The repository now includes a `pyproject.toml` with a console entry point:

`tie = "compiler.run:main"`

This allows local editable installation:

```bash
pip install -e .
tie examples/fibonacci.tie
```

## Packaging status

This is enough for:

- local development
- local demos
- internal testing
- early public repository use

Before broader public distribution, the next recommended steps are:

- choose an explicit license
- decide whether `tie.py` or installed `tie` is the canonical entry point
- add versioning policy for the language spec
- optionally publish to PyPI only after syntax and v1 semantics are frozen
