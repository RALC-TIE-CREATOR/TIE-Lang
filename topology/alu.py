from __future__ import annotations

from dataclasses import dataclass

from .interactions import apply_local_interaction
from .lattice import CubicLattice
from .loops import make_square_loop


@dataclass(frozen=True)
class CarryTransition:
    """
    Transicion local de carry entre planos vecinos de un registro topologico.
    """

    plane: int
    target_plane: int | None
    left_bit: int
    right_bit: int
    carry_in: int
    result_bit: int
    generate: int
    propagate: int
    carry_out: int
    interaction: str
    charge_before: int
    charge_after: int


@dataclass(frozen=True)
class TopologicalALUResult:
    bits: list[int]
    transitions: list[CarryTransition]

    @property
    def value(self) -> int:
        total = 0
        for idx, bit in enumerate(self.bits[:4]):
            total |= (bit & 1) << idx
        return total & 0xF


class TopologicalALU:
    """
    ALU discreta sobre planos topologicos.

    El valor se sigue leyendo como 4 bits, pero la suma ya registra el carry como
    una secuencia de interacciones locales entre planos.
    """

    def __init__(self, lattice: CubicLattice | None = None):
        self.lattice = lattice or CubicLattice(24, 24, 1)

    def bits_from_value(self, value: int) -> list[int]:
        if not 0 <= value <= 15:
            raise ValueError("La ALU topologica solo acepta valores 0..15")
        return [(value >> idx) & 1 for idx in range(4)]

    def value_from_bits(self, bits: list[int]) -> int:
        total = 0
        for idx, bit in enumerate(bits[:4]):
            total |= (bit & 1) << idx
        return total & 0xF

    def _local_interaction(
        self,
        plane: int,
        left_bit: int,
        right_bit: int,
        carry_in: int,
    ) -> dict:
        xor_lr = left_bit ^ right_bit
        generate = left_bit & right_bit
        propagate = xor_lr & carry_in
        y = 1 + plane * 4

        if generate:
            left = make_square_loop(self.lattice, origin=(1, y, 0), side=2)
            right = make_square_loop(self.lattice, origin=(4, y, 0), side=2)
            return apply_local_interaction(left, right, near_threshold=4.0)

        if propagate:
            signal = make_square_loop(self.lattice, origin=(1, y, 0), side=2)
            carry = make_square_loop(self.lattice, origin=(4, y, 0), side=2)
            return apply_local_interaction(signal, carry, near_threshold=4.0)

        if carry_in and not xor_lr:
            signal = make_square_loop(
                self.lattice,
                origin=(1, y, 0),
                side=2,
                clockwise=True,
            )
            carry = make_square_loop(self.lattice, origin=(4, y, 0), side=2)
            return apply_local_interaction(signal, carry, near_threshold=4.0)

        idle = make_square_loop(
            self.lattice,
            origin=(1, y, 0),
            side=2,
            clockwise=True,
        )
        neutral = make_square_loop(
            self.lattice,
            origin=(8, y, 0),
            side=2,
            clockwise=True,
        )
        return apply_local_interaction(idle, neutral, near_threshold=2.0)

    def add_bits(self, left_bits: list[int], right_bits: list[int]) -> TopologicalALUResult:
        carry = 0
        bits: list[int] = []
        transitions: list[CarryTransition] = []

        for plane, (left, right) in enumerate(zip(left_bits[:4], right_bits[:4])):
            xor_lr = left ^ right
            result_bit = xor_lr ^ carry
            generate = left & right
            propagate = xor_lr & carry
            carry_out = 1 if generate or propagate else 0
            interaction = self._local_interaction(plane, left, right, carry)

            transitions.append(
                CarryTransition(
                    plane=plane,
                    target_plane=plane + 1 if plane < 3 else None,
                    left_bit=left,
                    right_bit=right,
                    carry_in=carry,
                    result_bit=result_bit,
                    generate=generate,
                    propagate=propagate,
                    carry_out=carry_out,
                    interaction=interaction["action"],
                    charge_before=interaction["charge_before"],
                    charge_after=interaction["charge_after"],
                )
            )
            bits.append(result_bit)
            carry = carry_out

        return TopologicalALUResult(bits=bits, transitions=transitions)

    def sub_bits(self, left_bits: list[int], right_bits: list[int]) -> TopologicalALUResult:
        inverted = [1 - bit for bit in right_bits[:4]]
        plus_one = self.add_bits(inverted, [1, 0, 0, 0])
        return self.add_bits(left_bits, plus_one.bits)

    def mul_bits(self, left_bits: list[int], right_bits: list[int]) -> TopologicalALUResult:
        result = [0, 0, 0, 0]
        transitions: list[CarryTransition] = []
        for shift, right_bit in enumerate(right_bits[:4]):
            if not right_bit:
                continue
            shifted = ([0] * shift + left_bits[: 4 - shift])[:4]
            add_result = self.add_bits(result, shifted)
            transitions.extend(add_result.transitions)
            result = add_result.bits
        return TopologicalALUResult(bits=result, transitions=transitions)
