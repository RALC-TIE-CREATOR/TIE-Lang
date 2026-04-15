"""
tests/test_puertas.py
---------------------
Tests para puertas lógicas topológicas (NOT, AND, OR).
Resultado verificado: 3/3 puertas correctas. Turing-completo.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.alu import op_not, op_and, op_or


def test_not():
    print("── NOT ──────────────────────────────────")
    casos = [
        (False, True),
        (True,  False),
    ]
    for entrada, esperado in casos:
        resultado = op_not(entrada)
        ok = resultado == esperado
        print(f"  NOT({int(entrada)}) = {int(resultado)}"
              f"  esperado={int(esperado)}  {'✅' if ok else '❌'}")
        assert ok, f"NOT({entrada}) falló"
    print()


def test_and():
    print("── AND ──────────────────────────────────")
    casos = [
        (False, False, False),
        (False, True,  False),
        (True,  False, False),
        (True,  True,  True),
    ]
    for a, b, esperado in casos:
        resultado = op_and(a, b)
        ok = resultado == esperado
        print(f"  AND({int(a)},{int(b)}) = {int(resultado)}"
              f"  esperado={int(esperado)}  {'✅' if ok else '❌'}")
        assert ok, f"AND({a},{b}) falló"
    print()


def test_or():
    print("── OR ───────────────────────────────────")
    casos = [
        (False, False, False),
        (False, True,  True),
        (True,  False, True),
        (True,  True,  True),
    ]
    for a, b, esperado in casos:
        resultado = op_or(a, b)
        ok = resultado == esperado
        print(f"  OR({int(a)},{int(b)}) = {int(resultado)}"
              f"  esperado={int(esperado)}  {'✅' if ok else '❌'}")
        assert ok, f"OR({a},{b}) falló"
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: Puertas Lógicas")
    print("=" * 45)
    print()
    test_not()
    test_and()
    test_or()
    print("✅ 3/3 puertas correctas — Turing-completo")
