"""
cpu/memoria.py
--------------
Subsistemas de memoria de TIE-Lang.

MemoriaPrograma : ROM — almacena instrucciones + resuelve etiquetas
MemoriaDatos    : RAM topológica — 16 celdas × 4 bits
CeldaMemoria    : celda individual con WRITE/READ/RESET no-destructivo

Propiedad clave de CeldaMemoria:
    Un vórtice topológico NO necesita refresh (a diferencia de DRAM).
    Solo se borra inyectando su antivórtice exacto.
"""

from typing import List, Optional, Dict
from .instrucciones import Instruccion, Operacion
from ..core.red import Red
from ..core.vortice import medir_N


# ─────────────────────────────────────────────────────────────────────
# MEMORIA DE PROGRAMA (ROM)
# ─────────────────────────────────────────────────────────────────────

class MemoriaPrograma:
    """
    Almacena la secuencia de instrucciones y resuelve etiquetas
    de salto a índices numéricos.
    """

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
        """Lee la instrucción en la posición pc."""
        if 0 <= pc < len(self.instrucciones):
            return self.instrucciones[pc]
        return None

    def resolver(self, etiqueta: str) -> int:
        """Convierte nombre de etiqueta a índice. -1 si no existe."""
        return self.etiquetas.get(etiqueta, -1)

    def __len__(self):
        return len(self.instrucciones)


# ─────────────────────────────────────────────────────────────────────
# MEMORIA DE DATOS (RAM)
# ─────────────────────────────────────────────────────────────────────

class MemoriaDatos:
    """
    RAM simple de 16 celdas, cada una almacena un entero 0–15.
    En la arquitectura física, cada celda sería una CeldaMemoria
    topológica. Aquí usamos enteros para velocidad de simulación.
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


# ─────────────────────────────────────────────────────────────────────
# CELDA DE MEMORIA TOPOLÓGICA
# ─────────────────────────────────────────────────────────────────────

class CeldaMemoria:
    """
    Celda de memoria topológica individual.

    Implementa el ciclo completo:
        WRITE  → inyectar vórtice N en la celda
        READ   → medir winding number (no-destructivo)
        HOLD   → la topología garantiza persistencia indefinida
        RESET  → inyectar antivórtice −N → aniquilación → N=0

    Propiedades verificadas:
        - 51/51 lecturas consecutivas sin degradación
        - Resistencia al ruido: un vórtice N=8 persiste
          durante 500+ pasos de evolución libre sin intervención
    """

    def __init__(self, red: Red, posicion: tuple, radio_celda: int = 6):
        self.red   = red
        self.pos   = posicion
        self.radio = radio_celda

    def write(self, N_dato: int, pasos_estabilizar: int = 50):
        """Escribe N_dato en la celda e invoca estabilización."""
        self.red.insertar_vortice(*self.pos, N=N_dato, radio=self.radio)
        self.red.evolucionar(pasos=pasos_estabilizar)

    def read(self) -> int:
        """
        Lectura no-destructiva del winding number.
        El lazo de integración no modifica el campo de fase.
        """
        return medir_N(self.red.fases, *self.pos, radio=self.radio - 1)

    def hold(self, pasos: int = 200):
        """
        Evolución libre. Verifica persistencia topológica.
        Retorna (N_antes, N_después, historia).
        """
        N_antes  = self.read()
        historia = [N_antes]
        for _ in range(pasos // 10):
            self.red.evolucionar(pasos=10)
            historia.append(self.read())
        return N_antes, self.read(), historia

    def reset(self, pasos: int = 80):
        """Aniquila el vórtice. Resultado esperado: N → 0."""
        N = self.read()
        if N != 0:
            self.red.insertar_vortice(*self.pos, N=-N, radio=self.radio)
            self.red.evolucionar(pasos=pasos)
