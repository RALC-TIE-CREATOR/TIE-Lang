"""
core/red.py
-----------
Red cúbica de fases con dinámica sine-Gordon amortiguada.
Sustrato físico de toda la computación en TIE-Lang.

Ecuación de movimiento:
    φ̈_i = (1/6) Σ_j sin(φ_j - φ_i) - γ φ̇_i
"""

import numpy as np


class Red:
    """
    Red cúbica 3D de fases.
    Cada nodo almacena φ ∈ [0, 2π).
    Los vórtices topológicos (winding number N ≠ 0)
    son los portadores de información en TIE-Lang.
    """

    def __init__(self, Lx: int, Ly: int, Lz: int,
                 amortiguacion: float = 0.05):
        self.Lx    = Lx
        self.Ly    = Ly
        self.Lz    = Lz
        self.gamma = amortiguacion
        self.fases     = np.zeros((Lx, Ly, Lz))
        self.velocidad = np.zeros((Lx, Ly, Lz))

    def insertar_vortice(self, cx: int, cy: int,
                         N: int = 1, radio: int = 6):
        """
        Inyecta un vórtice de enrollamiento N centrado en (cx, cy).
        Perfil ansatz: φ(r,θ) = N · arctan2(y,x) · tanh(r / (radio/2))
        """
        for i in range(self.Lx):
            for j in range(self.Ly):
                dx, dy = i - cx, j - cy
                r = np.sqrt(dx**2 + dy**2)
                if r < radio * 2:
                    angulo = np.arctan2(dy, dx)
                    perfil = np.tanh(r / (radio / 2))
                    self.fases[i, j, :] += N * angulo * perfil
        self.fases %= (2 * np.pi)

    def paso(self, dt: float = 0.1):
        """Un paso Euler de sine-Gordon amortiguado."""
        f = self.fases
        laplaciano = (
            np.sin(np.roll(f, -1, 0) - f) +
            np.sin(np.roll(f,  1, 0) - f) +
            np.sin(np.roll(f, -1, 1) - f) +
            np.sin(np.roll(f,  1, 1) - f) +
            np.sin(np.roll(f, -1, 2) - f) +
            np.sin(np.roll(f,  1, 2) - f)
        ) / 6.0
        aceleracion    = laplaciano - self.gamma * self.velocidad
        self.velocidad = self.velocidad + dt * aceleracion
        self.fases     = (self.fases + dt * self.velocidad) % (2 * np.pi)

    def evolucionar(self, pasos: int = 10, dt: float = 0.1):
        """Ejecuta N pasos de integración."""
        for _ in range(pasos):
            self.paso(dt)

    def energia(self) -> float:
        """Energía total: E = Σ_enlaces (1 - cos Δφ)"""
        E = 0.0
        for ax in range(3):
            E += float(np.sum(1.0 - np.cos(
                np.roll(self.fases, -1, ax) - self.fases
            )))
        return E

    def energia_local(self, cx: int, cy: int,
                      radio: int = 8) -> float:
        """Energía en región cuadrada alrededor de (cx, cy)."""
        E = 0.0
        for i in range(cx - radio, cx + radio):
            for j in range(cy - radio, cy + radio):
                ii, jj = i % self.Lx, j % self.Ly
                for ax in range(2):
                    ni = (ii + int(ax == 0)) % self.Lx
                    nj = (jj + int(ax == 1)) % self.Ly
                    E += 1.0 - np.cos(
                        self.fases[ii, jj, 1] - self.fases[ni, nj, 1]
                    )
        return E

    def snapshot(self) -> np.ndarray:
        """Copia del estado actual."""
        return self.fases.copy()

    def __repr__(self):
        return (f"Red({self.Lx}×{self.Ly}×{self.Lz}, "
                f"γ={self.gamma}, E={self.energia():.3f})")
