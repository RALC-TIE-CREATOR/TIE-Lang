"""
tests/test_runner.py
--------------------
Tests del runner oficial de archivos `.tie`.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compiler.run import run_file


def test_run_file_fibonacci():
    """Runner CLI/librería: ejecuta un archivo .tie real."""
    print("── RUNNER: fibonacci.tie ────────────────")
    resultado = run_file("examples/fibonacci.tie", verbose_asm=False)

    salida = resultado["salida"]
    esperado = [0, 1, 1, 2, 3, 5, 8, 13]
    ok = salida == esperado
    print(f"  Salida:   {salida}")
    print(f"  Esperado: {esperado}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: Runner")
    print("=" * 45)
    print()
    test_run_file_fibonacci()
    print("✅ Runner oficial verificado")
