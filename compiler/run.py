"""
compiler/run.py
---------------
Runner oficial de archivos `.tie` para TIE-Lang.

Uso:
    python -m compiler.run examples/fibonacci.tie
"""

import argparse
from pathlib import Path
import sys

from .compiler import compile_and_run

VERSION = "0.1.0"


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


def run_path(path: str, verbose_asm: bool = False) -> int:
    destino = Path(path)

    if destino.is_file():
        run_file(str(destino), verbose_asm=verbose_asm)
        return 0

    if destino.is_dir():
        archivos = sorted(destino.glob("*.tie"))
        if not archivos:
            raise FileNotFoundError(
                f"No se encontraron archivos .tie en: {destino}"
            )
        for archivo in archivos:
            run_file(str(archivo), verbose_asm=verbose_asm)
        return 0

    raise FileNotFoundError(f"No existe el archivo o carpeta: {destino}")


def list_examples(base: str = "examples") -> int:
    raiz = Path(base)
    if not raiz.exists():
        print(f"No existe el directorio de ejemplos: {raiz}")
        return 1

    archivos = sorted(raiz.glob("*.tie"))
    if not archivos:
        print("No hay ejemplos .tie disponibles.")
        return 1

    print("Ejemplos disponibles:")
    for archivo in archivos:
        print(f"  - {archivo.as_posix()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tie",
        description="Runner oficial de TIE-Lang.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Archivo .tie o carpeta con ejemplos .tie",
    )
    parser.add_argument(
        "--asm",
        action="store_true",
        help="Muestra el ensamblador generado antes de ejecutar",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Muestra la versión actual del CLI de TIE-Lang",
    )
    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="Lista los ejemplos .tie disponibles en examples/",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.version:
        print(f"TIE-Lang CLI v{VERSION}")
        return 0

    if args.list_examples:
        return list_examples()

    if not args.path:
        parser.print_help()
        return 1

    try:
        return run_path(args.path, verbose_asm=args.asm)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
