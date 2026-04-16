"""
tests/test_cpu.py
-----------------
Tests de la CPU TIE-Lang completa.
Ciclo fetch → decode → execute.

Programas verificados: 4/4 correctos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cpu.instrucciones import Operacion
from cpu.memoria import MemoriaDatos
from cpu.cpu import CPU


def I(op, dest=None, src1=None, src2=None, label=None):
    from cpu.instrucciones import Instruccion
    return Instruccion(op, dest, src1, src2, label)


def test_hola_mundo():
    """3 + 4 = 7."""
    print("── P1: Hola Mundo (3+4=7) ───────────────")
    cpu = CPU()
    resultado = cpu.run([
        I(Operacion.LOAD, 'R0', '3'),
        I(Operacion.LOAD, 'R1', '4'),
        I(Operacion.SUMA, 'R2', 'R0', 'R1'),
        I(Operacion.PRINT, None, 'R2'),
        I(Operacion.HALT),
    ], verbose=False)

    r = resultado['regs']['R2']
    ok = r == 7
    print(f"  R2 = {r}  esperado=7  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_fibonacci():
    """Fibonacci de 4 bits con contador fijo: 0,1,1,2,3,5,8,13."""
    print("── P2: Fibonacci ────────────────────────")
    cpu = CPU()
    resultado = cpu.run([
        I(Operacion.LOAD,  'R0', '0'),
        I(Operacion.LOAD,  'R1', '1'),
        I(Operacion.LOAD,  'R3', '6'),
        I(Operacion.PRINT, None, 'R0'),
        I(Operacion.PRINT, None, 'R1'),
        # bucle:
        I(Operacion.CMP,   None, 'R3', '0', label='loop'),
        I(Operacion.JZ,    None, 'fin'),
        I(Operacion.SUMA,  'R2', 'R0', 'R1'),
        I(Operacion.PRINT, None, 'R2'),
        I(Operacion.MOVE,  'R0', 'R1'),
        I(Operacion.MOVE,  'R1', 'R2'),
        I(Operacion.RESTA, 'R3', 'R3', '1'),
        I(Operacion.JMP,   None, 'loop'),
        # fin:
        I(Operacion.HALT,  label='fin'),
    ], verbose=False)

    salida = resultado['salida']
    esperado = [0, 1, 1, 2, 3, 5, 8, 13]
    ok = salida == esperado
    print(f"  Salida:   {salida}")
    print(f"  Esperado: {esperado}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_busqueda_ram():
    """Busca el valor 9 en RAM[0..4] = [3,7,1,9,5]."""
    print("── P3: Búsqueda en RAM ──────────────────")
    cpu = CPU()

    for addr, val in enumerate([3, 7, 1, 9, 5]):
        cpu.ram.escribir(addr, val)

    resultado = cpu.run([
        I(Operacion.LOAD,   'R0', '0'),
        I(Operacion.LOAD,   'R3', '9'),
        # bucle:
        I(Operacion.LOAD_M, 'R1', 'R0'),
        I(Operacion.CMP,    None, 'R1', 'R3'),
        I(Operacion.JZ,     None, 'encontrado'),
        I(Operacion.SUMA,   'R0', 'R0', '1'),
        I(Operacion.CMP,    None, 'R0', '5'),
        I(Operacion.JZ,     None, 'noencontrado'),
        I(Operacion.JMP,    None, '2'),
        # encontrado:
        I(Operacion.PRINT,  None, 'R0', label='encontrado'),
        I(Operacion.HALT),
        # no encontrado:
        I(Operacion.LOAD,   'R0', '15', label='noencontrado'),
        I(Operacion.PRINT,  None, 'R0'),
        I(Operacion.HALT),
    ], verbose=False)

    idx = resultado['regs']['R0']
    ok  = idx == 3
    print(f"  Índice encontrado: {idx}  esperado=3  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_call_ret():
    """Subrutina: CALL y RET."""
    print("── P4: CALL / RET ───────────────────────")
    cpu = CPU()
    resultado = cpu.run([
        I(Operacion.LOAD,  'R0', '5'),
        I(Operacion.CALL,  None, 'doble'),
        I(Operacion.PRINT, None, 'R3'),
        I(Operacion.HALT),
        # subrutina doble: R3 = R0 + R0
        I(Operacion.SUMA, 'R3', 'R0', 'R0', label='doble'),
        I(Operacion.RET),
    ], verbose=False)

    r = resultado['regs']['R3']
    ok = r == 10
    print(f"  doble(5) = {r}  esperado=10  {'✅' if ok else '❌'}")
    assert ok
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: CPU")
    print("=" * 45)
    print()
    test_hola_mundo()
    test_fibonacci()
    test_busqueda_ram()
    test_call_ret()
    print("✅ CPU completa — 4/4 programas correctos")
