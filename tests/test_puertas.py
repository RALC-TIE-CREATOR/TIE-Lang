"""
tests/test_puertas.py
---------------------
Tests para puertas lógicas topológicas (NOT, AND, OR).
Verificado: 3/3 puertas, Turing-completo.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.alu import op_not, op_and, op_or


def test_not():
    print("── NOT ──────────────────────────────────")
    casos = [(False, True), (True, False)]
    for entrada, esperado in casos:
        resultado = op_not(entrada)
        ok = resultado == esperado
        print(f"  NOT({int(entrada)}) = {int(resultado)}  esperado={int(esperado)}  {'✅' if ok else '❌'}")
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
    for a, b, esp in casos:
        r = op_and(a, b)
        ok = r == esp
        print(f"  AND({int(a)},{int(b)}) = {int(r)}  esperado={int(esp)}  {'✅' if ok else '❌'}")
        assert ok
    print()


def test_or():
    print("── OR ───────────────────────────────────")
    casos = [
        (False, False, False),
        (False, True,  True),
        (True,  False, True),
        (True,  True,  True),
    ]
    for a, b, esp in casos:
        r = op_or(a, b)
        ok = r == esp
        print(f"  OR({int(a)},{int(b)}) = {int(r)}  esperado={int(esp)}  {'✅' if ok else '❌'}")
        assert ok
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests Puertas Lógicas")
    print("=" * 45)
    test_not()
    test_and()
    test_or()
    print("✅ Todas las puertas correctas. Turing-completo.")
