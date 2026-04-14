from .instrucciones import Instruccion, Operacion
from .memoria import MemoriaPrograma, MemoriaDatos, CeldaMemoria
from .cpu import CPU

def I(op, dest=None, src1=None, src2=None, label=None):
    """Shorthand para crear instrucciones."""
    return Instruccion(op, dest, src1, src2, label)
