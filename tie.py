"""
Lanzador raíz de TIE-Lang.

Uso:
    python tie.py examples/fibonacci.tie
    python tie.py examples/fibonacci.tie --asm
    python tie.py --help
"""

from compiler.run import main


if __name__ == "__main__":
    raise SystemExit(main())
