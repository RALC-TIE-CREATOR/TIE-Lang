from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .lattice import CubicLattice, Vec3


@dataclass(frozen=True)
class ClosedLoop:
    """
    Lazo cerrado autoevitante sobre una red cubica.

    El lazo se da como una lista de vertices unicos.
    El cierre se interpreta conectando el ultimo vertice con el primero.
    """

    lattice: CubicLattice
    vertices: tuple[Vec3, ...]

    def __post_init__(self):
        if len(self.vertices) < 4:
            raise ValueError("Un lazo cerrado requiere al menos 4 vertices")

        wrapped = tuple(self.lattice.wrap(v) for v in self.vertices)
        if len(set(wrapped)) != len(wrapped):
            raise ValueError("El lazo debe ser autoevitante")

        for idx, actual in enumerate(wrapped):
            siguiente = wrapped[(idx + 1) % len(wrapped)]
            if not self.lattice.are_adjacent(actual, siguiente):
                raise ValueError("Todos los segmentos del lazo deben ser adyacentes")

        object.__setattr__(self, "vertices", wrapped)

    @property
    def length(self) -> int:
        return len(self.vertices)

    @property
    def is_planar_xy(self) -> bool:
        return len({z for _, _, z in self.vertices}) == 1

    @property
    def winding(self) -> int:
        """
        Carga topologica discreta del lazo en el plano XY.

        +1 = orientacion antihoraria
        -1 = orientacion horaria
         0 = no planar o area degenerada
        """
        if not self.is_planar_xy:
            return 0

        puntos = [(x, y) for x, y, _ in self.vertices]
        area2 = 0
        for idx, (x1, y1) in enumerate(puntos):
            x2, y2 = puntos[(idx + 1) % len(puntos)]
            area2 += (x1 * y2) - (x2 * y1)

        if area2 == 0:
            return 0
        return 1 if area2 > 0 else -1

    def translated(self, dx: int = 0, dy: int = 0, dz: int = 0) -> "ClosedLoop":
        return ClosedLoop(
            self.lattice,
            tuple((x + dx, y + dy, z + dz) for x, y, z in self.vertices),
        )

    def reversed(self) -> "ClosedLoop":
        return ClosedLoop(self.lattice, tuple(reversed(self.vertices)))

    @property
    def center(self) -> tuple[float, float, float]:
        n = len(self.vertices)
        sx = sum(x for x, _, _ in self.vertices)
        sy = sum(y for _, y, _ in self.vertices)
        sz = sum(z for _, _, z in self.vertices)
        return (sx / n, sy / n, sz / n)

    @property
    def center_grid(self) -> Vec3:
        cx, cy, cz = self.center
        return self.lattice.wrap((round(cx), round(cy), round(cz)))

    @property
    def bounding_box(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        xs = [x for x, _, _ in self.vertices]
        ys = [y for _, y, _ in self.vertices]
        zs = [z for _, _, z in self.vertices]
        return ((min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs)))

    @property
    def radius_hint(self) -> int:
        (xmin, xmax), (ymin, ymax), _ = self.bounding_box
        span = max(xmax - xmin, ymax - ymin, 1)
        return max(2, span)

    def distance_to(self, other: "ClosedLoop") -> float:
        x1, y1, z1 = self.center
        x2, y2, z2 = other.center
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    def summary(self) -> dict:
        return {
            "length": self.length,
            "winding": self.winding,
            "planar_xy": self.is_planar_xy,
            "center": self.center_grid,
        }


def make_square_loop(
    lattice: CubicLattice,
    origin: Vec3 = (0, 0, 0),
    side: int = 2,
    clockwise: bool = False,
) -> ClosedLoop:
    """
    Crea un lazo cuadrado discreto de lado `side`.

    El lado se mide en pasos de red y produce un perimetro de 4 * side.
    """
    if side < 1:
        raise ValueError("El lado del lazo debe ser positivo")

    ox, oy, oz = origin
    vertices: list[Vec3] = []

    for step in range(side):
        vertices.append((ox + step, oy, oz))
    for step in range(side):
        vertices.append((ox + side, oy + step, oz))
    for step in range(side):
        vertices.append((ox + side - step, oy + side, oz))
    for step in range(side):
        vertices.append((ox, oy + side - step, oz))

    loop = ClosedLoop(lattice, tuple(vertices))
    if clockwise:
        return loop.reversed()
    return loop
