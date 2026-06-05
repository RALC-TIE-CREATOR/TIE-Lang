from __future__ import annotations

from core.red import Red
from core.vortice import localizar_defectos, medir_N

from .loops import ClosedLoop
from .stability import PhaseStabilityReport


class PhaseFieldBridge:
    """
    Puente entre el preview discreto de lazos y la dinamica de fase en `core/`.
    """

    def __init__(self, damping: float = 0.04):
        self.damping = damping

    def _build_red(self, loop: ClosedLoop, margin: int = 8) -> Red:
        lattice = loop.lattice
        size_x = max(lattice.size_x + margin, 20)
        size_y = max(lattice.size_y + margin, 20)
        size_z = max(lattice.size_z, 1)
        return Red(size_x, size_y, size_z, amortiguacion=self.damping)

    def _build_red_for_loops(self, loops: list[ClosedLoop], margin: int = 8) -> Red:
        size_x = max(max(loop.lattice.size_x for loop in loops) + margin, 20)
        size_y = max(max(loop.lattice.size_y for loop in loops) + margin, 20)
        size_z = max(max(loop.lattice.size_z for loop in loops), 1)
        return Red(size_x, size_y, size_z, amortiguacion=self.damping)

    def _phase_center(self, loop: ClosedLoop, red: Red) -> tuple[int, int, int]:
        cx, cy, _ = loop.center_grid
        center_x = min(max(cx + 4, 4), red.Lx - 5)
        center_y = min(max(cy + 4, 4), red.Ly - 5)
        radius = max(3, loop.radius_hint)
        return center_x, center_y, radius

    def project_loop(
        self,
        loop: ClosedLoop,
        pasos: int = 25,
        dt: float = 0.1,
    ) -> dict:
        red = self._build_red(loop)
        center_x, center_y, radius = self._phase_center(loop, red)

        red.insertar_vortice(center_x, center_y, N=loop.winding, radio=radius)
        energia_inicial = red.energia()
        red.evolucionar(pasos=pasos, dt=dt)
        energia_final = red.energia()
        measured = medir_N(red.fases, center_x, center_y, radio=radius)

        return {
            "center": (center_x, center_y),
            "input_winding": loop.winding,
            "measured_winding": measured,
            "energy_initial": energia_inicial,
            "energy_final": energia_final,
            "defects": localizar_defectos(red.fases, radio=radius + 1, paso=max(2, radius)),
            "red": red,
        }

    def project_register(
        self,
        register,
        pasos: int = 25,
        dt: float = 0.1,
    ) -> dict:
        loops = [plane.loop for plane in register.planes]
        red = self._build_red_for_loops(loops)
        centers = []

        for loop in loops:
            center_x, center_y, radius = self._phase_center(loop, red)
            centers.append((center_x, center_y, radius))
            red.insertar_vortice(center_x, center_y, N=loop.winding, radio=radius)

        energy_initial = red.energia()
        red.evolucionar(pasos=pasos, dt=dt)
        energy_final = red.energia()

        plane_results = {}
        measured_bits = []
        for idx, (loop, (center_x, center_y, radius)) in enumerate(zip(loops, centers)):
            raw_measured = medir_N(red.fases, center_x, center_y, radio=radius)
            measured = 1 if raw_measured > 0 else -1
            measured_bits.append(1 if measured > 0 else 0)
            plane_results[f"b{idx}"] = {
                "center": (center_x, center_y),
                "input_winding": loop.winding,
                "measured_winding": measured,
                "raw_measured_winding": raw_measured,
                "radius": radius,
            }

        measured_value = 0
        for idx, bit in enumerate(measured_bits):
            measured_value |= (bit & 1) << idx

        return {
            "value": register.read_value(),
            "bits": register.read_bits(),
            "measured_bits": measured_bits,
            "measured_value": measured_value,
            "layout": register.layout,
            "energy_initial": energy_initial,
            "energy_final": energy_final,
            "stability": PhaseStabilityReport(
                value=register.read_value(),
                measured_value=measured_value,
                bits=register.read_bits(),
                measured_bits=measured_bits,
                energy_initial=energy_initial,
                energy_final=energy_final,
            ).as_dict(),
            "defects": localizar_defectos(red.fases, radio=4, paso=4),
            "planes": plane_results,
            "red": red,
        }

    def project_runtime(
        self,
        runtime,
        pasos: int = 25,
        dt: float = 0.1,
    ) -> dict[str, dict]:
        return {
            name: self.project_loop(cell.loop, pasos=pasos, dt=dt)
            for name, cell in runtime.cells.items()
        }
