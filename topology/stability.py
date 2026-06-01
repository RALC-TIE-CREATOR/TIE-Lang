from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseStabilityReport:
    """
    Resumen minimo de estabilidad despues de evolucionar en el campo de fase.
    """

    value: int
    measured_value: int
    bits: list[int]
    measured_bits: list[int]
    energy_initial: float
    energy_final: float

    @property
    def bit_errors(self) -> int:
        return sum(
            1
            for expected, measured in zip(self.bits, self.measured_bits)
            if expected != measured
        )

    @property
    def energy_delta(self) -> float:
        return self.energy_final - self.energy_initial

    @property
    def stable(self) -> bool:
        return self.value == self.measured_value and self.bit_errors == 0

    def as_dict(self) -> dict:
        return {
            "stable": self.stable,
            "bit_errors": self.bit_errors,
            "energy_delta": self.energy_delta,
            "value": self.value,
            "measured_value": self.measured_value,
            "bits": self.bits,
            "measured_bits": self.measured_bits,
        }
