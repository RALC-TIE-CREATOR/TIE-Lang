"""
compiler/compiler.py
--------------------
Generador de código: AST → instrucciones CPU TIE-Lang.

Estrategia:
    Variables  → RAM (dirección fija por nombre)
    Expresiones→ R0/R1 temporales, resultado en R0
    Funciones  → R3 valor de retorno
    Etiquetas  → generadas automáticamente (L1, L2, ...)

compile_and_run() es el punto de entrada principal.
"""

from typing import List, Dict
from .lexer import Lexer
from .parser import (
    Parser, NodoNum, NodoBool, NodoID, NodoSymbol, NodoLista, NodoIndex,
    NodoBinOp, NodoCompareChain, NodoUnOp, NodoAsignar, NodoGlobalAsignar,
    NodoIndexAsignar, NodoIf, NodoWhile, NodoDef, NodoLlamar, NodoReturn,
    NodoPrint, NodoBreak, NodoContinue
)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cpu.instrucciones import Instruccion, Operacion
from cpu.cpu import CPU


class Compilador:
    """Transforma el AST en instrucciones para la CPU TIE-Lang."""

    def __init__(self):
        self.codigo:     List[Instruccion] = []
        self.variables:  Dict[str, int]    = {}
        self.funciones:  Dict[str, object] = {}
        self.next_addr:  int = 0
        self.next_label: int = 0
        self.scope_stack: List[Dict[str, int]] = [self.variables]
        self.array_scopes: List[Dict[str, tuple[int, int]]] = [{}]
        self.in_function: bool = False
        self.loop_stack: List[tuple[str, str]] = []
        self.simbolos: Dict[str, int] = {}
        self.function_array_params: Dict[str, Dict[int, int]] = {}
        self.function_array_param_slots: Dict[str, Dict[int, tuple[int, int]]] = {}

    def _nueva_etiqueta(self, prefijo='L') -> str:
        self.next_label += 1
        return f"{prefijo}{self.next_label}"

    def _alloc_addr(self, scope: Dict[str, int], nombre: str) -> int:
        if nombre not in scope:
            scope[nombre] = self.next_addr
            self.next_addr += 1
        return scope[nombre]

    def _scope_actual(self) -> Dict[str, int]:
        return self.scope_stack[-1]

    def _array_scope_actual(self) -> Dict[str, tuple[int, int]]:
        return self.array_scopes[-1]

    def _binding_en_scope(self, escalar_scope, array_scope, nombre: str):
        if nombre in escalar_scope:
            return 'scalar', escalar_scope[nombre]
        if nombre in array_scope:
            return 'array', array_scope[nombre]
        return None, None

    def _push_scope(self):
        self.scope_stack.append({})
        self.array_scopes.append({})

    def _pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.array_scopes.pop()

    def _lookup_binding(self, nombre: str):
        if self.in_function:
            for escalar_scope, array_scope in zip(
                    reversed(self.scope_stack[1:]),
                    reversed(self.array_scopes[1:])):
                kind, value = self._binding_en_scope(
                    escalar_scope, array_scope, nombre)
                if kind is not None:
                    return kind, value
        return self._binding_en_scope(
            self.variables, self.array_scopes[0], nombre)

    def _intern_symbol(self, nombre: str) -> int:
        if nombre not in self.simbolos:
            if len(self.simbolos) >= 16:
                raise SyntaxError(
                    "Se excedio el maximo de 16 simbolos ligeros por programa")
            self.simbolos[nombre] = len(self.simbolos)
        return self.simbolos[nombre]

    def _iterar_exprs(self, nodo):
        if nodo is None:
            return
        yield nodo
        if isinstance(nodo, NodoBinOp):
            yield from self._iterar_exprs(nodo.izq)
            yield from self._iterar_exprs(nodo.der)
        elif isinstance(nodo, NodoCompareChain):
            yield from self._iterar_exprs(nodo.primero)
            for _, expr in nodo.comparaciones:
                yield from self._iterar_exprs(expr)
        elif isinstance(nodo, NodoUnOp):
            yield from self._iterar_exprs(nodo.operando)
        elif isinstance(nodo, NodoLista):
            for expr in nodo.elementos:
                yield from self._iterar_exprs(expr)
        elif isinstance(nodo, NodoIndex):
            yield from self._iterar_exprs(nodo.indice)
        elif isinstance(nodo, NodoLlamar):
            for arg in nodo.args:
                yield from self._iterar_exprs(arg)

    def _colectar_defs(self, stmts):
        for stmt in stmts:
            if isinstance(stmt, NodoDef):
                self.funciones[stmt.nombre] = stmt
                self._colectar_defs(stmt.cuerpo)
            elif isinstance(stmt, NodoIf):
                self._colectar_defs(stmt.cuerpo)
                self._colectar_defs(stmt.sino)
            elif isinstance(stmt, NodoWhile):
                self._colectar_defs(stmt.cuerpo)

    def _parametros_arreglo_en_cuerpo(self, nodo_def: NodoDef) -> set[str]:
        usados = set()
        params = set(nodo_def.params)

        def visitar_expr(expr):
            if isinstance(expr, NodoIndex) and expr.nombre in params:
                usados.add(expr.nombre)
                visitar_expr(expr.indice)
                return
            if isinstance(expr, NodoLlamar):
                if expr.nombre in ('len', 'first', 'last'):
                    for arg in expr.args:
                        if isinstance(arg, NodoID) and arg.nombre in params:
                            usados.add(arg.nombre)
                        visitar_expr(arg)
                    return
                for arg in expr.args:
                    visitar_expr(arg)
                return
            if isinstance(expr, NodoBinOp):
                visitar_expr(expr.izq)
                visitar_expr(expr.der)
                return
            if isinstance(expr, NodoCompareChain):
                visitar_expr(expr.primero)
                for _, subexpr in expr.comparaciones:
                    visitar_expr(subexpr)
                return
            if isinstance(expr, NodoUnOp):
                visitar_expr(expr.operando)
                return
            if isinstance(expr, NodoLista):
                for subexpr in expr.elementos:
                    visitar_expr(subexpr)

        def visitar_stmt(stmt):
            if isinstance(stmt, NodoIndexAsignar):
                if stmt.nombre in params:
                    usados.add(stmt.nombre)
                visitar_expr(stmt.indice)
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoAsignar):
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoGlobalAsignar):
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoPrint):
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoReturn):
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoIf):
                visitar_expr(stmt.condicion)
                for sub in stmt.cuerpo:
                    visitar_stmt(sub)
                for sub in stmt.sino:
                    visitar_stmt(sub)
            elif isinstance(stmt, NodoWhile):
                visitar_expr(stmt.condicion)
                for sub in stmt.cuerpo:
                    visitar_stmt(sub)
            elif isinstance(stmt, NodoLlamar):
                visitar_expr(stmt)

        for stmt in nodo_def.cuerpo:
            visitar_stmt(stmt)
        return usados

    def _resolver_longitud_arg_arreglo(self, arg, array_scopes, scalar_scopes):
        if isinstance(arg, NodoLista):
            return len(arg.elementos)
        if isinstance(arg, NodoID):
            nombre = arg.nombre
            for escalar_scope, array_scope in zip(
                    reversed(scalar_scopes),
                    reversed(array_scopes)):
                if nombre in escalar_scope:
                    return None
                if nombre in array_scope:
                    return array_scope[nombre]
        return None

    def _registrar_longitud_param_arreglo(self, fn_name: str, index: int,
                                          longitud: int):
        info = self.function_array_params.setdefault(fn_name, {})
        previa = info.get(index)
        if previa is None:
            info[index] = longitud
        elif previa != longitud:
            raise SyntaxError(
                f"El parametro arreglo #{index + 1} de '{fn_name}' "
                f"recibe longitudes incompatibles ({previa} y {longitud})")

    def _preanalizar_llamadas(self, stmts, scalar_scopes=None, array_scopes=None):
        if scalar_scopes is None:
            scalar_scopes = [set()]
        if array_scopes is None:
            array_scopes = [{}]

        def declarar_escalar(nombre: str, declaracion: bool):
            if declaracion or len(scalar_scopes) == 1:
                scalar_scopes[-1].add(nombre)
                return
            for scope in reversed(scalar_scopes):
                if nombre in scope:
                    return
            scalar_scopes[-1].add(nombre)

        def declarar_array(nombre: str, longitud: int, declaracion: bool,
                           global_explicito: bool = False):
            if global_explicito:
                array_scopes[0][nombre] = longitud
                return
            if declaracion or len(array_scopes) == 1:
                array_scopes[-1][nombre] = longitud
                return
            for scope in reversed(array_scopes):
                if nombre in scope:
                    scope[nombre] = longitud
                    return
            array_scopes[-1][nombre] = longitud

        def visitar_expr(expr):
            if isinstance(expr, NodoLlamar):
                self._registrar_llamada_arreglo(expr, array_scopes, scalar_scopes)
                for arg in expr.args:
                    visitar_expr(arg)
            elif isinstance(expr, NodoBinOp):
                visitar_expr(expr.izq)
                visitar_expr(expr.der)
            elif isinstance(expr, NodoCompareChain):
                visitar_expr(expr.primero)
                for _, subexpr in expr.comparaciones:
                    visitar_expr(subexpr)
            elif isinstance(expr, NodoUnOp):
                visitar_expr(expr.operando)
            elif isinstance(expr, NodoLista):
                for subexpr in expr.elementos:
                    visitar_expr(subexpr)
            elif isinstance(expr, NodoIndex):
                visitar_expr(expr.indice)

        for stmt in stmts:
            if isinstance(stmt, NodoAsignar):
                if isinstance(stmt.expr, NodoLista):
                    declarar_array(stmt.nombre, len(stmt.expr.elementos),
                                   stmt.declaracion)
                    for subexpr in stmt.expr.elementos:
                        visitar_expr(subexpr)
                else:
                    declarar_escalar(stmt.nombre, stmt.declaracion)
                    visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoGlobalAsignar):
                if isinstance(stmt.expr, NodoLista):
                    declarar_array(stmt.nombre, len(stmt.expr.elementos), False,
                                   global_explicito=True)
                    for subexpr in stmt.expr.elementos:
                        visitar_expr(subexpr)
                else:
                    scalar_scopes[0].add(stmt.nombre)
                    visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoIndexAsignar):
                visitar_expr(stmt.indice)
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoPrint):
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoReturn):
                visitar_expr(stmt.expr)
            elif isinstance(stmt, NodoLlamar):
                self._registrar_llamada_arreglo(stmt, array_scopes, scalar_scopes)
                for arg in stmt.args:
                    visitar_expr(arg)
            elif isinstance(stmt, NodoIf):
                visitar_expr(stmt.condicion)
                scalar_scopes.append(set())
                array_scopes.append({})
                self._preanalizar_llamadas(stmt.cuerpo, scalar_scopes, array_scopes)
                scalar_scopes.pop()
                array_scopes.pop()
                scalar_scopes.append(set())
                array_scopes.append({})
                self._preanalizar_llamadas(stmt.sino, scalar_scopes, array_scopes)
                scalar_scopes.pop()
                array_scopes.pop()
            elif isinstance(stmt, NodoWhile):
                visitar_expr(stmt.condicion)
                scalar_scopes.append(set())
                array_scopes.append({})
                self._preanalizar_llamadas(stmt.cuerpo, scalar_scopes, array_scopes)
                scalar_scopes.pop()
                array_scopes.pop()
            elif isinstance(stmt, NodoDef):
                params_array = {
                    index: self.function_array_params.get(stmt.nombre, {}).get(index)
                    for index in self.function_array_params.get(stmt.nombre, {})
                }
                scalar_scopes.append(set())
                array_scopes.append({})
                for index, param in enumerate(stmt.params):
                    if index in params_array:
                        longitud = params_array[index]
                        if longitud is not None:
                            array_scopes[-1][param] = longitud
                    else:
                        scalar_scopes[-1].add(param)
                self._preanalizar_llamadas(stmt.cuerpo, scalar_scopes, array_scopes)
                scalar_scopes.pop()
                array_scopes.pop()

    def _registrar_llamada_arreglo(self, llamada: NodoLlamar, array_scopes, scalar_scopes):
        if llamada.nombre in ('len', 'first', 'last'):
            return
        if llamada.nombre not in self.funciones:
            return
        param_arrays = self.function_array_params.get(llamada.nombre, {})
        for index, _ in param_arrays.items():
            if index >= len(llamada.args):
                continue
            longitud = self._resolver_longitud_arg_arreglo(
                llamada.args[index], array_scopes, scalar_scopes)
            if longitud is None:
                raise SyntaxError(
                    f"El parametro arreglo #{index + 1} de '{llamada.nombre}' "
                    f"debe recibir un arreglo o literal de arreglo")
            self._registrar_longitud_param_arreglo(
                llamada.nombre, index, longitud)

    def _reservar_parametros_arreglo(self):
        for fn_name, nodo_def in self.funciones.items():
            param_lengths = self.function_array_params.get(fn_name, {})
            if not param_lengths:
                continue
            slots = {}
            for index, longitud in param_lengths.items():
                if longitud is None:
                    raise SyntaxError(
                        f"No se pudo inferir la longitud del parametro arreglo "
                        f"#{index + 1} de '{fn_name}'")
                base = self.next_addr
                self.next_addr += longitud
                slots[index] = (base, longitud)
            self.function_array_param_slots[fn_name] = slots

    def _preanalizar_programa(self, ast: list):
        self.funciones = {}
        self.function_array_params = {}
        self.function_array_param_slots = {}
        self._colectar_defs(ast)
        for fn_name, nodo_def in self.funciones.items():
            usados = self._parametros_arreglo_en_cuerpo(nodo_def)
            if usados:
                self.function_array_params[fn_name] = {
                    index: None
                    for index, param in enumerate(nodo_def.params)
                    if param in usados
                }
        self._preanalizar_llamadas(ast)
        self._reservar_parametros_arreglo()

    def _registrar_parametros_arreglo_en_scope(self, nodo_def: NodoDef):
        slots = self.function_array_param_slots.get(nodo_def.nombre, {})
        if not slots:
            return
        array_scope = self._array_scope_actual()
        for index, (base, longitud) in slots.items():
            array_scope[nodo_def.params[index]] = (base, longitud)

    def _copiar_argumento_arreglo(self, arg, base_dest: int, longitud: int):
        if isinstance(arg, NodoLista):
            if len(arg.elementos) != longitud:
                raise SyntaxError(
                    "Literal de arreglo con longitud incompatible en llamada")
            for offset, expr in enumerate(arg.elementos):
                self.compilar_expr(expr, 'R0')
                self._emit(Operacion.STORE, None, 'R0', str(base_dest + offset))
            return

        if isinstance(arg, NodoID):
            info = self._lookup_array(arg.nombre)
            if info is None:
                raise SyntaxError(
                    f"El argumento '{arg.nombre}' no es un arreglo valido")
            base_src, longitud_src = info
            if longitud_src != longitud:
                raise SyntaxError(
                    f"El arreglo '{arg.nombre}' tiene longitud {longitud_src} "
                    f"y se esperaba {longitud}")
            for offset in range(longitud):
                self._emit(Operacion.LOAD_M, 'R0', str(base_src + offset))
                self._emit(Operacion.STORE, None, 'R0', str(base_dest + offset))
            return

        raise SyntaxError(
            "Los parametros arreglo solo aceptan arreglos nombrados o literales")

    def _lookup_array(self, nombre: str):
        kind, value = self._lookup_binding(nombre)
        if kind == 'array':
            return value
        return None

    def _resolve_array_scope(self, nombre: str):
        if self.in_function:
            for escalar_scope, array_scope in zip(
                    reversed(self.scope_stack[1:]),
                    reversed(self.array_scopes[1:])):
                kind, _ = self._binding_en_scope(
                    escalar_scope, array_scope, nombre)
                if kind == 'array':
                    return array_scope
                if kind == 'scalar':
                    return None
        kind, _ = self._binding_en_scope(
            self.variables, self.array_scopes[0], nombre)
        if kind == 'array':
            return self.array_scopes[0]
        return None

    def _alloc_array(self, scope: Dict[str, tuple[int, int]],
                     nombre: str, longitud: int) -> tuple[int, int]:
        if nombre in scope:
            base, existente = scope[nombre]
            if existente != longitud:
                raise SyntaxError(
                    f"El arreglo '{nombre}' ya existe con longitud {existente}")
            return base, existente
        if nombre in self.variables and scope is not self.array_scopes[0]:
            pass
        base = self.next_addr
        self.next_addr += longitud
        scope[nombre] = (base, longitud)
        return base, longitud

    def _asignar_lista(self, nombre: str, nodo_lista: NodoLista,
                       declaracion: bool = False, global_explicito: bool = False):
        elementos = nodo_lista.elementos
        longitud = len(elementos)
        if longitud == 0:
            raise SyntaxError("Los arreglos vacios aun no estan soportados")

        if global_explicito:
            scope = self.array_scopes[0]
            if nombre in self.variables:
                raise SyntaxError(
                    f"'{nombre}' ya existe como escalar global")
        elif declaracion:
            scope = self.array_scopes[0] if not self.in_function else self._array_scope_actual()
            scope_escalar = self.variables if scope is self.array_scopes[0] else self._scope_actual()
            if nombre in scope_escalar:
                raise SyntaxError(
                    f"'{nombre}' ya existe como variable escalar")
        else:
            scope = self._resolve_array_scope(nombre)
            if scope is None:
                raise SyntaxError(
                    f"El arreglo '{nombre}' debe declararse con let antes de reasignarse")

        if not global_explicito and not declaracion and nombre in self.variables and scope is self.array_scopes[0]:
            pass

        base, existente = self._alloc_array(scope, nombre, longitud)
        if existente != longitud:
            raise SyntaxError(
                f"El arreglo '{nombre}' esperaba {existente} elementos")

        for offset, expr in enumerate(elementos):
            self.compilar_expr(expr, 'R0')
            self._emit(Operacion.STORE, None, 'R0', str(base + offset))

    def _emit_array_load(self, nombre: str, indice, reg: str) -> str:
        info = self._lookup_array(nombre)
        if info is None:
            raise SyntaxError(f"Arreglo no definido: {nombre}")
        base, longitud = info

        if isinstance(indice, NodoNum):
            if indice.valor < 0 or indice.valor >= longitud:
                raise SyntaxError(
                    f"Indice fuera de rango para '{nombre}': {indice.valor}")
            self._emit(Operacion.LOAD_M, reg, str(base + indice.valor))
            return reg

        self.compilar_expr(indice, 'R1')
        idx_temp = self._addr_temp()
        self._emit(Operacion.STORE, None, 'R1', str(idx_temp))
        etq_fin = self._nueva_etiqueta('arrfin')
        etq_default = self._nueva_etiqueta('arrdefault')
        etiquetas_match = [self._nueva_etiqueta('arrmatch')
                           for _ in range(longitud)]

        for i, etq_match in enumerate(etiquetas_match):
            self._emit(Operacion.LOAD_M, 'R1', str(idx_temp))
            self._emit(Operacion.CMP, None, 'R1', str(i))
            self._emit(Operacion.JZ, None, etq_match)

        self._emit(Operacion.JMP, None, etq_default)
        for i, etq_match in enumerate(etiquetas_match):
            self._emit(Operacion.LOAD_M, reg, str(base + i), label=etq_match)
            self._emit(Operacion.JMP, None, etq_fin)
        self._emit(Operacion.LOAD, reg, '0', label=etq_default)
        self._emit(Operacion.LOAD, reg, reg, label=etq_fin)
        return reg

    def _emit_array_store(self, nombre: str, indice, valor_reg: str = 'R0'):
        info = self._lookup_array(nombre)
        if info is None:
            raise SyntaxError(f"Arreglo no definido: {nombre}")
        base, longitud = info

        if isinstance(indice, NodoNum):
            if indice.valor < 0 or indice.valor >= longitud:
                raise SyntaxError(
                    f"Indice fuera de rango para '{nombre}': {indice.valor}")
            self._emit(Operacion.STORE, None, valor_reg, str(base + indice.valor))
            return

        valor_temp = self._addr_temp()
        idx_temp = self._addr_temp()
        self._emit(Operacion.STORE, None, valor_reg, str(valor_temp))
        self.compilar_expr(indice, 'R1')
        self._emit(Operacion.STORE, None, 'R1', str(idx_temp))
        etq_fin = self._nueva_etiqueta('arrstorefin')
        etiquetas_match = [self._nueva_etiqueta('arrstore')
                           for _ in range(longitud)]

        for i, etq_match in enumerate(etiquetas_match):
            self._emit(Operacion.LOAD_M, 'R1', str(idx_temp))
            self._emit(Operacion.CMP, None, 'R1', str(i))
            self._emit(Operacion.JZ, None, etq_match)

        self._emit(Operacion.JMP, None, etq_fin)
        for i, etq_match in enumerate(etiquetas_match):
            self._emit(Operacion.LOAD_M, 'R0', str(valor_temp), label=etq_match)
            self._emit(Operacion.STORE, None, 'R0', str(base + i))
            self._emit(Operacion.JMP, None, etq_fin)
        self._emit(Operacion.LOAD, 'R3', 'R3', label=etq_fin)

    def _addr_lectura(self, nombre: str) -> int:
        kind, value = self._lookup_binding(nombre)
        if kind == 'scalar':
            return value
        if kind == 'array':
            raise SyntaxError(
                f"El arreglo '{nombre}' debe usarse con indice")
        return self._alloc_addr(self.variables, nombre)

    def _addr_escritura(self, nombre: str, declaracion: bool = False) -> int:
        if self.in_function:
            if declaracion:
                return self._alloc_addr(self._scope_actual(), nombre)
            for scope in reversed(self.scope_stack[1:]):
                if nombre in scope:
                    return scope[nombre]
            return self._alloc_addr(self._scope_actual(), nombre)
        return self._alloc_addr(self.variables, nombre)

    def _addr_global(self, nombre: str) -> int:
        return self._alloc_addr(self.variables, nombre)

    def _addr_temp(self) -> int:
        addr = self.next_addr
        self.next_addr += 1
        return addr

    def _emit(self, op, dest=None, src1=None,
              src2=None, label=None):
        self.codigo.append(
            Instruccion(op, dest, src1, src2, label))

    def _emit_bool_desde_cmp(self, reg: str, true_on_zero: bool = False):
        etq_si  = self._nueva_etiqueta('si')
        etq_no  = self._nueva_etiqueta('no')
        etq_fin = self._nueva_etiqueta('fin')
        self._emit(Operacion.JZ, None, etq_si if true_on_zero else etq_no)
        self._emit(Operacion.LOAD, reg, '1' if not true_on_zero else '0')
        self._emit(Operacion.JMP, None, etq_fin)
        self._emit(
            Operacion.LOAD,
            reg,
            '0' if not true_on_zero else '1',
            label=etq_si if true_on_zero else etq_no,
        )
        self._emit(Operacion.LOAD, reg, reg, label=etq_fin)

    def _emit_cmp_result(self, op: str, reg: str):
        etq_si  = self._nueva_etiqueta('si')
        etq_no  = self._nueva_etiqueta('no')
        etq_fin = self._nueva_etiqueta('fin')

        if op == '==':
            self._emit(Operacion.JZ, None, etq_si)

        elif op == '!=':
            self._emit(Operacion.JZ, None, etq_no)
            self._emit(Operacion.JMP, None, etq_si)

        elif op == '<':
            self._emit(Operacion.JN, None, etq_si)

        elif op == '>':
            self._emit(Operacion.JZ, None, etq_no)
            self._emit(Operacion.JN, None, etq_no)
            self._emit(Operacion.JMP, None, etq_si)

        elif op == '<=':
            self._emit(Operacion.JZ, None, etq_si)
            self._emit(Operacion.JN, None, etq_si)

        elif op == '>=':
            self._emit(Operacion.JN, None, etq_no)
            self._emit(Operacion.JMP, None, etq_si)

        self._emit(Operacion.LOAD, reg, '0', label=etq_no)
        self._emit(Operacion.JMP, None, etq_fin)
        self._emit(Operacion.LOAD, reg, '1', label=etq_si)
        self._emit(Operacion.JMP, None, etq_fin)
        self._emit(Operacion.LOAD, reg, reg, label=etq_fin)

    def _emit_cmp_fail_jump(self, op: str, fail_label: str):
        if op == '==':
            etq_ok = self._nueva_etiqueta('cmpok')
            self._emit(Operacion.JZ, None, etq_ok)
            self._emit(Operacion.JMP, None, fail_label)
            self._emit(Operacion.LOAD, 'R3', 'R3', label=etq_ok)
            return

        if op == '!=':
            self._emit(Operacion.JZ, None, fail_label)
            return

        if op == '<':
            etq_ok = self._nueva_etiqueta('cmpok')
            self._emit(Operacion.JN, None, etq_ok)
            self._emit(Operacion.JMP, None, fail_label)
            self._emit(Operacion.LOAD, 'R3', 'R3', label=etq_ok)
            return

        if op == '>':
            self._emit(Operacion.JZ, None, fail_label)
            self._emit(Operacion.JN, None, fail_label)
            return

        if op == '<=':
            etq_ok = self._nueva_etiqueta('cmpok')
            self._emit(Operacion.JZ, None, etq_ok)
            self._emit(Operacion.JN, None, etq_ok)
            self._emit(Operacion.JMP, None, fail_label)
            self._emit(Operacion.LOAD, 'R3', 'R3', label=etq_ok)
            return

        if op == '>=':
            self._emit(Operacion.JN, None, fail_label)
            return

    def _compilar_bloque(self, stmts, scope_local: bool = False):
        if scope_local:
            self._push_scope()
        for stmt in stmts:
            self.compilar_stmt(stmt)
        if scope_local:
            self._pop_scope()

    # ── Compilar expresión ───────────────────────────────────────────

    def compilar_expr(self, nodo, reg='R0') -> str:

        if isinstance(nodo, NodoNum):
            self._emit(Operacion.LOAD, reg, str(nodo.valor & 0xF))
            return reg

        if isinstance(nodo, NodoBool):
            self._emit(Operacion.LOAD, reg, '1' if nodo.valor else '0')
            return reg

        if isinstance(nodo, NodoSymbol):
            self._emit(Operacion.LOAD, reg,
                       str(self._intern_symbol(nodo.nombre)))
            return reg

        if isinstance(nodo, NodoLista):
            raise SyntaxError(
                "Los literales de arreglo solo pueden usarse en asignaciones")

        if isinstance(nodo, NodoID):
            self._emit(Operacion.LOAD_M, reg,
                       str(self._addr_lectura(nodo.nombre)))
            return reg

        if isinstance(nodo, NodoIndex):
            return self._emit_array_load(nodo.nombre, nodo.indice, reg)

        if isinstance(nodo, NodoUnOp):
            self.compilar_expr(nodo.operando, reg)
            if nodo.op == '~':
                self._emit(Operacion.NOT, reg, reg)
            elif nodo.op == 'not':
                self._emit(Operacion.CMP, None, reg, '0')
                self._emit_bool_desde_cmp(reg, true_on_zero=True)
            return reg

        if isinstance(nodo, NodoBinOp):
            if nodo.op == 'and':
                etq_false = self._nueva_etiqueta('andfalse')
                etq_fin   = self._nueva_etiqueta('andfin')
                self.compilar_expr(nodo.izq, reg)
                self._emit(Operacion.CMP, None, reg, '0')
                self._emit(Operacion.JZ, None, etq_false)
                self.compilar_expr(nodo.der, reg)
                self._emit(Operacion.CMP, None, reg, '0')
                self._emit(Operacion.JZ, None, etq_false)
                self._emit(Operacion.LOAD, reg, '1')
                self._emit(Operacion.JMP, None, etq_fin)
                self._emit(Operacion.LOAD, reg, '0', label=etq_false)
                self._emit(Operacion.LOAD, reg, reg, label=etq_fin)
                return reg

            if nodo.op == 'or':
                etq_eval_rhs = self._nueva_etiqueta('orevalrhs')
                etq_false    = self._nueva_etiqueta('orfalse')
                etq_fin      = self._nueva_etiqueta('orfin')
                self.compilar_expr(nodo.izq, reg)
                self._emit(Operacion.CMP, None, reg, '0')
                self._emit(Operacion.JZ, None, etq_eval_rhs)
                self._emit(Operacion.LOAD, reg, '1')
                self._emit(Operacion.JMP, None, etq_fin)
                self._emit(Operacion.LOAD, reg, reg, label=etq_eval_rhs)
                self.compilar_expr(nodo.der, reg)
                self._emit(Operacion.CMP, None, reg, '0')
                self._emit(Operacion.JZ, None, etq_false)
                self._emit(Operacion.LOAD, reg, '1')
                self._emit(Operacion.JMP, None, etq_fin)
                self._emit(Operacion.LOAD, reg, '0', label=etq_false)
                self._emit(Operacion.LOAD, reg, reg, label=etq_fin)
                return reg

            self.compilar_expr(nodo.izq, 'R0')
            temp_izq = self._addr_temp()
            self._emit(Operacion.STORE, None, 'R0', str(temp_izq))
            self.compilar_expr(nodo.der, 'R1')
            self._emit(Operacion.LOAD_M, 'R0', str(temp_izq))

            op_map = {
                '+': Operacion.SUMA,
                '-': Operacion.RESTA,
                '&': Operacion.AND,
                '|': Operacion.OR,
                '^': Operacion.XOR,
            }

            if nodo.op in op_map:
                self._emit(op_map[nodo.op], reg, 'R0', 'R1')
                return reg

            if nodo.op == '*':
                etq_loop = self._nueva_etiqueta('mul')
                etq_fin  = self._nueva_etiqueta('endmul')
                self._emit(Operacion.LOAD, 'R2', '0')
                self._emit(Operacion.MOVE, 'R3', 'R1')
                self._emit(Operacion.CMP, None, 'R3', '0', label=etq_loop)
                self._emit(Operacion.JZ, None, etq_fin)
                self._emit(Operacion.SUMA, 'R2', 'R2', 'R0')
                self._emit(Operacion.RESTA, 'R3', 'R3', '1')
                self._emit(Operacion.JMP, None, etq_loop)
                self._emit(Operacion.MOVE, reg, 'R2', label=etq_fin)
                return reg

            if nodo.op in ('==', '!=', '<', '>', '<=', '>='):
                self._emit(Operacion.CMP, None, 'R0', 'R1')
                self._emit_cmp_result(nodo.op, reg)
                return reg

        if isinstance(nodo, NodoCompareChain):
            if len(nodo.comparaciones) == 1:
                op, der = nodo.comparaciones[0]
                return self.compilar_expr(NodoBinOp(op, nodo.primero, der), reg)

            etq_false = self._nueva_etiqueta('cmpfalse')
            etq_fin   = self._nueva_etiqueta('cmpfin')
            self.compilar_expr(nodo.primero, 'R0')
            temp_prev = self._addr_temp()
            self._emit(Operacion.STORE, None, 'R0', str(temp_prev))

            for op, expr in nodo.comparaciones:
                self.compilar_expr(expr, 'R1')
                self._emit(Operacion.LOAD_M, 'R0', str(temp_prev))
                self._emit(Operacion.CMP, None, 'R0', 'R1')
                self._emit_cmp_fail_jump(op, etq_false)
                self._emit(Operacion.STORE, None, 'R1', str(temp_prev))

            self._emit(Operacion.LOAD, reg, '1')
            self._emit(Operacion.JMP, None, etq_fin)
            self._emit(Operacion.LOAD, reg, '0', label=etq_false)
            self._emit(Operacion.LOAD, reg, reg, label=etq_fin)
            return reg

        if isinstance(nodo, NodoLlamar):
            return self.compilar_llamada(nodo, reg)

        return reg

    # ── Compilar sentencias ──────────────────────────────────────────

    def compilar_stmt(self, nodo):

        if isinstance(nodo, NodoAsignar):
            if isinstance(nodo.expr, NodoLista):
                self._asignar_lista(
                    nodo.nombre,
                    nodo.expr,
                    declaracion=nodo.declaracion,
                )
                return
            if nodo.declaracion:
                array_scope = (self.array_scopes[0] if not self.in_function
                               else self._array_scope_actual())
                if nodo.nombre in array_scope:
                    raise SyntaxError(
                        f"'{nodo.nombre}' ya existe como arreglo")
            elif self._lookup_array(nodo.nombre) is not None:
                raise SyntaxError(
                    f"El arreglo '{nodo.nombre}' no puede recibir un escalar directo")
            self.compilar_expr(nodo.expr, 'R0')
            self._emit(Operacion.STORE, None, 'R0',
                       str(self._addr_escritura(
                           nodo.nombre,
                           declaracion=nodo.declaracion)))

        elif isinstance(nodo, NodoGlobalAsignar):
            if isinstance(nodo.expr, NodoLista):
                self._asignar_lista(
                    nodo.nombre,
                    nodo.expr,
                    global_explicito=True,
                )
                return
            self.compilar_expr(nodo.expr, 'R0')
            self._emit(Operacion.STORE, None, 'R0',
                       str(self._addr_global(nodo.nombre)))

        elif isinstance(nodo, NodoIndexAsignar):
            self.compilar_expr(nodo.expr, 'R0')
            self._emit_array_store(nodo.nombre, nodo.indice, 'R0')

        elif isinstance(nodo, NodoPrint):
            self.compilar_expr(nodo.expr, 'R0')
            self._emit(Operacion.PRINT, None, 'R0')

        elif isinstance(nodo, NodoIf):
            self.compilar_expr(nodo.condicion, 'R0')
            self._emit(Operacion.CMP, None, 'R0', '0')
            etq_sino = self._nueva_etiqueta('sino')
            etq_fin  = self._nueva_etiqueta('finif')
            self._emit(Operacion.JZ, None, etq_sino)
            self._compilar_bloque(nodo.cuerpo, scope_local=self.in_function)
            self._emit(Operacion.JMP, None, etq_fin)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_sino))
            self._compilar_bloque(nodo.sino, scope_local=self.in_function)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_fin))

        elif isinstance(nodo, NodoWhile):
            etq_inicio = self._nueva_etiqueta('loop')
            etq_fin    = self._nueva_etiqueta('endloop')
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_inicio))
            self.compilar_expr(nodo.condicion, 'R0')
            self._emit(Operacion.CMP, None, 'R0', '0')
            self._emit(Operacion.JZ,  None, etq_fin)
            self.loop_stack.append((etq_inicio, etq_fin))
            self._compilar_bloque(nodo.cuerpo, scope_local=self.in_function)
            self.loop_stack.pop()
            self._emit(Operacion.JMP, None, etq_inicio)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_fin))

        elif isinstance(nodo, NodoBreak):
            if not self.loop_stack:
                raise SyntaxError("break solo puede usarse dentro de un while")
            _, etq_fin = self.loop_stack[-1]
            self._emit(Operacion.JMP, None, etq_fin)

        elif isinstance(nodo, NodoContinue):
            if not self.loop_stack:
                raise SyntaxError(
                    "continue solo puede usarse dentro de un while")
            etq_inicio, _ = self.loop_stack[-1]
            self._emit(Operacion.JMP, None, etq_inicio)

        elif isinstance(nodo, NodoDef):
            self.funciones[nodo.nombre] = nodo
            etq_saltar = self._nueva_etiqueta('skipfn')
            self._emit(Operacion.JMP, None, etq_saltar)
            primera = True
            regs_args = ['R0', 'R1', 'R2', 'R3']
            self._push_scope()
            self.in_function = True
            self._registrar_parametros_arreglo_en_scope(nodo)

            reg_index = 0
            for i, param in enumerate(nodo.params[:4]):
                if i in self.function_array_param_slots.get(nodo.nombre, {}):
                    continue
                prev_len = len(self.codigo)
                self._emit(Operacion.STORE, None, regs_args[reg_index],
                           str(self._addr_escritura(param, declaracion=True)))
                if primera:
                    self.codigo[prev_len].label = nodo.nombre
                    primera = False
                reg_index += 1
            for s in nodo.cuerpo:
                prev_len = len(self.codigo)
                if isinstance(s, NodoReturn):
                    self.compilar_expr(s.expr, 'R3')
                    if primera:
                        self.codigo[prev_len].label = nodo.nombre
                        primera = False
                    self._emit(Operacion.RET)
                else:
                    self.compilar_stmt(s)
                    if primera and len(self.codigo) > prev_len:
                        self.codigo[prev_len].label = nodo.nombre
                        primera = False

            self._pop_scope()
            self.in_function = False
            self._emit(Operacion.RET)
            self.codigo.append(
                Instruccion(Operacion.LOAD, 'R3', '0',
                            label=etq_saltar))

        elif isinstance(nodo, NodoReturn):
            self.compilar_expr(nodo.expr, 'R3')
            self._emit(Operacion.RET)

        elif isinstance(nodo, NodoLlamar):
            self.compilar_llamada(nodo, 'R3')

    def compilar_llamada(self, nodo: NodoLlamar,
                          reg: str) -> str:
        if nodo.nombre in ('len', 'first', 'last'):
            return self.compilar_builtin(nodo, reg)

        param_arrays = self.function_array_param_slots.get(nodo.nombre, {})
        regs_args = ['R0', 'R1', 'R2', 'R3']
        reg_index = 0
        for i, arg in enumerate(nodo.args[:4]):
            if i in param_arrays:
                base, longitud = param_arrays[i]
                self._copiar_argumento_arreglo(arg, base, longitud)
                continue
            self.compilar_expr(arg, regs_args[reg_index])
            reg_index += 1
        self._emit(Operacion.CALL, None, nodo.nombre)
        if reg != 'R3':
            self._emit(Operacion.MOVE, reg, 'R3')
        return reg

    def compilar_builtin(self, nodo: NodoLlamar, reg: str) -> str:
        if len(nodo.args) != 1:
            raise SyntaxError(
                f"La builtin '{nodo.nombre}' espera exactamente 1 argumento")
        arg = nodo.args[0]

        if nodo.nombre == 'len':
            if isinstance(arg, NodoLista):
                self._emit(Operacion.LOAD, reg, str(len(arg.elementos) & 0xF))
                return reg
            if isinstance(arg, NodoID):
                info = self._lookup_array(arg.nombre)
                if info is None:
                    raise SyntaxError("len() espera un arreglo")
                _, longitud = info
                self._emit(Operacion.LOAD, reg, str(longitud & 0xF))
                return reg
            raise SyntaxError("len() espera un arreglo")

        if nodo.nombre == 'first':
            if isinstance(arg, NodoLista):
                if not arg.elementos:
                    raise SyntaxError("first() no acepta arreglos vacios")
                return self.compilar_expr(arg.elementos[0], reg)
            if isinstance(arg, NodoID):
                info = self._lookup_array(arg.nombre)
                if info is None:
                    raise SyntaxError("first() espera un arreglo")
                base, longitud = info
                if longitud == 0:
                    raise SyntaxError("first() no acepta arreglos vacios")
                self._emit(Operacion.LOAD_M, reg, str(base))
                return reg
            raise SyntaxError("first() espera un arreglo")

        if nodo.nombre == 'last':
            if isinstance(arg, NodoLista):
                if not arg.elementos:
                    raise SyntaxError("last() no acepta arreglos vacios")
                return self.compilar_expr(arg.elementos[-1], reg)
            if isinstance(arg, NodoID):
                info = self._lookup_array(arg.nombre)
                if info is None:
                    raise SyntaxError("last() espera un arreglo")
                base, longitud = info
                if longitud == 0:
                    raise SyntaxError("last() no acepta arreglos vacios")
                self._emit(Operacion.LOAD_M, reg, str(base + longitud - 1))
                return reg
            raise SyntaxError("last() espera un arreglo")

        raise SyntaxError(f"Builtin desconocida: {nodo.nombre}")

    def compilar(self, ast: list) -> List[Instruccion]:
        self._preanalizar_programa(ast)
        for nodo in ast:
            self.compilar_stmt(nodo)
        self._emit(Operacion.HALT)
        return self.codigo

    def mostrar_codigo(self):
        print("  CÓDIGO ENSAMBLADOR:")
        for i, ins in enumerate(self.codigo):
            etq = f"[{ins.label}]" if ins.label else "       "
            print(f"    {i:3d}: {etq:12s} {ins}")


# ── Interfaz principal ───────────────────────────────────────────────

def compile_and_run(fuente: str,
                    titulo: str = "Programa TIE-Lang",
                    verbose_asm: bool = True) -> dict:
    """
    Compila y ejecuta código TIE-Lang.

    Pipeline:
        fuente → Lexer → tokens → Parser → AST
               → Compilador → instrucciones → CPU

    Retorna dict con 'regs', 'Z', 'N', 'C', 'salida', 'ciclos'
    """
    print(f"\n{'═'*55}")
    print(f"  {titulo}")
    print(f"{'═'*55}")
    print("  CÓDIGO FUENTE:")
    for i, l in enumerate(fuente.strip().splitlines(), 1):
        print(f"    {i:2d}: {l}")

    lexer      = Lexer(fuente)
    parser     = Parser(lexer.tokens)
    ast        = parser.parse()
    compilador = Compilador()
    codigo     = compilador.compilar(ast)

    if verbose_asm:
        print()
        compilador.mostrar_codigo()

    print("\n  EJECUCIÓN:")
    cpu       = CPU()
    resultado = cpu.run(codigo, verbose=False)

    print(f"\n  Registros: {resultado['regs']}")
    ram = cpu.ram.dump()
    if ram:
        print(f"  RAM: {ram}")
    print(f"  Salida:  {resultado['salida']}")
    print(f"  Ciclos:  {resultado['ciclos']}")

    return resultado
