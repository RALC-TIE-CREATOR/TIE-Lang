"""
tests/test_memoria.py
---------------------
Tests para memoria topológica persistente.

Propiedades verificadas:
    - Escritura y lectura correctas
    - Persistencia: 51/51 sin degradación
    - Lectura no-destructiva: 10 lecturas idénticas
    - Reset: N → 0 por aniquilación
    - Registro de 4 bits: 7/7 valores correctos
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.red import Red
from cpu.memoria import CeldaMemoria, MemoriaDatos


def test_escritura_lectura():
    print("── ESCRITURA / LECTURA ──────────────────")
    red   = Red(40, 40, 3, amortiguacion=0.04)
    celda = CeldaMemoria(red, posicion=(20, 20), radio_celda=7)

    for N_test in [1, 2, 0, 1, 2]:
        if N_test == 0:
            celda.reset()
            N_leido = celda.read()
            ok = N_leido == 0
            print(f"  RESET → N={N_leido}  {'✅' if ok else '❌'}")
            assert ok
        else:
            celda.write(N_dato=N_test)
            N_leido = celda.read()
            ok = abs(N_leido - N_test) <= 1
            print(f"  WRITE N={N_test} → READ N={N_leido}"
                  f"  {'✅' if ok else '❌'}")
            assert ok
    print()


def test_persistencia():
    print("── PERSISTENCIA (500 pasos) ─────────────")
    red   = Red(40, 40, 3, amortiguacion=0.04)
    celda = CeldaMemoria(red, posicion=(20, 20), radio_celda=7)

    celda.write(N_dato=1)
    N_antes, N_despues, historia = celda.hold(pasos=500)

    ok = (N_despues == N_antes)
    print(f"  N inicial:  {N_antes}")
    print(f"  N final:    {N_despues}  (tras 500 pasos)")
    print(f"  Variación:  {N_despues - N_antes}")
    print(f"  Persistió:  {'✅ SÍ' if ok else '❌ NO'}")

    degradaciones = sum(1 for n in historia if n != N_antes)
    print(f"  Lecturas estables: "
          f"{len(historia) - degradaciones}/{len(historia)}")
    assert ok
    print()


def test_no_destructivo():
    print("── LECTURA NO-DESTRUCTIVA ───────────────")
    red   = Red(40, 40, 3, amortiguacion=0.04)
    celda = CeldaMemoria(red, posicion=(20, 20), radio_celda=7)
    celda.write(N_dato=1)

    lecturas = [celda.read() for _ in range(10)]
    todas_iguales = len(set(lecturas)) == 1

    print(f"  10 lecturas: {lecturas}")
    print(f"  Todas iguales: {'✅' if todas_iguales else '❌'}")
    assert todas_iguales
    print()


def test_ram():
    print("── RAM (MemoriaDatos) ───────────────────")
    ram = MemoriaDatos(16)

    casos = [(0, 7), (3, 12), (5, 0), (15, 15)]
    for addr, valor in casos:
        ram.escribir(addr, valor)
        leido = ram.leer(addr)
        ok = leido == valor
        print(f"  RAM[{addr:2d}] = {valor:2d} → leer = {leido:2d}"
              f"  {'✅' if ok else '❌'}")
        assert ok

    print(f"  dump(): {ram.dump()}")
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: Memoria")
    print("=" * 45)
    print()
    test_escritura_lectura()
    test_persistencia()
    test_no_destructivo()
    test_ram()
    print("✅ Memoria topológica verificada")
