import numpy as np

class Red:
    def __init__(self, Lx, Ly, Lz, amortiguacion=0.05):
        self.Lx, self.Ly, self.Lz = Lx, Ly, Lz
        self.fases     = np.zeros((Lx, Ly, Lz))
        self.velocidad = np.zeros((Lx, Ly, Lz))
        self.gamma     = amortiguacion

    def insertar_vortice(self, cx, cy, N=1, radio=6):
        """Inyecta la huella de fase de un vórtice (N) o antivórtice (-N)."""
        for i in range(self.Lx):
            for j in range(self.Ly):
                dx, dy = i - cx, j - cy
                r = np.sqrt(dx**2 + dy**2)
                if r < radio * 2:
                    angulo = np.arctan2(dy, dx)
                    perfil = np.tanh(r / (radio / 2))
                    # Aplicamos a todas las capas Z para mantener coherencia
                    self.fases[i, j, :] += N * angulo * perfil
        self.fases %= (2 * np.pi)

    def paso(self, dt=0.1):
        """Dinámica Sine-Gordon: Propagación de ondas de fase con disipación."""
        f = self.fases
        # Laplaciano discreto usando rolls para eficiencia
        lap = (
            np.sin(np.roll(f, -1, 0) - f) + np.sin(np.roll(f, 1, 0) - f) +
            np.sin(np.roll(f, -1, 1) - f) + np.sin(np.roll(f, 1, 1) - f) +
            np.sin(np.roll(f, -1, 2) - f) + np.sin(np.roll(f, 1, 2) - f)
        ) / 6.0
        
        self.velocidad += dt * (lap - self.gamma * self.velocidad)
        self.fases      = (self.fases + dt * self.velocidad) % (2 * np.pi)

    def evolucionar(self, pasos=10, dt=0.1):
        for _ in range(pasos):
            self.paso(dt)

    def energia_local(self, cx, cy, radio=8):
        """Mide la densidad de energía en una zona (detección de umbral)."""
        E = 0.0
        for i in range(cx-radio, cx+radio):
            for j in range(cy-radio, cy+radio):
                ii, jj = i % self.Lx, j % self.Ly
                for ax in range(2):
                    d = (self.fases[ii, jj, 1] - 
                         self.fases[(ii + (ax==0)) % self.Lx, 
                                    (jj + (ax==1)) % self.Ly, 1])
                    E += 1 - np.cos(d)
        return E

def medir_N(fases, cx, cy, z=0, radio=4):
    """Cálculo del Winding Number (Carga Topológica)."""
    Lx, Ly, _ = fases.shape
    total = 0.0
    r = radio
    puntos = (
        [(cx-r+i, cy-r) for i in range(2*r)] +
        [(cx+r,   cy-r+i) for i in range(2*r)] +
        [(cx+r-i, cy+r)   for i in range(2*r)] +
        [(cx-r,   cy+r-i) for i in range(2*r)]
    )
    for k in range(len(puntos)):
        x1, y1 = puntos[k]
        x2, y2 = puntos[(k+1) % len(puntos)]
        x1 %= Lx; y1 %= Ly; x2 %= Lx; y2 %= Ly
        diff = fases[x2, y2, z] - fases[x1, y1, z]
        diff = (diff + np.pi) % (2 * np.pi) - np.pi
        total += diff
    return int(round(total / (2 * np.pi)))