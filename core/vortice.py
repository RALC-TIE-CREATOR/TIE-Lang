"""
core/vortice.py
---------------
Medición del número de enrollamiento topológico (winding number).

El winding number N es el invariante topológico que no cambia
bajo deformaciones continuas del campo de fase.

    N = (1/2π) ∮ ∇φ · dl

donde el lazo encierra el defecto. Para un vórtice puro, N ∈ ℤ.
Esta cantidad es el "dato" fundamental en TIE-Lang.
"""

import numpy as np
from typing import Tuple


def medir_N(fases: np.ndarray,
            cx: int, cy: int,
            z: int = 0,
            radio: int = 4) -> int:
    """
    Mide el winding number en (cx, cy) integrando sobre
    un lazo cuadrado de radio `radio`.

    La integral discreta suma las diferencias de fase entre
    puntos adyacentes del lazo, normalizadas a (-π, π].
    Esto es el equivalente discreto de ∮ dφ / (2π).

    Parámetros
    ----------
    fases : array (Lx, Ly, Lz)
    cx, cy : centro del lazo
    z : capa z donde medir
    radio : mitad del lado del cuadrado

    Retorna
    -------
    N : int  (número de enrollamiento, típicamente -2..+16 en TIE-Lang)
    """
    Lx, Ly, _ = fases.shape
    total = 0.0
    r = radio

    # Lazo cuadrado en sentido antihorario
    puntos = (
        [(cx - r + i, cy - r) for i in range(2 * r)] +   # borde inferior →
        [(cx + r,     cy - r + i) for i in range(2 * r)] + # borde derecho ↑
        [(cx + r - i, cy + r)     for i in range(2 * r)] + # borde superior ←
        [(cx - r,     cy + r - i) for i in range(2 * r)]   # borde izquierdo ↓
    )

    for k in range(len(puntos)):
        x1, y1 = puntos[k]
        x2, y2 = puntos[(k + 1) % len(puntos)]
        x1 %= Lx; y1 %= Ly
        x2 %= Lx; y2 %= Ly

        diff = fases[x2, y2, z] - fases[x1, y1, z]
        # Normalizar a (-π, π] para contar correctamente
        diff = (diff + np.pi) % (2 * np.pi) - np.pi
        total += diff

    return int(round(total / (2 * np.pi)))


def mapa_vorticidad(fases: np.ndarray, z: int = 1) -> np.ndarray:
    """
    Calcula el mapa de vorticidad local en el plano z.
    Útil para visualización: los defectos aparecen como picos.

    Retorna array 2D de la misma forma que fases[:,:,z].
    """
    f = fases[:, :, z]
    vort = (
        np.roll(f, -1, 0) - np.roll(f, 1, 0) +
        np.roll(f, -1, 1) - np.roll(f, 1, 1)
    )
    return vort


def localizar_defectos(fases: np.ndarray,
                       z: int = 0,
                       radio: int = 4,
                       paso: int = 4) -> list:
    """
    Escanea la red y devuelve una lista de (x, y, N) para
    todos los defectos topológicos con |N| ≥ 1.

    Útil para lectura automática del estado de la red.
    """
    Lx, Ly, _ = fases.shape
    defectos = []

    for cx in range(radio, Lx - radio, paso):
        for cy in range(radio, Ly - radio, paso):
            N = medir_N(fases, cx, cy, z=z, radio=radio)
            if abs(N) >= 1:
                defectos.append((cx, cy, N))

    return defectos
