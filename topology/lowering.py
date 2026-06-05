from __future__ import annotations

from dataclasses import dataclass

from compiler.lexer import Lexer
from compiler.parser import (
    Parser,
    NodoAsignar,
    NodoBinOp,
    NodoBool,
    NodoBreak,
    NodoCompareChain,
    NodoContinue,
    NodoID,
    NodoIf,
    NodoNum,
    NodoPrint,
    NodoUnOp,
    NodoWhile,
)

from .instructions import (
    TopologicalInstruction,
    TopologicalInstructionMachine,
)


@dataclass
class TopologicalExecutionResult:
    output: list[int]
    snapshot: dict[str, dict]
    phase_projection: dict[str, dict] | None = None


class TopologicalLowerer:
    """
    Baja un subconjunto pequeño de TIE-Lang a instrucciones topologicas.

    Subconjunto actual:
    - `let x = expr`
    - `x = expr`
    - `print expr`
    - `if expr: ... else: ...`
    - expresiones: `0`, `1`, `true`, `false`, `id`, `not expr`, `and`, `or`
    """

    def __init__(self):
        self.instructions: list[TopologicalInstruction] = []
        self.temp_index = 0
        self.label_index = 0
        self.loop_stack: list[tuple[str, str]] = []

    def _new_temp(self) -> str:
        self.temp_index += 1
        return f"__t{self.temp_index}"

    def _new_label(self, prefix: str = "L") -> str:
        self.label_index += 1
        return f"{prefix}{self.label_index}"

    def _eval_expr(self, expr) -> int:
        if isinstance(expr, NodoNum):
            if not 0 <= expr.valor <= 15:
                raise SyntaxError(
                    "El lowering topologico solo acepta literales enteros entre 0 y 15"
                )
            return expr.valor

        if isinstance(expr, NodoBool):
            return int(expr.valor)

        if isinstance(expr, NodoID):
            return 1

        if isinstance(expr, NodoUnOp) and expr.op == "~":
            operand = self._compile_expr_ref(expr.operando)
            if operand[0] == "const":
                return (~operand[1]) & 0xF
            return 1

        if isinstance(expr, NodoUnOp) and expr.op == "not":
            operand = self._compile_expr_ref(expr.operando)
            if operand[0] == "const":
                return 0 if operand[1] else 1
            return 1

        if isinstance(expr, NodoBinOp) and expr.op in ("and", "or", "+", "-", "*", "&", "|", "^"):
            left = self._compile_expr_ref(expr.izq)
            right = self._compile_expr_ref(expr.der)
            if left[0] == right[0] == "const":
                operations = {
                    "and": 1 if left[1] and right[1] else 0,
                    "or": 1 if left[1] or right[1] else 0,
                    "+": (left[1] + right[1]) & 0xF,
                    "-": (left[1] - right[1]) & 0xF,
                    "*": (left[1] * right[1]) & 0xF,
                    "&": left[1] & right[1],
                    "|": left[1] | right[1],
                    "^": left[1] ^ right[1],
                }
                return operations[expr.op]
            return 1

        if isinstance(expr, NodoCompareChain):
            first = self._compile_expr_ref(expr.primero)
            all_const = first[0] == "const"
            actual = first[1] if all_const else None
            for op, siguiente_expr in expr.comparaciones:
                siguiente = self._compile_expr_ref(siguiente_expr)
                all_const = all_const and siguiente[0] == "const"
                if all_const:
                    ok = {
                        "==": actual == siguiente[1],
                        "!=": actual != siguiente[1],
                        "<": actual < siguiente[1],
                        ">": actual > siguiente[1],
                        "<=": actual <= siguiente[1],
                        ">=": actual >= siguiente[1],
                    }[op]
                    if not ok:
                        return 0
                    actual = siguiente[1]
                else:
                    return 1
            return 1

        raise SyntaxError(
            "Expresion no soportada por el lowering topologico v0.3.0"
        )

    def _compile_expr_ref(self, expr):
        if isinstance(expr, NodoID):
            return ("var", expr.nombre)

        if isinstance(expr, NodoBool):
            return ("const", int(expr.valor))

        if isinstance(expr, NodoNum):
            return ("const", self._eval_expr(expr))

        if isinstance(expr, NodoUnOp) and expr.op == "~":
            operand = self._compile_expr_ref(expr.operando)
            if operand[0] == "const":
                return ("const", self._eval_expr(expr))
            temp = self._new_temp()
            self.instructions.append(
                TopologicalInstruction("STORE_UNARY", (temp, "~", operand))
            )
            return ("var", temp)

        if isinstance(expr, NodoUnOp) and expr.op == "not" and isinstance(expr.operando, NodoID):
            return ("not_var", expr.operando.nombre)

        if isinstance(expr, NodoBinOp) and expr.op in ("and", "or", "+", "-", "*", "&", "|", "^"):
            left = self._compile_expr_ref(expr.izq)
            right = self._compile_expr_ref(expr.der)
            if left[0] == right[0] == "const":
                return ("const", self._eval_expr(expr))
            temp = self._new_temp()
            self.instructions.append(
                TopologicalInstruction("STORE_BINARY", (temp, expr.op, left, right))
            )
            return ("var", temp)

        if isinstance(expr, NodoUnOp) and expr.op == "not":
            operand = self._compile_expr_ref(expr.operando)
            if operand[0] == "const":
                return ("const", self._eval_expr(expr))
            temp = self._new_temp()
            self.instructions.append(
                TopologicalInstruction("STORE_UNARY", (temp, "not", operand))
            )
            return ("var", temp)

        if isinstance(expr, NodoCompareChain):
            if all(
                ref[0] == "const"
                for ref in [self._compile_expr_ref(expr.primero)]
            ):
                try:
                    return ("const", self._eval_expr(expr))
                except Exception:
                    pass
            refs = [self._compile_expr_ref(expr.primero)]
            for _, subexpr in expr.comparaciones:
                refs.append(self._compile_expr_ref(subexpr))

            compare_results = []
            for idx, (op, _) in enumerate(expr.comparaciones):
                temp = self._new_temp()
                self.instructions.append(
                    TopologicalInstruction(
                        "STORE_COMPARE",
                        (temp, refs[idx], op, refs[idx + 1]),
                    )
                )
                compare_results.append(("var", temp))

            current = compare_results[0]
            for next_ref in compare_results[1:]:
                temp = self._new_temp()
                self.instructions.append(
                    TopologicalInstruction(
                        "STORE_BINARY",
                        (temp, "and", current, next_ref),
                    )
                )
                current = ("var", temp)
            return current

        raise SyntaxError(
            "Expresion no soportada por el lowering topologico v0.3.0"
        )

    def _assign(self, name: str, expr):
        kind, value = self._compile_expr_ref(expr)

        if kind == "var":
            self.instructions.append(TopologicalInstruction("STORE_COPY", (name, value)))
            return

        if kind == "not_var":
            self.instructions.append(TopologicalInstruction("STORE_NOT", (name, value)))
            return

        self.instructions.append(TopologicalInstruction("STORE_CONST", (name, value)))

    def _emit_print(self, expr):
        kind, value = self._compile_expr_ref(expr)
        if kind == "var":
            self.instructions.append(TopologicalInstruction("PRINT_VAR", (value,)))
            return
        if kind == "not_var":
            self.instructions.append(TopologicalInstruction("PRINT_NOT_VAR", (value,)))
            return
        if kind == "const":
            self.instructions.append(TopologicalInstruction("PRINT_CONST", (value,)))
            return
        self.instructions.append(TopologicalInstruction("PRINT_REF", ((kind, value),)))

    def _compile_stmt(self, stmt):
        if isinstance(stmt, NodoAsignar):
            self._assign(stmt.nombre, stmt.expr)
            return

        if isinstance(stmt, NodoPrint):
            self._emit_print(stmt.expr)
            return

        if isinstance(stmt, NodoIf):
            cond_ref = self._compile_expr_ref(stmt.condicion)
            else_label = self._new_label("else")
            end_label = self._new_label("endif")
            self.instructions.append(
                TopologicalInstruction("JUMP_IF_FALSE", (cond_ref, else_label))
            )
            for substmt in stmt.cuerpo:
                self._compile_stmt(substmt)
            self.instructions.append(TopologicalInstruction("JUMP", (end_label,)))
            self.instructions.append(TopologicalInstruction("LABEL", (else_label,)))
            for substmt in stmt.sino:
                self._compile_stmt(substmt)
            self.instructions.append(TopologicalInstruction("LABEL", (end_label,)))
            return

        if isinstance(stmt, NodoWhile):
            start_label = self._new_label("while")
            end_label = self._new_label("endwhile")
            self.loop_stack.append((start_label, end_label))
            self.instructions.append(TopologicalInstruction("LABEL", (start_label,)))
            cond_ref = self._compile_expr_ref(stmt.condicion)
            self.instructions.append(
                TopologicalInstruction("JUMP_IF_FALSE", (cond_ref, end_label))
            )
            for substmt in stmt.cuerpo:
                self._compile_stmt(substmt)
            self.instructions.append(TopologicalInstruction("JUMP", (start_label,)))
            self.instructions.append(TopologicalInstruction("LABEL", (end_label,)))
            self.loop_stack.pop()
            return

        if isinstance(stmt, NodoBreak):
            if not self.loop_stack:
                raise SyntaxError("break solo puede usarse dentro de un while topologico")
            _, end_label = self.loop_stack[-1]
            self.instructions.append(TopologicalInstruction("JUMP", (end_label,)))
            return

        if isinstance(stmt, NodoContinue):
            if not self.loop_stack:
                raise SyntaxError("continue solo puede usarse dentro de un while topologico")
            start_label, _ = self.loop_stack[-1]
            self.instructions.append(TopologicalInstruction("JUMP", (start_label,)))
            return

        raise SyntaxError(
            "Sentencia no soportada por el lowering topologico v0.3.0"
        )

    def run_source(
        self,
        fuente: str,
        with_phase_projection: bool = False,
        phase_steps: int = 8,
        phase_dt: float = 0.08,
        phase_causal_alu: bool = False,
    ) -> TopologicalExecutionResult:
        lexer = Lexer(fuente)
        parser = Parser(lexer.tokens)
        ast = parser.parse()

        for stmt in ast:
            self._compile_stmt(stmt)

        machine = TopologicalInstructionMachine(
            phase_causal_alu=phase_causal_alu,
            phase_steps=phase_steps,
            phase_dt=phase_dt,
        )
        result = machine.execute(
            self.instructions,
            with_phase_projection=with_phase_projection,
            phase_steps=phase_steps,
            phase_dt=phase_dt,
        )
        return TopologicalExecutionResult(
            output=result.output,
            snapshot=result.snapshot,
            phase_projection=result.phase_projection,
        )


def run_topological_source(
    fuente: str,
    with_phase_projection: bool = False,
    phase_causal_alu: bool = False,
) -> TopologicalExecutionResult:
    lowerer = TopologicalLowerer()
    return lowerer.run_source(
        fuente,
        with_phase_projection=with_phase_projection,
        phase_causal_alu=phase_causal_alu,
    )
