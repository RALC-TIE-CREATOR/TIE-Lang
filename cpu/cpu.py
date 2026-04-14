"""
cpu/cpu.py
----------
CPU TIE-Lang de 4 bits. Ciclo fetch → decode → execute.

Arquitectura:
    Registros : R0, R1, R2, R3  (propósito general, 4 bits)
    PC        : Program Counter
    Flags     : Z (zero), N (negative), C (carry)
    RAM       : 16 × 4 bits
    Stack     : para CALL/RET

Todas las operaciones aritméticas y lógicas delegan
a core/alu.py, que usa física de vórtices topológicos.
"""

from typing import List, Dict, Optional
from .instrucciones import Instruccion, Operacion
from .memoria import MemoriaPrograma, MemoriaDatos
from ..core.alu import (
    sumar, restar, and4, or4, not4, xor4, cmp4
)


class CPU:
    """
    CPU topológica de 4 bits.

    El ciclo de ejecución:
        1. FETCH   — leer instrucción en PC
        2. DECODE  — resolver operandos
        3. EXECUTE — ALU topológica
        4. UPDATE  — registros, flags, PC
    """

    REGISTROS = ('R0', 'R1', 'R2', 'R3')

    def __init__(self):
        self.regs:   Dict[str, int] = {r: 0 for r in self.REGISTROS}
        self.PC:     int   = 0
        self.Z:      bool  = False
        self.N:      bool  = False
        self.C:      bool  = False
        self.ram:    MemoriaDatos = MemoriaDatos()
        self.pila:   List[int]    = []
        self.activo: bool  = True
        self.ciclos: int   = 0
        self.traza:  List[str] = []
        self.salida: List[int] = []

    # ── Lectura de operandos ──────────────────

    def _leer(self, src) -> int:
        """Resuelve un operando: registro, inmediato o @dirección."""
        if src is None:
            return 0
        if src in self.regs:
            return self.regs[src]
        if str(src).startswith('@'):
            return self.ram.leer(int(str(src)[1:]))
        try:
            return int(src) & 0xF
        except (ValueError, TypeError):
            return 0

    def _flags(self, resultado: int,
               carry: bool = False,
               negativo: bool = False):
        self.Z = (resultado == 0)
        self.N = negativo
        self.C = carry

    def _log(self, msg: str):
        self.traza.append(f"  [{self.ciclos:3d}] {msg}")

    # ── Ejecución ─────────────────────────────

    def execute(self, instr: Instruccion, mem: MemoriaPrograma):
        """Ejecuta una instrucción. Actualiza PC."""
        A  = self._leer(instr.src1)
        B  = self._leer(instr.src2)
        op = instr.op
        r  = 0

        # ── TRANSFERENCIA ─────────────────────
        if op == Operacion.LOAD:
            r = A
            self._log(f"LOAD {instr.dest} ← {A}")

        elif op == Operacion.LOAD_M:
            r = self.ram.leer(A)
            self._log(f"LOAD_M {instr.dest} ← RAM[{A}]={r}")

        elif op == Operacion.STORE:
            self.ram.escribir(int(instr.src2), A)
            self._log(f"STORE RAM[{instr.src2}] ← {A}")
            self.PC += 1
            return

        elif op == Operacion.MOVE:
            r = A
            self._log(f"MOVE {instr.dest} ← {A}")

        # ── ARITMÉTICA ────────────────────────
        elif op == Operacion.SUMA:
            ext   = sumar(A, B)
            carry = ext > 15
            r     = ext & 0xF
            self._flags(r, carry=carry)
            self._log(f"SUMA {instr.dest} = {A}+{B} = {r} (C={int(carry)})")

        elif op == Operacion.RESTA:
            r, neg = restar(A, B)
            r &= 0xF
            self._flags(r, negativo=neg)
            self._log(f"RESTA {instr.dest} = {A}-{B} = {r} (N={int(neg)})")

        # ── LÓGICA ────────────────────────────
        elif op == Operacion.AND:
            r = and4(A, B)
            self._flags(r)
            self._log(f"AND {instr.dest} = {A:04b}&{B:04b} = {r:04b}")

        elif op == Operacion.OR:
            r = or4(A, B)
            self._flags(r)
            self._log(f"OR {instr.dest} = {A:04b}|{B:04b} = {r:04b}")

        elif op == Operacion.NOT:
            r = not4(A) & 0xF
            self._flags(r)
            self._log(f"NOT {instr.dest} = ~{A:04b} = {r:04b}")

        elif op == Operacion.XOR:
            r = xor4(A, B)
            self._flags(r)
            self._log(f"XOR {instr.dest} = {A:04b}^{B:04b} = {r:04b}")

        elif op == Operacion.CMP:
            c = cmp4(A, B)
            self.Z = (c == 0)
            self.N = (c == 2)
            label = ['=', '>', '<'][c]
            self._log(f"CMP {instr.src1}({A}) {label} {instr.src2}({B})")
            self.PC += 1
            return

        # ── SALTOS ────────────────────────────
        elif op == Operacion.JMP:
            d = mem.resolver(instr.src1)
            self.PC = d if d >= 0 else int(instr.src1)
            self._log(f"JMP → PC={self.PC}")
            return

        elif op == Operacion.JZ:
            if self.Z:
                d = mem.resolver(instr.src1)
                self.PC = d if d >= 0 else int(instr.src1)
                self._log(f"JZ  → SALTA PC={self.PC}")
            else:
                self._log("JZ  → no salta")
                self.PC += 1
            return

        elif op == Operacion.JN:
            if self.N:
                d = mem.resolver(instr.src1)
                self.PC = d if d >= 0 else int(instr.src1)
                self._log(f"JN  → SALTA PC={self.PC}")
            else:
                self._log("JN  → no salta")
                self.PC += 1
            return

        # ── SUBRUTINAS ────────────────────────
        elif op == Operacion.CALL:
            self.pila.append(self.PC + 1)
            d = mem.resolver(instr.src1)
            self.PC = d if d >= 0 else int(instr.src1)
            self._log(f"CALL → {instr.src1}")
            return

        elif op == Operacion.RET:
            self.PC = self.pila.pop() if self.pila else 0
            self._log(f"RET → PC={self.PC}")
            return

        # ── CONTROL ───────────────────────────
        elif op == Operacion.HALT:
            self._log("HALT")
            self.activo = False
            return

        elif op == Operacion.PRINT:
            v = self._leer(instr.src1)
            self.salida.append(v)
            print(f"    📤 {instr.src1} = {v} ({v:04b})")
            self._log(f"PRINT {instr.src1}={v}")
            self.PC += 1
            return

        # ── ESCRIBIR RESULTADO ─────────────────
        if instr.dest and instr.dest in self.regs:
            self.regs[instr.dest] = r & 0xF
        self.PC     += 1
        self.ciclos += 1

    # ── Ejecución completa ────────────────────

    def run(self, programa: List[Instruccion],
            max_ciclos: int = 500,
            verbose: bool = True) -> dict:
        """
        Ejecuta un programa completo.
        Retorna dict con registros, flags y salida.
        """
        mem = MemoriaPrograma(programa)
        self.activo = True
        self.PC     = 0
        self.ciclos = 0
        self.traza  = []
        self.salida = []

        if verbose:
            print(f"  {'─'*50}")
            print(f"  Ejecutando ({len(programa)} instrucciones)")
            print(f"  {'─'*50}")

        while self.activo and self.ciclos < max_ciclos:
            instr = mem.fetch(self.PC)
            if instr is None:
                break
            self.execute(instr, mem)
            self.ciclos += 1

        if verbose:
            print("\n  TRAZA:")
            for l in self.traza[-30:]:
                print(l)
            print(f"\n  Registros: {self.regs}")
            print(f"  Flags: Z={int(self.Z)} N={int(self.N)} C={int(self.C)}")
            d = self.ram.dump()
            if d:
                print(f"  RAM: {d}")
            print(f"  Ciclos: {self.ciclos}")

        return {
            'regs':   dict(self.regs),
            'Z':      self.Z,
            'N':      self.N,
            'C':      self.C,
            'salida': self.salida,
            'ciclos': self.ciclos,
        }
