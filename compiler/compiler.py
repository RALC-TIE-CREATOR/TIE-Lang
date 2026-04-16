"""
compiler/compiler.py
--------------------
Generador de código: AST → instrucciones CPU TIE-Lang.

Estrategia:
    Variables  → RAM (dirección fija por nombre)
    Expresiones→ R0/R1 temporales, resultado en R0
    Funciones  → R3 valor de retorno
    Etiquetas  → generadas automáticamente (L1, L2, ...)

compile_and_run() es el punto de entrada principal.
"""

from typing import List, Dict
from .lexer import Lexer
from .parser import (
    Parser, NodoNum, NodoID, NodoBinOp, NodoUnOp,
    NodoAsignar, NodoIf, NodoWhile, NodoDef,
    NodoLlamar, NodoReturn, NodoPrint
)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cpu.instrucciones import Instruccion, Operacion
from cpu.cpu import CPU


class Compilador:
    """Transforma el AST en instrucciones para la CPU TIE-Lang."""

    def __init__(self):
        self.codigo:     List[Instruccion] = []
        self.variables:  Dict[str, int]    = {}
        self.funciones:  Dict[str, object] = {}
        self.next_addr:  int = 0
        self.next_label: int = 0

    def _nueva_etiqueta(self, prefijo='L') -> str:
        self.next_label += 1
        return f"{prefijo}{self.next_label}"

    def _addr(self, nombre: str) -> int:
        if nombre not in self.variables:
            self.variables[nombre] = self.next_addr
            self.next_addr += 1
        return self.variables[nombre]

    def _emit(self, op, dest=None, src1=None,
              src2=None, label=None):
        self.codigo.append(
            Instruccion(op, dest, src1, src2, label))

    # ── Compilar expresión ───────────────────────────────────────────

    def compilar_expr(self, nodo, reg='R0') -> str:

        if isinstance(nodo, NodoNum):
            self._emit(Operacion.LOAD, reg, str(nodo.valor & 0xF))
            return reg

        if isinstance(nodo, NodoID):
            self._emit(Operacion.LOAD_M, reg,
                       str(self._addr(nodo.nombre)))
            return reg

        if isinstance(nodo, NodoUnOp):
            self.compilar_expr(nodo.operando, reg)
            self._emit(Operacion.NOT, reg, reg)
            return reg

        if isinstance(nodo, NodoBinOp):
            self.compilar_expr(nodo.izq, 'R0')
            self.compilar_expr(nodo.der, 'R1')

            op_map = {
                '+': Operacion.SUMA,
                '-': Operacion.RESTA,
                '&': Operacion.AND,
                '|': Operacion.OR,
                '^': Operacion.XOR,
            }

            if nodo.op in op_map:
                self._emit(op_map[nodo.op], reg, 'R0', 'R1')
                return reg

            if nodo.op in ('==', '!=', '<', '>', '<=', '>='):
                self._emit(Operacion.CMP, None, 'R0', 'R1')
                etq_si  = self._nueva_etiqueta('si')
                etq_no  = self._nueva_etiqueta('no')
                etq_fin = self._nueva_etiqueta('fin')

                if nodo.op == '==':
                    self._emit(Operacion.JZ, None, etq_si)

                elif nodo.op == '!=':
                    self._emit(Operacion.JZ, None, etq_no)
                    self._emit(Operacion.JMP, None, etq_si)

                elif nodo.op == '<':
                    self._emit(Operacion.JN, None, etq_si)

                elif nodo.op == '>':
                    self._emit(Operacion.JZ, None, etq_no)
                    self._emit(Operacion.JN, None, etq_no)
                    self._emit(Operacion.JMP, None, etq_si)

                elif nodo.op == '<=':
                    self._emit(Operacion.JZ, None, etq_si)
                    self._emit(Operacion.JN, None, etq_si)

                elif nodo.op == '>=':
                    self._emit(Operacion.JN, None, etq_no)
                    self._emit(Operacion.JMP, None, etq_si)

                self._emit(Operacion.LOAD, reg, '0', label=etq_no)
                self._emit(Operacion.JMP, None, etq_fin)
                self._emit(Operacion.LOAD, reg, '1', label=etq_si)
                self._emit(Operacion.JMP, None, etq_fin)
                self._emit(Operacion.LOAD, reg, reg, label=etq_fin)
                return reg

        if isinstance(nodo, NodoLlamar):
            return self.compilar_llamada(nodo, reg)

        return reg

    # ── Compilar sentencias ──────────────────────────────────────────

    def compilar_stmt(self, nodo):

        if isinstance(nodo, NodoAsignar):
            self.compilar_expr(nodo.expr, 'R0')
            self._emit(Operacion.STORE, None, 'R0',
                       str(self._addr(nodo.nombre)))

        elif isinstance(nodo, NodoPrint):
            self.compilar_expr(nodo.expr, 'R0')
            self._emit(Operacion.PRINT, None, 'R0')

        elif isinstance(nodo, NodoIf):
            self.compilar_expr(nodo.condicion, 'R0')
            self._emit(Operacion.CMP, None, 'R0', '0')
            etq_sino = self._nueva_etiqueta('sino')
            etq_fin  = self._nueva_etiqueta('finif')
            self._emit(Operacion.JZ, None, etq_sino)
            for s in nodo.cuerpo:
                self.compilar_stmt(s)
            self._emit(Operacion.JMP, None, etq_fin)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_sino))
            for s in nodo.sino:
                self.compilar_stmt(s)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_fin))

        elif isinstance(nodo, NodoWhile):
            etq_inicio = self._nueva_etiqueta('loop')
            etq_fin    = self._nueva_etiqueta('endloop')
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_inicio))
            self.compilar_expr(nodo.condicion, 'R0')
            self._emit(Operacion.CMP, None, 'R0', '0')
            self._emit(Operacion.JZ,  None, etq_fin)
            for s in nodo.cuerpo:
                self.compilar_stmt(s)
            self._emit(Operacion.JMP, None, etq_inicio)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_fin))

        elif isinstance(nodo, NodoDef):
            self.funciones[nodo.nombre] = nodo
            etq_saltar = self._nueva_etiqueta('skipfn')
            self._emit(Operacion.JMP, None, etq_saltar)
            primera = True
            regs_args = ['R0', 'R1', 'R2', 'R3']
            for i, param in enumerate(nodo.params[:4]):
                prev_len = len(self.codigo)
                self._emit(Operacion.STORE, None, regs_args[i],
                           str(self._addr(param)))
                if primera:
                    self.codigo[prev_len].label = nodo.nombre
                    primera = False
            for s in nodo.cuerpo:
                prev_len = len(self.codigo)
                if isinstance(s, NodoReturn):
                    self.compilar_expr(s.expr, 'R3')
                    if primera:
                        self.codigo[prev_len].label = nodo.nombre
                        primera = False
                    self._emit(Operacion.RET)
                else:
                    self.compilar_stmt(s)
                    if primera and len(self.codigo) > prev_len:
                        self.codigo[prev_len].label = nodo.nombre
                        primera = False
            self._emit(Operacion.RET)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_saltar))

        elif isinstance(nodo, NodoReturn):
            self.compilar_expr(nodo.expr, 'R3')
            self._emit(Operacion.RET)

        elif isinstance(nodo, NodoLlamar):
            self.compilar_llamada(nodo, 'R3')

    def compilar_llamada(self, nodo: NodoLlamar,
                          reg: str) -> str:
        regs_args = ['R0', 'R1', 'R2', 'R3']
        for i, arg in enumerate(nodo.args[:4]):
            self.compilar_expr(arg, regs_args[i])
        self._emit(Operacion.CALL, None, nodo.nombre)
        if reg != 'R3':
            self._emit(Operacion.MOVE, reg, 'R3')
        return reg

    def compilar(self, ast: list) -> List[Instruccion]:
        for nodo in ast:
            self.compilar_stmt(nodo)
        self._emit(Operacion.HALT)
        return self.codigo

    def mostrar_codigo(self):
        print("  CÓDIGO ENSAMBLADOR:")
        for i, ins in enumerate(self.codigo):
            etq = f"[{ins.label}]" if ins.label else "       "
            print(f"    {i:3d}: {etq:12s} {ins}")


# ── Interfaz principal ───────────────────────────────────────────────

def compile_and_run(fuente: str,
                    titulo: str = "Programa TIE-Lang",
                    verbose_asm: bool = True) -> dict:
    """
    Compila y ejecuta código TIE-Lang.

    Pipeline:
        fuente → Lexer → tokens → Parser → AST
               → Compilador → instrucciones → CPU

    Retorna dict con 'regs', 'Z', 'N', 'C', 'salida', 'ciclos'
    """
    print(f"\n{'═'*55}")
    print(f"  {titulo}")
    print(f"{'═'*55}")
    print("  CÓDIGO FUENTE:")
    for i, l in enumerate(fuente.strip().splitlines(), 1):
        print(f"    {i:2d}: {l}")

    lexer      = Lexer(fuente)
    parser     = Parser(lexer.tokens)
    ast        = parser.parse()
    compilador = Compilador()
    codigo     = compilador.compilar(ast)

    if verbose_asm:
        print()
        compilador.mostrar_codigo()

    print("\n  EJECUCIÓN:")
    cpu       = CPU()
    resultado = cpu.run(codigo, verbose=False)

    print(f"\n  Registros: {resultado['regs']}")
    ram = cpu.ram.dump()
    if ram:
        print(f"  RAM: {ram}")
    print(f"  Salida:  {resultado['salida']}")
    print(f"  Ciclos:  {resultado['ciclos']}")

    return resultado
