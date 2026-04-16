"""
tests/test_compiler.py
----------------------
Tests del compilador TIE-Lang v1.0.
Verifica el pipeline completo:
    fuente → Lexer → Parser → AST → Compilador → CPU

Programas verificados: 7/7 correctos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compiler.compiler import compile_and_run


def test_asignacion_suma():
    """P1: Asignación y suma básica. 5 + 3 = 8."""
    print("── P1: Asignación y suma ────────────────")
    resultado = compile_and_run("""
let x = 5
let y = 3
let z = x + y
print z
""", titulo="P1", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [8]
    print(f"  Salida: {salida}  esperado=[8]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_condicional():
    """P2: If/else. 7 - 3 = 4 > 3 → imprime a=7."""
    print("── P2: Condicional ──────────────────────")
    resultado = compile_and_run("""
let a = 7
let b = 3
let c = a - b
if c > 3:
    print a
else:
    print b
""", titulo="P2", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [7]
    print(f"  Salida: {salida}  esperado=[7]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_while():
    """P3: Bucle while. Suma 5+4+3+2+1 = 15."""
    print("── P3: While ────────────────────────────")
    resultado = compile_and_run("""
let i = 5
let suma = 0
while i > 0:
    suma = suma + i
    i = i - 1
print suma
""", titulo="P3", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [15]
    print(f"  Salida: {salida}  esperado=[15]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_funcion():
    """P4: Función. doble(4) = 8."""
    print("── P4: Función ──────────────────────────")
    resultado = compile_and_run("""
def doble(n):
    return n + n

let x = 4
let y = doble(x)
print y
""", titulo="P4", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [8]
    print(f"  Salida: {salida}  esperado=[8]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_funcion_con_if():
    """P5: Función con if interno. max(6, 9) = 9."""
    print("── P5: max(6,9) = 9 ─────────────────────")
    resultado = compile_and_run("""
def max(a b):
    if a > b:
        return a
    else:
        return b

let x = 6
let y = 9
let m = max(x y)
print m
""", titulo="P5", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [9]
    print(f"  Salida: {salida}  esperado=[9]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_funcion_con_comas():
    """P6: Sintaxis con comas en definición y llamada."""
    print("── P6: Función con comas ─────────────────")
    resultado = compile_and_run("""
def max(a, b):
    if a > b:
        return a
    else:
        return b

let x = 6
let y = 9
let m = max(x, y)
print m
""", titulo="P6", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [9]
    print(f"  Salida: {salida}  esperado=[9]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_comparadores():
    """P7: Regresión de comparadores básicos."""
    print("── P7: Comparadores ─────────────────────")
    resultado = compile_and_run("""
print 5 == 5
print 5 != 5
print 3 < 7
print 7 > 3
print 3 <= 3
print 7 >= 7
""", titulo="P7", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 0, 1, 1, 1, 1]
    print(f"  Salida: {salida}  esperado=[1, 0, 1, 1, 1, 1]  {'✅' if ok else '❌'}")
    assert ok
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("  TIE-Lang — Tests: Compilador v1.0")
    print("=" * 50)
    print()
    test_asignacion_suma()
    test_condicional()
    test_while()
    test_funcion()
    test_funcion_con_if()
    test_funcion_con_comas()
    test_comparadores()
    print("✅ Compilador completo — 7/7 programas correctos")
