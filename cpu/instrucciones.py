"""
cpu/instrucciones.py
--------------------
Definición del conjunto de instrucciones (ISA) de TIE-Lang.

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
    # Transferencia de datos
    LOAD   = auto()   # carga inmediata:     dest = inmediato
    LOAD_M = auto()   # carga desde RAM:     dest = RAM[src1]
    STORE  = auto()   # guarda en RAM:       RAM[src2] = src1
    MOVE   = auto()   # copia de registro:   dest = src1

    # Aritmética
    SUMA   = auto()   # dest = src1 + src2
    RESTA  = auto()   # dest = src1 - src2

    # Lógica
    AND    = auto()   # dest = src1 & src2
    OR     = auto()   # dest = src1 | src2
    NOT    = auto()   # dest = ~src1
    XOR    = auto()   # dest = src1 ^ src2

    # Comparación (actualiza flags Z, N)
    CMP    = auto()   # compara src1 vs src2, no escribe dest

    # Saltos
    JMP    = auto()   # salto incondicional: PC = etiqueta
    JZ     = auto()   # salto si Z=True:     PC = etiqueta
    JN     = auto()   # salto si N=True:     PC = etiqueta

    # Subrutinas
    CALL   = auto()   # guarda PC+1, salta a función
    RET    = auto()   # retorna: PC = tope de pila

    # Control
    HALT   = auto()   # detiene la CPU
    PRINT  = auto()   # salida (debug/display)


@dataclass
class Instruccion:
    """
    Una instrucción del ISA TIE-Lang.

    Campos:
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
