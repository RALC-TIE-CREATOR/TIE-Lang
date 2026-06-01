from __future__ import annotations

from dataclasses import dataclass


Vec3 = tuple[int, int, int]


@dataclass(frozen=True)
class CubicLattice:
    """
    Red cubica discreta con condiciones periodicas.

    Esta es la malla base del preview topologico de v0.3.0.
    La informacion no se modela aqui como bits abstractos,
    sino como recorridos cerrados sobre el sustrato.
    """

    size_x: int
    size_y: int
    size_z: int = 1

    def __post_init__(self):
        if self.size_x < 2 or self.size_y < 2 or self.size_z < 1:
            raise ValueError("La red cubica debe tener dimensiones validas")

    def wrap(self, punto: Vec3) -> Vec3:
        x, y, z = punto
        return (x % self.size_x, y % self.size_y, z % self.size_z)

    def neighbors(self, punto: Vec3) -> list[Vec3]:
        x, y, z = self.wrap(punto)
        return [
            ((x + 1) % self.size_x, y, z),
            ((x - 1) % self.size_x, y, z),
            (x, (y + 1) % self.size_y, z),
            (x, (y - 1) % self.size_y, z),
            (x, y, (z + 1) % self.size_z),
            (x, y, (z - 1) % self.size_z),
        ]

    def are_adjacent(self, a: Vec3, b: Vec3) -> bool:
        return self.wrap(b) in self.neighbors(a)
