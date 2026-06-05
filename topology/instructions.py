from __future__ import annotations

from dataclasses import dataclass, field

from .alu import CarryTransition, TopologicalALU
from .bridge import PhaseFieldBridge
from .runtime import TopologicalRuntimePreview


@dataclass
class TopologicalInstruction:
    op: str
    args: tuple = field(default_factory=tuple)


@dataclass
class TopologicalProgramResult:
    output: list[int]
    snapshot: dict[str, dict]
    phase_projection: dict[str, dict] | None = None


class TopologicalInstructionMachine:
    """
    Maquina intermedia del backend topologico.
    """

    def __init__(
        self,
        phase_causal_alu: bool = False,
        phase_steps: int = 8,
        phase_dt: float = 0.08,
    ):
        self.runtime = TopologicalRuntimePreview()
        self.alu = TopologicalALU(self.runtime.lattice)
        self.phase_bridge = PhaseFieldBridge()
        self.phase_causal_alu = phase_causal_alu
        self.phase_steps = phase_steps
        self.phase_dt = phase_dt
        self.values: dict[str, int] = {}
        self.origins: dict[str, tuple[int, int, int]] = {}
        self.output: list[int] = []
        self.alu_traces: dict[str, list[CarryTransition]] = {}
        self.phase_causal_reports: dict[str, dict] = {}
        self.next_origin_x = 1
        self.next_origin_y = 1

    def _allocate_origin(self, name: str) -> tuple[int, int, int]:
        if name in self.origins:
            return self.origins[name]
        origin = (self.next_origin_x, self.next_origin_y, 0)
        self.origins[name] = origin
        self.next_origin_x += 8
        if self.next_origin_x > self.runtime.lattice.size_x - 7:
            self.next_origin_x = 1
            self.next_origin_y += 8
        return origin

    def _store_value(self, name: str, value: int):
        if not 0 <= value <= 15:
            raise SyntaxError(
                "La ALU topologica minima solo acepta valores entre 0 y 15"
            )
        self.values[name] = value
        origin = self._allocate_origin(name)
        self.runtime.write_value(name, value, origin=origin)

    def _apply_phase_causal_commit(self, name: str, operation: str):
        if not self.phase_causal_alu or name not in self.runtime.registers:
            return

        projection = self.phase_bridge.project_register(
            self.runtime.registers[name],
            pasos=self.phase_steps,
            dt=self.phase_dt,
        )
        measured_value = projection["measured_value"]
        original_value = self.values[name]
        report = {
            "operation": operation,
            "input_value": original_value,
            "measured_value": measured_value,
            "committed_value": measured_value,
            "bits": projection["bits"],
            "measured_bits": projection["measured_bits"],
            "stability": projection["stability"],
            "layout": projection["layout"],
        }

        self.values[name] = measured_value
        if measured_value != original_value:
            origin = self._allocate_origin(name)
            self.runtime.write_value(name, measured_value, origin=origin)
        self.phase_causal_reports[name] = report

    def _bits_from_value(self, value: int) -> list[int]:
        return self.alu.bits_from_value(value)

    def _value_from_bits(self, bits: list[int]) -> int:
        return self.alu.value_from_bits(bits)

    def _logical_trace(
        self,
        left_bits: list[int],
        right_bits: list[int],
        result_bits: list[int],
    ) -> list[CarryTransition]:
        transitions = []
        for plane, (left_bit, right_bit, result_bit) in enumerate(
            zip(left_bits[:4], right_bits[:4], result_bits[:4])
        ):
            charge_before = (1 if left_bit else -1) + (1 if right_bit else -1)
            charge_after = 1 if result_bit else -1
            transitions.append(
                CarryTransition(
                    plane=plane,
                    target_plane=None,
                    left_bit=left_bit,
                    right_bit=right_bit,
                    carry_in=0,
                    result_bit=result_bit,
                    generate=1 if left_bit and right_bit else 0,
                    propagate=1 if left_bit ^ right_bit else 0,
                    carry_out=0,
                    interaction="logic",
                    charge_before=charge_before,
                    charge_after=charge_after,
                )
            )
        return transitions

    def _resolve_bits(self, ref) -> list[int]:
        return self._bits_from_value(self._resolve_ref(ref))

    def _add_bits(self, left_bits: list[int], right_bits: list[int]) -> list[int]:
        return self.alu.add_bits(left_bits, right_bits).bits

    def _sub_bits(self, left_bits: list[int], right_bits: list[int]) -> list[int]:
        return self.alu.sub_bits(left_bits, right_bits).bits

    def _mul_bits(self, left_bits: list[int], right_bits: list[int]) -> list[int]:
        return self.alu.mul_bits(left_bits, right_bits).bits

    def _resolve_ref(self, ref) -> int:
        kind, value = ref
        if kind == "const":
            return value
        if kind == "var":
            if value not in self.values:
                raise SyntaxError(f"La variable '{value}' no existe")
            return self.values[value]
        raise SyntaxError(f"Referencia topologica desconocida: {ref}")

    def _apply_unary(self, unary_op: str, value: int) -> int:
        if unary_op == "not":
            return 0 if value else 1
        if unary_op == "inc":
            return (value + 1) & 0xF
        if unary_op == "dec":
            return (value - 1) & 0xF
        if unary_op == "~":
            return (~value) & 0xF
        raise SyntaxError(f"Operacion unaria topologica desconocida: {unary_op}")

    def _apply_binary(self, binary_op: str, left: int, right: int) -> int:
        if binary_op == "and":
            return 1 if left and right else 0
        if binary_op == "or":
            return 1 if left or right else 0
        if binary_op == "+":
            return (left + right) & 0xF
        if binary_op == "-":
            return (left - right) & 0xF
        if binary_op == "*":
            return (left * right) & 0xF
        if binary_op == "&":
            return left & right
        if binary_op == "|":
            return left | right
        if binary_op == "^":
            return left ^ right
        raise SyntaxError(f"Operacion binaria topologica desconocida: {binary_op}")

    def _apply_unary_bits(self, unary_op: str, operand_bits: list[int]) -> list[int]:
        if unary_op == "not":
            return self._bits_from_value(0 if self._value_from_bits(operand_bits) else 1)
        if unary_op == "inc":
            return self._add_bits(operand_bits, [1, 0, 0, 0])
        if unary_op == "dec":
            return self._sub_bits(operand_bits, [1, 0, 0, 0])
        if unary_op == "~":
            return [1 - bit for bit in operand_bits]
        raise SyntaxError(f"Operacion unaria topologica desconocida: {unary_op}")

    def _apply_binary_bits(
        self,
        binary_op: str,
        left_bits: list[int],
        right_bits: list[int],
    ) -> list[int]:
        left_value = self._value_from_bits(left_bits)
        right_value = self._value_from_bits(right_bits)
        if binary_op == "and":
            return self._bits_from_value(1 if left_value and right_value else 0)
        if binary_op == "or":
            return self._bits_from_value(1 if left_value or right_value else 0)
        if binary_op == "+":
            return self._add_bits(left_bits, right_bits)
        if binary_op == "-":
            return self._sub_bits(left_bits, right_bits)
        if binary_op == "*":
            return self._mul_bits(left_bits, right_bits)
        if binary_op == "&":
            return [left & right for left, right in zip(left_bits, right_bits)]
        if binary_op == "|":
            return [left | right for left, right in zip(left_bits, right_bits)]
        if binary_op == "^":
            return [left ^ right for left, right in zip(left_bits, right_bits)]
        raise SyntaxError(f"Operacion binaria topologica desconocida: {binary_op}")

    def execute(
        self,
        instructions: list[TopologicalInstruction],
        with_phase_projection: bool = False,
        phase_steps: int = 8,
        phase_dt: float = 0.08,
    ) -> TopologicalProgramResult:
        labels = {
            ins.args[0]: idx
            for idx, ins in enumerate(instructions)
            if ins.op == "LABEL"
        }

        ip = 0
        while ip < len(instructions):
            ins = instructions[ip]
            op = ins.op
            args = ins.args

            if op == "LABEL":
                ip += 1
                continue

            if op == "STORE_CONST":
                name, value = args
                self._store_value(name, value)
                ip += 1
                continue

            if op == "STORE_COPY":
                target, source = args
                if source not in self.values:
                    raise SyntaxError(f"La variable '{source}' no existe")
                self._store_value(target, self.values[source])
                if source in self.alu_traces:
                    self.alu_traces[target] = self.alu_traces[source]
                if source in self.phase_causal_reports:
                    self.phase_causal_reports[target] = {
                        **self.phase_causal_reports[source],
                        "source": source,
                    }
                ip += 1
                continue

            if op == "STORE_NOT":
                target, source = args
                if source not in self.values:
                    raise SyntaxError(f"La variable '{source}' no existe")
                value = 0 if self.values[source] else 1
                self._store_value(target, value)
                ip += 1
                continue

            if op == "STORE_UNARY":
                target, unary_op, operand_ref = args
                operand_bits = self._resolve_bits(operand_ref)
                result_bits = self._apply_unary_bits(unary_op, operand_bits)
                self._store_value(target, self._value_from_bits(result_bits))
                if unary_op in ("inc", "dec"):
                    other = [1, 0, 0, 0]
                    result = (
                        self.alu.add_bits(operand_bits, other)
                        if unary_op == "inc"
                        else self.alu.sub_bits(operand_bits, other)
                    )
                    self.alu_traces[target] = result.transitions
                if unary_op == "~":
                    self.alu_traces[target] = self._logical_trace(
                        operand_bits,
                        [0, 0, 0, 0],
                        result_bits,
                    )
                if unary_op in ("inc", "dec", "~"):
                    self._apply_phase_causal_commit(target, unary_op)
                ip += 1
                continue

            if op == "STORE_BINARY":
                target, binary_op, left_ref, right_ref = args
                left_bits = self._resolve_bits(left_ref)
                right_bits = self._resolve_bits(right_ref)
                result_bits = self._apply_binary_bits(binary_op, left_bits, right_bits)
                self._store_value(target, self._value_from_bits(result_bits))
                if binary_op in ("+", "-", "*"):
                    result = {
                        "+": self.alu.add_bits,
                        "-": self.alu.sub_bits,
                        "*": self.alu.mul_bits,
                    }[binary_op](left_bits, right_bits)
                    self.alu_traces[target] = result.transitions
                if binary_op in ("&", "|", "^"):
                    self.alu_traces[target] = self._logical_trace(
                        left_bits,
                        right_bits,
                        result_bits,
                    )
                if binary_op in ("+", "-", "*", "&", "|", "^"):
                    self._apply_phase_causal_commit(target, binary_op)
                ip += 1
                continue

            if op == "STORE_COMPARE":
                target, left_ref, cmp_op, right_ref = args
                left = self._resolve_ref(left_ref)
                right = self._resolve_ref(right_ref)
                value = {
                    "==": 1 if left == right else 0,
                    "!=": 1 if left != right else 0,
                    "<": 1 if left < right else 0,
                    ">": 1 if left > right else 0,
                    "<=": 1 if left <= right else 0,
                    ">=": 1 if left >= right else 0,
                }.get(cmp_op)
                if value is None:
                    raise SyntaxError(f"Comparador topologico desconocido: {cmp_op}")
                self._store_value(target, value)
                ip += 1
                continue

            if op == "PRINT_CONST":
                value, = args
                self.output.append(value)
                ip += 1
                continue

            if op == "PRINT_VAR":
                name, = args
                if name not in self.values:
                    raise SyntaxError(f"La variable '{name}' no existe")
                self.output.append(self.values[name])
                ip += 1
                continue

            if op == "PRINT_NOT_VAR":
                name, = args
                if name not in self.values:
                    raise SyntaxError(f"La variable '{name}' no existe")
                self.output.append(0 if self.values[name] else 1)
                ip += 1
                continue

            if op == "PRINT_REF":
                ref, = args
                self.output.append(self._resolve_ref(ref))
                ip += 1
                continue

            if op == "JUMP":
                label, = args
                ip = labels[label]
                continue

            if op == "JUMP_IF_FALSE":
                cond_ref, label = args
                cond = self._resolve_ref(cond_ref)
                if cond == 0:
                    ip = labels[label]
                else:
                    ip += 1
                continue

            raise SyntaxError(f"Instruccion topologica desconocida: {op}")

        projection = None
        if with_phase_projection:
            projection = self.runtime.phase_projection(
                pasos=phase_steps,
                dt=phase_dt,
            )

        runtime_snapshot = self.runtime.snapshot()

        return TopologicalProgramResult(
            output=self.output[:],
            snapshot={
                name: (
                    {
                        "value": self.values[name],
                        "topological": False,
                    }
                    if name not in runtime_snapshot
                    else {
                        "value": self.values[name],
                        "topological": True,
                        **runtime_snapshot[name],
                        **(
                            {
                                "alu_trace": [
                                    {
                                        "plane": transition.plane,
                                        "target_plane": transition.target_plane,
                                        "left_bit": transition.left_bit,
                                        "right_bit": transition.right_bit,
                                        "carry_in": transition.carry_in,
                                        "result_bit": transition.result_bit,
                                        "generate": transition.generate,
                                        "propagate": transition.propagate,
                                        "carry_out": transition.carry_out,
                                        "interaction": transition.interaction,
                                        "charge_before": transition.charge_before,
                                        "charge_after": transition.charge_after,
                                    }
                                    for transition in self.alu_traces[name]
                                ]
                            }
                            if name in self.alu_traces
                            else {}
                        ),
                        **(
                            {"phase_causal": self.phase_causal_reports[name]}
                            if name in self.phase_causal_reports
                            else {}
                        ),
                    }
                )
                for name in self.values
            },
            phase_projection=projection,
        )
