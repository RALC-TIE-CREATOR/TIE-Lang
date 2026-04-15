"""
cpu/memoria.py
--------------
Subsistemas de memoria de TIE-Lang.

MemoriaPrograma : ROM — instrucciones + resolución de etiquetas
MemoriaDatos    : RAM — 16 celdas × 4 bits
CeldaMemoria    : celda topológica individual (WRITE/READ/RESET)

Propiedad clave:
    Un vórtice topológico NO necesita refresh.
    Solo se borra inyectando su antivórtice exacto.
"""

from typing import List, Optional, Dict
from .instrucciones import Instruccion, Operacion
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.red import Red
from core.vortice import medir_N


class MemoriaPrograma:
    """ROM topológica — almacena instrucciones y resuelve etiquetas."""

    def __init__(self, instrucciones: List[Instruccion]):
        self.instrucciones = instrucciones
        self.etiquetas: Dict[str, int] = {}
        self._resolver_etiquetas()

    def _resolver_etiquetas(self):
        for i, instr in enumerate(self.instrucciones):
            if (instr.label and
                    instr.op not in (Operacion.JMP, Operacion.JZ,
                                     Operacion.JN, Operacion.CALL)):
                self.etiquetas[instr.label] = i

    def fetch(self, pc: int) -> Optional[Instruccion]:
        if 0 <= pc < len(self.instrucciones):
            return self.instrucciones[pc]
        return None

    def resolver(self, etiqueta: str) -> int:
        return self.etiquetas.get(etiqueta, -1)

    def __len__(self):
        return len(self.instrucciones)


class MemoriaDatos:
    """
    RAM de 16 celdas × 4 bits.
    En hardware real cada celda sería una CeldaMemoria topológica.
    """

    def __init__(self, tamanio: int = 16):
        self.datos = [0] * tamanio

    def leer(self, direccion: int) -> int:
        return self.datos[direccion % len(self.datos)]

    def escribir(self, direccion: int, valor: int):
        self.datos[direccion % len(self.datos)] = valor & 0xF

    def dump(self) -> Dict[int, int]:
        return {i: v for i, v in enumerate(self.datos) if v != 0}

    def __repr__(self):
        d = self.dump()
        return f"RAM({d})" if d else "RAM(vacía)"


class CeldaMemoria:
    """
    Celda de memoria topológica individual.

    WRITE  → inyectar vórtice N
    READ   → medir winding number (no-destructivo)
    HOLD   → persistencia garantizada por topología
    RESET  → inyectar antivórtice → aniquilación → N=0

    Verificado:
        51/51 lecturas consecutivas sin degradación.
        500 pasos de evolución libre sin pérdida de dato.
    """

    def __init__(self, red: Red, posicion: tuple,
                 radio_celda: int = 6):
        self.red   = red
        self.pos   = posicion
        self.radio = radio_celda

    def write(self, N_dato: int, pasos: int = 50):
        self.red.insertar_vortice(*self.pos, N=N_dato,
                                  radio=self.radio)
        self.red.evolucionar(pasos=pasos)

    def read(self) -> int:
        """Lectura no-destructiva del winding number."""
        return medir_N(self.red.fases, *self.pos,
                       radio=self.radio - 1)

    def hold(self, pasos: int = 200):
        """
        Evolución libre. Verifica persistencia.
        Retorna (N_antes, N_después, historia).
        """
        N_antes  = self.read()
        historia = [N_antes]
        for _ in range(pasos // 10):
            self.red.evolucionar(pasos=10)
            historia.append(self.read())
        return N_antes, self.read(), historia

    def reset(self, pasos: int = 80):
        """Aniquila el vórtice. Resultado: N → 0."""
        N = self.read()
        if N != 0:
            self.red.insertar_vortice(*self.pos, N=-N,
                                      radio=self.radio)
            self.red.evolucionar(pasos=pasos)
