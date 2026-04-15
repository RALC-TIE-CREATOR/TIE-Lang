"""
core/vortice.py
---------------
Medición del número de enrollamiento topológico (winding number).

    N = (1/2π) ∮ ∇φ · dl

N es el invariante topológico que no cambia bajo
deformaciones continuas del campo de fase.
Es el "dato" fundamental en TIE-Lang.
"""

import numpy as np


def medir_N(fases: np.ndarray,
            cx: int, cy: int,
            z: int = 0,
            radio: int = 4) -> int:
    """
    Mide el winding number en (cx, cy) integrando sobre
    un lazo cuadrado de radio `radio`.

    La integral discreta suma diferencias de fase entre
    puntos adyacentes del lazo, normalizadas a (-π, π].
    Equivalente discreto de ∮ dφ / (2π).
    """
    Lx, Ly, _ = fases.shape
    total = 0.0
    r = radio

    puntos = (
        [(cx - r + i, cy - r) for i in range(2 * r)] +
        [(cx + r,     cy - r + i) for i in range(2 * r)] +
        [(cx + r - i, cy + r)     for i in range(2 * r)] +
        [(cx - r,     cy + r - i) for i in range(2 * r)]
    )

    for k in range(len(puntos)):
        x1, y1 = puntos[k]
        x2, y2 = puntos[(k + 1) % len(puntos)]
        x1 %= Lx; y1 %= Ly
        x2 %= Lx; y2 %= Ly

        diff = fases[x2, y2, z] - fases[x1, y1, z]
        diff = (diff + np.pi) % (2 * np.pi) - np.pi
        total += diff

    return int(round(total / (2 * np.pi)))


def mapa_vorticidad(fases: np.ndarray, z: int = 1) -> np.ndarray:
    """
    Mapa de vorticidad local en el plano z.
    Los defectos aparecen como picos. Útil para visualización.
    """
    f = fases[:, :, z]
    return (
        np.roll(f, -1, 0) - np.roll(f, 1, 0) +
        np.roll(f, -1, 1) - np.roll(f, 1, 1)
    )


def localizar_defectos(fases: np.ndarray,
                       z: int = 0,
                       radio: int = 4,
                       paso: int = 4) -> list:
    """
    Escanea la red y devuelve lista de (x, y, N)
    para todos los defectos con |N| ≥ 1.
    """
    Lx, Ly, _ = fases.shape
    defectos = []
    for cx in range(radio, Lx - radio, paso):
        for cy in range(radio, Ly - radio, paso):
            N = medir_N(fases, cx, cy, z=z, radio=radio)
            if abs(N) >= 1:
                defectos.append((cx, cy, N))
    return defectos
