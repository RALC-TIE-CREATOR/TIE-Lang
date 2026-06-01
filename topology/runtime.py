from __future__ import annotations

from dataclasses import dataclass

from .bridge import PhaseFieldBridge
from .interactions import apply_local_interaction
from .lattice import CubicLattice
from .loops import ClosedLoop, make_square_loop


@dataclass
class TopologicalMemoryCell:
    """
    Celda minima de memoria topologica.

    `bit = 1` se representa como lazo con winding +1.
    `bit = 0` se representa como lazo con winding -1.
    """

    name: str
    loop: ClosedLoop

    def read_bit(self) -> int:
        return 1 if self.loop.winding > 0 else 0

    def read_charge(self) -> int:
        return self.loop.winding

    def translate(self, dx: int = 0, dy: int = 0, dz: int = 0):
        self.loop = self.loop.translated(dx=dx, dy=dy, dz=dz)

    def flip(self):
        self.loop = self.loop.reversed()


@dataclass
class TopologicalRegister:
    """
    Registro topologico minimo de 4 planos.

    Cada plano almacena un bit como lazo orientado independiente.
    El valor total se interpreta en little-endian:
    plano 0 = bit menos significativo.
    """

    name: str
    planes: tuple[TopologicalMemoryCell, ...]
    layout: str = "compact"

    def read_bits(self) -> list[int]:
        return [plane.read_bit() for plane in self.planes]

    def read_charges(self) -> list[int]:
        return [plane.read_charge() for plane in self.planes]

    def read_value(self) -> int:
        value = 0
        for idx, bit in enumerate(self.read_bits()):
            value |= (bit & 1) << idx
        return value

    def translate(self, dx: int = 0, dy: int = 0, dz: int = 0):
        for plane in self.planes:
            plane.translate(dx=dx, dy=dy, dz=dz)

    def summary(self) -> dict:
        bits = self.read_bits()
        charges = self.read_charges()
        summary = {
            "value": self.read_value(),
            "bits": bits,
            "charges": charges,
            "planes": len(self.planes),
            "layout": self.layout,
            "centers": [plane.loop.center_grid for plane in self.planes],
        }
        if summary["value"] in (0, 1):
            summary.update(
                {
                    "bit": summary["value"],
                    "charge": charges[0],
                    **self.planes[0].loop.summary(),
                }
            )
        return summary


class TopologicalRuntimePreview:
    """
    Primer runtime topologico discreto para TIE-Lang v0.3.0.

    Esta capa no reemplaza aun a la CPU binaria estable.
    Sirve como backend experimental donde el estado se almacena
    como lazos sobre una red cubica y no como bits RAM abstractos.
    """

    def __init__(self, lattice: CubicLattice | None = None):
        self.lattice = lattice or CubicLattice(24, 24, 1)
        self.cells: dict[str, TopologicalMemoryCell] = {}
        self.registers: dict[str, TopologicalRegister] = {}

    def _bundle_origins(
        self,
        origin: tuple[int, int, int],
        layout: str = "compact",
    ) -> list[tuple[int, int, int]]:
        ox, oy, oz = origin
        if layout == "stable":
            return [
                (ox, oy, oz),
                (ox + 8, oy, oz),
                (ox, oy + 8, oz),
                (ox + 8, oy + 8, oz),
            ]
        if layout != "compact":
            raise ValueError(f"Layout topologico desconocido: {layout}")
        return [
            (ox, oy, oz),
            (ox + 4, oy, oz),
            (ox, oy + 4, oz),
            (ox + 4, oy + 4, oz),
        ]

    def write_bit(
        self,
        name: str,
        value: int,
        origin: tuple[int, int, int] = (1, 1, 0),
        side: int = 2,
    ) -> TopologicalMemoryCell:
        loop = make_square_loop(
            self.lattice,
            origin=origin,
            side=side,
            clockwise=(int(value) == 0),
        )
        cell = TopologicalMemoryCell(name, loop)
        self.cells[name] = cell
        return cell

    def write_value(
        self,
        name: str,
        value: int,
        origin: tuple[int, int, int] = (1, 1, 0),
        side: int = 2,
        layout: str = "compact",
    ) -> TopologicalRegister:
        if not 0 <= value <= 15:
            raise ValueError("El registro topologico minimo solo acepta valores 0..15")

        bits = [(value >> idx) & 1 for idx in range(4)]
        planes = []
        for idx, (bit, plane_origin) in enumerate(zip(bits, self._bundle_origins(origin, layout))):
            loop = make_square_loop(
                self.lattice,
                origin=plane_origin,
                side=side,
                clockwise=(bit == 0),
            )
            planes.append(TopologicalMemoryCell(f"{name}__b{idx}", loop))

        register = TopologicalRegister(name, tuple(planes), layout=layout)
        self.registers[name] = register
        return register

    def read_value(self, name: str) -> int:
        if name in self.registers:
            return self.registers[name].read_value()
        return self.read_bit(name)

    def read_bits(self, name: str) -> list[int]:
        if name in self.registers:
            return self.registers[name].read_bits()
        bit = self.read_bit(name)
        return [bit, 0, 0, 0]

    def read_bit(self, name: str) -> int:
        if name in self.registers:
            return self.registers[name].read_bits()[0]
        return self.cells[name].read_bit()

    def read_charge(self, name: str) -> int:
        if name in self.registers:
            return self.registers[name].read_charges()[0]
        return self.cells[name].read_charge()

    def translate(self, name: str, dx: int = 0, dy: int = 0, dz: int = 0):
        if name in self.registers:
            self.registers[name].translate(dx=dx, dy=dy, dz=dz)
            return
        self.cells[name].translate(dx=dx, dy=dy, dz=dz)

    def topological_not(self, source: str, target: str | None = None) -> TopologicalMemoryCell:
        if source in self.registers:
            target_name = target or source
            source_bits = self.registers[source].read_bits()
            register = self.write_value(
                target_name,
                0 if any(source_bits) else 1,
                origin=self.registers[source].planes[0].loop.center_grid,
            )
            return register.planes[0]
        cell = self.cells[source]
        target_name = target or source
        new_cell = TopologicalMemoryCell(target_name, cell.loop.reversed())
        self.cells[target_name] = new_cell
        return new_cell

    def interact(self, left: str, right: str, near_threshold: float = 3.0) -> dict:
        left_cell = self.cells[left]
        right_cell = self.cells[right]
        result = apply_local_interaction(
            left_cell.loop,
            right_cell.loop,
            near_threshold=near_threshold,
        )

        if result["action"] == "annihilate":
            del self.cells[left]
            del self.cells[right]
            return result

        if result["action"] == "repel":
            self.cells[left] = TopologicalMemoryCell(left, result["loops"][0])
            self.cells[right] = TopologicalMemoryCell(right, result["loops"][1])
            return result

        return result

    def phase_projection(
        self,
        pasos: int = 25,
        dt: float = 0.1,
        bridge: PhaseFieldBridge | None = None,
    ) -> dict[str, dict]:
        bridge = bridge or PhaseFieldBridge()
        result = {
            name: bridge.project_loop(cell.loop, pasos=pasos, dt=dt)
            for name, cell in self.cells.items()
        }
        for name, register in self.registers.items():
            projection = bridge.project_register(register, pasos=pasos, dt=dt)
            projection["input_winding"] = projection["planes"]["b0"]["input_winding"]
            projection["measured_winding"] = projection["planes"]["b0"]["measured_winding"]
            result[name] = projection
        return result

    def snapshot(self) -> dict[str, dict]:
        snapshot = {
            name: {
                "bit": cell.read_bit(),
                "charge": cell.read_charge(),
                **cell.loop.summary(),
            }
            for name, cell in self.cells.items()
        }
        snapshot.update(
            {
                name: register.summary()
                for name, register in self.registers.items()
            }
        )
        return snapshot
