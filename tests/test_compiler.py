"""
tests/test_compiler.py
----------------------
Tests del compilador TIE-Lang v1.0.
Verifica el pipeline completo:
    fuente → Lexer → Parser → AST → Compilador → CPU

Programas verificados: 31/31 correctos.
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


def test_scope_local_shadowing():
    """P8: Los locales de función sombrean globals sin mutarlos."""
    print("── P8: Scope local/shadowing ────────────")
    resultado = compile_and_run("""
let x = 2

def doble_local(x):
    let y = x + x
    return y

print doble_local(5)
print x
""", titulo="P8", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [10, 2]
    print(f"  Salida: {salida}  esperado=[10, 2]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_scope_global_read():
    """P9: Una función puede leer globals si no hay local con ese nombre."""
    print("── P9: Scope lectura global ─────────────")
    resultado = compile_and_run("""
let base = 3

def sumar_base(n):
    let z = n + base
    return z

print sumar_base(4)
print base
""", titulo="P9", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [7, 3]
    print(f"  Salida: {salida}  esperado=[7, 3]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_scope_locals_do_not_leak():
    """P10: Variables locales no contaminan la RAM global visible por nombre."""
    print("── P10: Scope sin fuga local ────────────")
    resultado = compile_and_run("""
let a = 1

def crear_local(n):
    let temp = n + 1
    return temp

print crear_local(6)
print a
""", titulo="P10", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [7, 1]
    print(f"  Salida: {salida}  esperado=[7, 1]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_global_assignment_from_function():
    """P11: Una función puede escribir explícitamente a un global."""
    print("── P11: Escritura global ─────────────────")
    resultado = compile_and_run("""
let contador = 1

def subir(n):
    global contador = contador + n
    return contador

print subir(3)
print contador
""", titulo="P11", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [4, 4]
    print(f"  Salida: {salida}  esperado=[4, 4]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_global_assignment_with_shadowing():
    """P12: global x = ... actualiza el global aunque exista un local x."""
    print("── P12: Global con shadowing ─────────────")
    resultado = compile_and_run("""
let total = 2

def ajustar(total):
    let local = total + 1
    global total = local + 5
    return local

print ajustar(4)
print total
""", titulo="P12", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [5, 10]
    print(f"  Salida: {salida}  esperado=[5, 10]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_block_scope_shadowing_inside_function():
    """P13: let dentro de if crea shadowing local de bloque."""
    print("── P13: Scope de bloque/shadowing ───────")
    resultado = compile_and_run("""
def prueba():
    let total = 1
    if 1:
        let total = 5
        print total
    print total

prueba()
""", titulo="P13", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [5, 1]
    print(f"  Salida: {salida}  esperado=[5, 1]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_block_assignment_updates_outer_scope():
    """P14: asignacion sin let dentro de bloque actualiza el scope exterior."""
    print("── P14: Scope de bloque/actualizacion ──")
    resultado = compile_and_run("""
def prueba():
    let total = 1
    if 1:
        total = total + 4
    print total

prueba()
""", titulo="P14", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [5]
    print(f"  Salida: {salida}  esperado=[5]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_multiplicacion_y_precedencia():
    """P15: Multiplicacion y precedencia aritmetica."""
    print("── P15: Multiplicacion ──────────────────")
    resultado = compile_and_run("""
print 2 + 3 * 4
print (2 + 3) * 2
print 3 * 5
""", titulo="P15", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [14, 10, 15]
    print(f"  Salida: {salida}  esperado=[14, 10, 15]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_operadores_logicos():
    """P16: not, and, or con booleanos normalizados."""
    print("── P16: Operadores logicos ──────────────")
    resultado = compile_and_run("""
print not 0
print not 3
print 1 and 0
print 2 and 7
print 0 or 5
print 0 or 0
print (3 < 4) and (2 < 1)
print (3 < 4) or (2 < 1)
""", titulo="P16", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 0, 0, 1, 1, 0, 0, 1]
    print(f"  Salida: {salida}  esperado=[1, 0, 0, 1, 1, 0, 0, 1]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_comparaciones_encadenadas_y_bool():
    """P17: comparaciones encadenadas y literales true/false."""
    print("── P17: Comparaciones encadenadas ───────")
    resultado = compile_and_run("""
print 1 < 2 < 3
print 1 < 2 > 3
print true and not false
print false or (2 <= 2)
""", titulo="P17", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 0, 1, 1]
    print(f"  Salida: {salida}  esperado=[1, 0, 1, 1]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_elif():
    """P18: elif selecciona la rama intermedia correcta."""
    print("── P18: Elif ────────────────────────────")
    resultado = compile_and_run("""
let x = 3
if x == 1:
    print 1
elif x == 3:
    print 2
else:
    print 9
""", titulo="P18", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [2]
    print(f"  Salida: {salida}  esperado=[2]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_break():
    """P19: break sale del while cuando se cumple la condicion interna."""
    print("── P19: Break ───────────────────────────")
    resultado = compile_and_run("""
let i = 0
while i < 6:
    if i == 3:
        break
    print i
    i = i + 1
print 9
""", titulo="P19", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [0, 1, 2, 9]
    print(f"  Salida: {salida}  esperado=[0, 1, 2, 9]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_continue():
    """P20: continue salta al siguiente ciclo sin ejecutar el resto del cuerpo."""
    print("── P20: Continue ────────────────────────")
    resultado = compile_and_run("""
let i = 0
while i < 5:
    i = i + 1
    if i == 3:
        continue
    print i
""", titulo="P20", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 2, 4, 5]
    print(f"  Salida: {salida}  esperado=[1, 2, 4, 5]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_arreglos_indice_constante():
    """P21: literal de arreglo y lectura por indice constante."""
    print("── P21: Arreglos / indice constante ─────")
    resultado = compile_and_run("""
let xs = [2, 4, 6]
print xs[0]
print xs[2]
""", titulo="P21", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [2, 6]
    print(f"  Salida: {salida}  esperado=[2, 6]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_arreglos_mutacion():
    """P22: escritura a arreglo por indice constante."""
    print("── P22: Arreglos / mutacion ─────────────")
    resultado = compile_and_run("""
let xs = [1, 2, 3]
xs[1] = 9
print xs[0]
print xs[1]
print xs[2]
""", titulo="P22", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 9, 3]
    print(f"  Salida: {salida}  esperado=[1, 9, 3]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_arreglos_indice_dinamico():
    """P23: lectura y escritura con indice variable."""
    print("── P23: Arreglos / indice dinamico ──────")
    resultado = compile_and_run("""
let xs = [3, 5, 7]
let i = 1
print xs[i]
i = 2
xs[i] = 9
print xs[2]
""", titulo="P23", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [5, 9]
    print(f"  Salida: {salida}  esperado=[5, 9]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_arreglos_locales_en_funcion():
    """P24: una funcion puede declarar y mutar su propio arreglo local."""
    print("── P24: Arreglos locales en funcion ─────")
    resultado = compile_and_run("""
def prueba():
    let xs = [1, 2, 3]
    xs[1] = 8
    print xs[0]
    print xs[1]

prueba()
""", titulo="P24", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 8]
    print(f"  Salida: {salida}  esperado=[1, 8]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_lectura_de_arreglo_global_desde_funcion():
    """P25: una funcion puede leer un arreglo global si no esta sombreado."""
    print("── P25: Arreglo global leido en funcion ─")
    resultado = compile_and_run("""
let datos = [4, 6, 9]

def leer(i):
    return datos[i]

print leer(2)
print datos[0]
""", titulo="P25", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [9, 4]
    print(f"  Salida: {salida}  esperado=[9, 4]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_shadowing_escalar_sobre_arreglo_global():
    """P26: un escalar local sombrea un arreglo global con el mismo nombre."""
    print("── P26: Scalar sombreando arreglo global ─")
    resultado = compile_and_run("""
let xs = [3, 5, 7]

def prueba():
    let xs = 9
    print xs

prueba()
print xs[1]
""", titulo="P26", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [9, 5]
    print(f"  Salida: {salida}  esperado=[9, 5]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_shadowing_de_arreglo_en_bloque():
    """P27: let de arreglo dentro de bloque crea shadowing local del global."""
    print("── P27: Arreglo local de bloque ─────────")
    resultado = compile_and_run("""
let xs = [1, 2, 3]

def prueba():
    if true:
        let xs = [8, 9]
        print xs[0]
        xs[1] = 6
        print xs[1]
    print xs[2]

prueba()
print xs[1]
""", titulo="P27", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [8, 6, 3, 2]
    print(f"  Salida: {salida}  esperado=[8, 6, 3, 2]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_arreglo_como_argumento_por_copia():
    """P28: los arreglos se pasan a funciones por copia controlada."""
    print("── P28: Arreglo como argumento ──────────")
    resultado = compile_and_run("""
def tocar(xs):
    print xs[1]
    xs[1] = 9
    print xs[1]

let datos = [2, 4, 6]
tocar(datos)
print datos[1]
""", titulo="P28", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [4, 9, 4]
    print(f"  Salida: {salida}  esperado=[4, 9, 4]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_builtins_de_arreglo():
    """P29: len, first y last funcionan sobre arreglos."""
    print("── P29: Builtins de arreglo ─────────────")
    resultado = compile_and_run("""
let xs = [5, 7, 9]
print len(xs)
print first(xs)
print last(xs)
print len([1, 2, 3, 4])
""", titulo="P29", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [3, 5, 9, 4]
    print(f"  Salida: {salida}  esperado=[3, 5, 9, 4]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_funcion_con_arreglo_literal():
    """P30: una funcion puede recibir un literal de arreglo."""
    print("── P30: Literal de arreglo en funcion ───")
    resultado = compile_and_run("""
def bordes(xs):
    return first(xs) + last(xs)

print bordes([2, 3, 4])
""", titulo="P30", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [6]
    print(f"  Salida: {salida}  esperado=[6]  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_simbolos_ligeros():
    """P31: los simbolos ligeros compilan a etiquetas compactas comparables."""
    print("── P31: Simbolos ligeros ─────────────────")
    resultado = compile_and_run("""
let inicio = @inicio
let fin = @fin

print inicio == @inicio
print inicio == fin

def clasificar(x):
    if x == @inicio:
        print 7
    else:
        print 9

clasificar(inicio)
clasificar(fin)
""", titulo="P31", verbose_asm=False)

    salida = resultado['salida']
    ok = salida == [1, 0, 7, 9]
    print(f"  Salida: {salida}  esperado=[1, 0, 7, 9]  {'✅' if ok else '❌'}")
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
    test_scope_local_shadowing()
    test_scope_global_read()
    test_scope_locals_do_not_leak()
    test_global_assignment_from_function()
    test_global_assignment_with_shadowing()
    test_block_scope_shadowing_inside_function()
    test_block_assignment_updates_outer_scope()
    test_multiplicacion_y_precedencia()
    test_operadores_logicos()
    test_comparaciones_encadenadas_y_bool()
    test_elif()
    test_break()
    test_continue()
    test_arreglos_indice_constante()
    test_arreglos_mutacion()
    test_arreglos_indice_dinamico()
    test_arreglos_locales_en_funcion()
    test_lectura_de_arreglo_global_desde_funcion()
    test_shadowing_escalar_sobre_arreglo_global()
    test_shadowing_de_arreglo_en_bloque()
    test_arreglo_como_argumento_por_copia()
    test_builtins_de_arreglo()
    test_funcion_con_arreglo_literal()
    test_simbolos_ligeros()
    print("✅ Compilador completo — 31/31 programas correctos")
