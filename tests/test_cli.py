"""
tests/test_cli.py
-----------------
Tests del lanzador raíz `tie.py`.
"""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_root_cli_fibonacci():
    """CLI raíz: ejecuta un ejemplo real y termina con código 0."""
    print("── CLI: tie.py fibonacci.tie ────────────")
    proc = subprocess.run(
        [sys.executable, "tie.py", "examples/fibonacci.tie"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    ok = (
        proc.returncode == 0
        and "Salida:  [0, 1, 1, 2, 3, 5, 8, 13]" in proc.stdout
    )
    print(f"  Return code: {proc.returncode}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_root_cli_help():
    """CLI raíz: muestra ayuda útil."""
    print("── CLI: tie.py --help ───────────────────")
    proc = subprocess.run(
        [sys.executable, "tie.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    ok = (
        proc.returncode == 0
        and "Runner oficial de TIE-Lang" in proc.stdout
        and "--list-examples" in proc.stdout
        and "--version" in proc.stdout
    )
    print(f"  Return code: {proc.returncode}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_root_cli_version():
    """CLI raíz: expone versión."""
    print("── CLI: tie.py --version ────────────────")
    proc = subprocess.run(
        [sys.executable, "tie.py", "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    ok = proc.returncode == 0 and "TIE-Lang CLI v0.1.0" in proc.stdout
    print(f"  Return code: {proc.returncode}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_root_cli_list_examples():
    """CLI raíz: lista ejemplos disponibles."""
    print("── CLI: tie.py --list-examples ──────────")
    proc = subprocess.run(
        [sys.executable, "tie.py", "--list-examples"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    ok = (
        proc.returncode == 0
        and "examples/fibonacci.tie" in proc.stdout
        and "examples/funciones.tie" in proc.stdout
        and "examples/comparadores.tie" in proc.stdout
    )
    print(f"  Return code: {proc.returncode}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: CLI")
    print("=" * 45)
    print()
    test_root_cli_fibonacci()
    test_root_cli_help()
    test_root_cli_version()
    test_root_cli_list_examples()
    print("✅ CLI raíz verificado")
