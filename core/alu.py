"""
core/alu.py
-----------
Operaciones lógicas y aritméticas implementadas mediante
interacción topológica de vórtices en la Red sine-Gordon.

Alfabeto TIE-Lang:
    N = 8  →  "1" lógico  (protón)
    N = 9  →  "0" lógico  (electrón)
    N = 4  →  null/pointer (neutrino)
    N = 7  →  operador    (bosón W/Z)

Todas las funciones crean redes temporales, ejecutan la
física, leen el resultado topológico y descartan la red.
El cómputo es la evolución natural del campo — no el código.
"""

from .red import Red
from .vortice import medir_N


# ─────────────────────────────────────────────────────────────────────
# PRIMITIVAS DE 1 BIT
# ─────────────────────────────────────────────────────────────────────

def op_not(a: bool) -> bool:
    """
    Puerta NOT topológica.
    Mecanismo: vórtice N_in + antivórtice N=-N_in → salida N=-N_in
    La señal emerge invertida en el punto C.
    """
    red = Red(60, 60, 3, amortiguacion=0.05)
    N = 8 if a else 9
    red.insertar_vortice(10, 30, N=N,  radio=6)
    red.insertar_vortice(30, 30, N=-N, radio=6)
    red.evolucionar(pasos=80)
    return abs(medir_N(red.fases, 50, 30, radio=4)) >= 7


def op_and(a: bool, b: bool) -> bool:
    """
    Puerta AND topológica.
    Mecanismo: sumidero N=-8 en la unión J.
    - 1 señal sola: N_total = 8+(-8) = 0 → nada en salida
    - 2 señales:    N_total = 8+8+(-8) = 8 → vórtice en salida
    """
    red = Red(70, 60, 3, amortiguacion=0.08)
    red.insertar_vortice(35, 30, N=-8, radio=5)
    if a: red.insertar_vortice(15, 40, N=8, radio=5)
    if b: red.insertar_vortice(15, 20, N=8, radio=5)
    red.evolucionar(pasos=120, dt=0.08)
    return abs(medir_N(red.fases, 55, 30, radio=4)) >= 7


def op_or(a: bool, b: bool) -> bool:
    """
    Puerta OR topológica.
    Mecanismo: sin sumidero — cualquier señal pasa.
    OR(1,1) produce N=16 en la salida (suma topológica natural).
    """
    red = Red(70, 60, 3, amortiguacion=0.08)
    if a: red.insertar_vortice(15, 40, N=8, radio=5)
    if b: red.insertar_vortice(15, 20, N=8, radio=5)
    red.evolucionar(pasos=120, dt=0.08)
    return abs(medir_N(red.fases, 55, 30, radio=4)) >= 1


# ─────────────────────────────────────────────────────────────────────
# ARITMÉTICA DE 1 BIT
# ─────────────────────────────────────────────────────────────────────

def _half_adder(a: bool, b: bool):
    """
    Medio sumador topológico.
    N_total = 0  → S=0, C=0
    N_total = 8  → S=1, C=0
    N_total = 16 → S=0, C=1  (desbordamiento)
    """
    red = Red(70, 60, 3, amortiguacion=0.06)
    if a: red.insertar_vortice(15, 40, N=8, radio=5)
    if b: red.insertar_vortice(15, 20, N=8, radio=5)
    red.evolucionar(pasos=150, dt=0.08)
    N = medir_N(red.fases, 45, 30, radio=5)
    return int((N % 16) >= 7), int(N >= 16)


def _full_adder(a: bool, b: bool, cin: bool):
    """Sumador completo: compone dos medios sumadores."""
    s1, c1 = _half_adder(a, b)
    s,  c2 = _half_adder(bool(s1), cin)
    return int(s), int(bool(c1) or bool(c2))


# ─────────────────────────────────────────────────────────────────────
# OPERACIONES DE 4 BITS
# ─────────────────────────────────────────────────────────────────────

def sumar(A: int, B: int) -> int:
    """Suma A + B (4 bits). Retorna hasta 5 bits (con carry)."""
    bA = [(A >> i) & 1 for i in range(4)]
    bB = [(B >> i) & 1 for i in range(4)]
    carry = 0
    bits  = []
    for i in range(4):
        s, carry = _full_adder(bool(bA[i]), bool(bB[i]), bool(carry))
        bits.append(s)
    bits.append(carry)
    return sum(bits[i] * 2**i for i in range(5))


def restar(A: int, B: int):
    """
    Resta A - B por complemento a 2.
    Retorna (resultado 4 bits, flag_negativo).
    """
    B_comp2  = ((~B) & 0xF) + 1
    resultado = sumar(A, B_comp2) & 0xF
    return resultado, A < B


def and4(A: int, B: int) -> int:
    bA = [(A >> i) & 1 for i in range(4)]
    bB = [(B >> i) & 1 for i in range(4)]
    bR = [int(op_and(bool(a), bool(b))) for a, b in zip(bA, bB)]
    return sum(bR[i] * 2**i for i in range(4))


def or4(A: int, B: int) -> int:
    bA = [(A >> i) & 1 for i in range(4)]
    bB = [(B >> i) & 1 for i in range(4)]
    bR = [int(op_or(bool(a), bool(b))) for a, b in zip(bA, bB)]
    return sum(bR[i] * 2**i for i in range(4))


def not4(A: int) -> int:
    bA = [(A >> i) & 1 for i in range(4)]
    bR = [int(op_not(bool(a))) for a in bA]
    return sum(bR[i] * 2**i for i in range(4))


def xor4(A: int, B: int) -> int:
    return and4(or4(A, B), not4(and4(A, B)))


def cmp4(A: int, B: int) -> int:
    """
    Compara A vs B.
    Retorna: 0 = igual, 1 = A>B, 2 = A<B
    """
    if xor4(A, B) == 0:
        return 0
    _, negativo = restar(A, B)
    return 2 if negativo else 1
