"""
tests/test_aritmetica.py
------------------------
Tests para aritmética topológica.
Half Adder, Full Adder, suma de 4 bits.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.alu import half_adder, full_adder, sumar


def test_half_adder():
    print("── HALF ADDER ───────────────────────────")
    casos = [
        (False, False, 0, 0),
        (False, True,  1, 0),
        (True,  False, 1, 0),
        (True,  True,  0, 1),
    ]
    for a, b, esp_s, esp_c in casos:
        s, c = half_adder(a, b)
        ok = (s == esp_s) and (c == esp_c)
        print(f"  HA({int(a)},{int(b)}) → S={s},C={c}"
              f"  esperado S={esp_s},C={esp_c}"
              f"  {'✅' if ok else '❌'}")
        assert ok, f"HalfAdder({a},{b}) falló"
    print()


def test_full_adder():
    print("── FULL ADDER ───────────────────────────")
    casos = [
        (0, 0, 0,  0, 0),
        (0, 1, 0,  1, 0),
        (1, 0, 0,  1, 0),
        (1, 1, 0,  0, 1),
        (1, 1, 1,  1, 1),
    ]
    for a, b, cin, esp_s, esp_c in casos:
        s, c = full_adder(bool(a), bool(b), bool(cin))
        ok = (s == esp_s) and (c == esp_c)
        print(f"  FA({a},{b},Cin={cin}) → S={s},C={c}"
              f"  esperado S={esp_s},C={esp_c}"
              f"  {'✅' if ok else '❌'}")
        assert ok, f"FullAdder({a},{b},{cin}) falló"
    print()


def test_suma_4bits():
    print("── SUMA 4 BITS ──────────────────────────")
    casos = [
        (5,  3,  8),
        (7,  8,  15),
        (9,  9,  18),
        (12, 11, 23),
        (15, 15, 30),
        (0,  0,  0),
    ]
    for A, B, esperado in casos:
        resultado = sumar(A, B)
        ok = resultado == esperado
        print(f"  {A:2d} + {B:2d} = {resultado:2d}"
              f"  esperado={esperado}"
              f"  {'✅' if ok else '❌'}")
        assert ok, f"sumar({A},{B}) = {resultado}, esperado {esperado}"
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: Aritmética")
    print("=" * 45)
    print()
    test_half_adder()
    test_full_adder()
    test_suma_4bits()
    print("✅ Aritmética topológica completa")
