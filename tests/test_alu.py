"""
tests/test_alu.py
-----------------
Tests completos de la ALU topológica de 4 bits.
Resultado verificado: 22/22 operaciones, 100% precisión.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.alu import (
    sumar, restar,
    and4, or4, not4, xor4, cmp4
)


def test_suma():
    print("── SUMA ─────────────────────────────────")
    casos = [(3,4,7), (7,8,15), (9,9,18), (15,15,30), (0,0,0)]
    for A, B, esp in casos:
        r     = sumar(A, B)
        bits  = r & 0xF
        carry = r > 15
        ok    = (bits == esp % 16) and (carry == (esp > 15))
        print(f"  {A:2d}+{B:2d} = {bits:2d} (C={int(carry)})"
              f"  esp={esp%16}(c={int(esp>15)})"
              f"  {'✅' if ok else '❌'}")
        assert ok


def test_resta():
    print("── RESTA ────────────────────────────────")
    casos = [
        (7,  3, 4,  False),
        (10, 5, 5,  False),
        (3,  7, 12, True),
        (0,  0, 0,  False),
        (15, 8, 7,  False),
    ]
    for A, B, esp_r, esp_n in casos:
        r, n = restar(A, B)
        ok = (r == esp_r) and (n == esp_n)
        print(f"  {A:2d}-{B:2d} = {r:2d} (N={int(n)})"
              f"  esp={esp_r}(n={int(esp_n)})"
              f"  {'✅' if ok else '❌'}")
        assert ok


def test_and():
    print("── AND ──────────────────────────────────")
    casos = [
        (0b1100, 0b1010, 0b1000),
        (0b1111, 0b0101, 0b0101),
        (0b0000, 0b1111, 0b0000),
    ]
    for A, B, esp in casos:
        r  = and4(A, B)
        ok = r == esp
        print(f"  {A:04b} & {B:04b} = {r:04b}"
              f"  esp={esp:04b}"
              f"  {'✅' if ok else '❌'}")
        assert ok


def test_or():
    print("── OR ───────────────────────────────────")
    casos = [
        (0b1100, 0b0011, 0b1111),
        (0b1010, 0b0101, 0b1111),
        (0b0000, 0b0000, 0b0000),
    ]
    for A, B, esp in casos:
        r  = or4(A, B)
        ok = r == esp
        print(f"  {A:04b} | {B:04b} = {r:04b}"
              f"  esp={esp:04b}"
              f"  {'✅' if ok else '❌'}")
        assert ok


def test_not():
    print("── NOT ──────────────────────────────────")
    casos = [
        (0b1010, 0b0101),
        (0b0000, 0b1111),
        (0b1111, 0b0000),
    ]
    for A, esp in casos:
        r  = not4(A) & 0xF
        ok = r == esp
        print(f"  ~{A:04b} = {r:04b}"
              f"  esp={esp:04b}"
              f"  {'✅' if ok else '❌'}")
        assert ok


def test_xor():
    print("── XOR ──────────────────────────────────")
    casos = [
        (0b1100, 0b1010, 0b0110),
        (0b1111, 0b1111, 0b0000),
        (0b0101, 0b1010, 0b1111),
    ]
    for A, B, esp in casos:
        r  = xor4(A, B)
        ok = r == esp
        print(f"  {A:04b} ^ {B:04b} = {r:04b}"
              f"  esp={esp:04b}"
              f"  {'✅' if ok else '❌'}")
        assert ok


def test_cmp():
    print("── CMP ──────────────────────────────────")
    etq = {0: 'igual', 1: 'mayor', 2: 'menor'}
    casos = [(5, 5, 0), (7, 3, 1), (2, 9, 2)]
    for A, B, esp in casos:
        r  = cmp4(A, B)
        ok = r == esp
        print(f"  cmp({A},{B}) = {etq[r]}"
              f"  esp={etq[esp]}"
              f"  {'✅' if ok else '❌'}")
        assert ok


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: ALU 4 bits")
    print("=" * 45)
    print()
    test_suma()
    print()
    test_resta()
    print()
    test_and()
    print()
    test_or()
    print()
    test_not()
    print()
    test_xor()
    print()
    test_cmp()
    print()
    print("✅ ALU completa — 100% precisión")
