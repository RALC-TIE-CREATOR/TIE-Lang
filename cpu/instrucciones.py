"""
cpu/instrucciones.py
--------------------
Conjunto de instrucciones (ISA) de TIE-Lang.

Formato: OPCODE dest src1 src2/inmediato

Ejemplos:
    LOAD  R0  7         →  R0 = 7
    SUMA  R2  R0  R1    →  R2 = R0 + R1
    JZ    fin           →  if Z: PC = fin
    STORE R2  @3        →  RAM[3] = R2
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class Operacion(Enum):
    # Transferencia
    LOAD   = auto()   # dest = inmediato
    LOAD_M = auto()   # dest = RAM[src1]
    STORE  = auto()   # RAM[src2] = src1
    MOVE   = auto()   # dest = src1

    # Aritmética
    SUMA   = auto()   # dest = src1 + src2
    RESTA  = auto()   # dest = src1 - src2

    # Lógica
    AND    = auto()   # dest = src1 & src2
    OR     = auto()   # dest = src1 | src2
    NOT    = auto()   # dest = ~src1
    XOR    = auto()   # dest = src1 ^ src2

    # Comparación
    CMP    = auto()   # actualiza flags Z, N

    # Saltos
    JMP    = auto()   # PC = etiqueta
    JZ     = auto()   # if Z: PC = etiqueta
    JN     = auto()   # if N: PC = etiqueta

    # Subrutinas
    CALL   = auto()   # push PC+1, PC = función
    RET    = auto()   # PC = pop

    # Control
    HALT   = auto()
    PRINT  = auto()


@dataclass
class Instruccion:
    """
    Una instrucción del ISA TIE-Lang.

    op    : operación (Operacion enum)
    dest  : registro destino ('R0'–'R3') o None
    src1  : primer operando: registro, inmediato o etiqueta
    src2  : segundo operando o dirección RAM
    label : etiqueta de esta instrucción (para saltos)
    """
    op:    Operacion
    dest:  Optional[str] = None
    src1:  Optional[str] = None
    src2:  Optional[str] = None
    label: Optional[str] = None

    def __repr__(self):
        partes = [self.op.name]
        for p in [self.dest, self.src1, self.src2]:
            if p is not None:
                partes.append(str(p))
        return " ".join(partes)
