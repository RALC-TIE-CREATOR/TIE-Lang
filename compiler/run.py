"""
compiler/run.py
---------------
Runner oficial de archivos `.tie` para TIE-Lang.

Uso:
    python -m compiler.run examples/fibonacci.tie
"""

from pathlib import Path
import sys

from .compiler import compile_and_run


def run_file(path: str, verbose_asm: bool = False) -> dict:
    archivo = Path(path)
    if not archivo.exists():
        raise FileNotFoundError(f"No existe el archivo: {archivo}")
    fuente = archivo.read_text(encoding="utf-8")
    return compile_and_run(
        fuente,
        titulo=f"TIE-Lang :: {archivo.name}",
        verbose_asm=verbose_asm,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        print("Uso: python -m compiler.run <archivo.tie> [--asm]")
        return 1

    verbose_asm = False
    if "--asm" in args:
        verbose_asm = True
        args.remove("--asm")

    if len(args) != 1:
        print("Uso: python -m compiler.run <archivo.tie> [--asm]")
        return 1

    try:
        run_file(args[0], verbose_asm=verbose_asm)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
