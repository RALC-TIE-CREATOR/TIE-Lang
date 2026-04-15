"""
compiler/parser.py
------------------
Analizador sintáctico de TIE-Lang.
Convierte tokens en AST (Abstract Syntax Tree).

Gramática:
    programa    = sentencia*
    sentencia   = asignar | print | if | while | def | return | expr
    asignar     = ('let')? ID '=' expr
    expr        = comparacion
    comparacion = aritmetica (COMP aritmetica)?
    aritmetica  = unaria (('+' | '-' | '&' | '|' | '^') unaria)*
    unaria      = '~' primario | primario
    primario    = NUM | llamada | ID | '(' expr ')'
    llamada     = ID '(' args ')'
"""

from dataclasses import dataclass, field
from typing import List, Any
from .lexer import Token, TipoToken


# ── Nodos del AST ────────────────────────────────────────────────────

@dataclass
class NodoNum:
    valor: int

@dataclass
class NodoID:
    nombre: str

@dataclass
class NodoBinOp:
    op:  str
    izq: Any
    der: Any

@dataclass
class NodoUnOp:
    op:       str
    operando: Any

@dataclass
class NodoAsignar:
    nombre: str
    expr:   Any

@dataclass
class NodoIf:
    condicion: Any
    cuerpo:    List
    sino:      List = field(default_factory=list)

@dataclass
class NodoWhile:
    condicion: Any
    cuerpo:    List

@dataclass
class NodoDef:
    nombre: str
    params: List[str]
    cuerpo: List

@dataclass
class NodoLlamar:
    nombre: str
    args:   List

@dataclass
class NodoReturn:
    expr: Any

@dataclass
class NodoPrint:
    expr: Any


# ── Parser ───────────────────────────────────────────────────────────

class Parser:
    """
    Parser descendente recursivo para TIE-Lang.

    Uso:
        parser = Parser(tokens)
        ast    = parser.parse()
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos    = 0

    def actual(self) -> Token:
        return self.tokens[self.pos]

    def ver(self, offset: int = 1) -> Token:
        i = self.pos + offset
        return (self.tokens[i] if i < len(self.tokens)
                else Token(TipoToken.EOF, None))

    def consumir(self, tipo: TipoToken = None) -> Token:
        t = self.actual()
        if tipo and t.tipo != tipo:
            raise SyntaxError(
                f"Línea {t.linea}: esperaba {tipo.name}, "
                f"encontré {t.tipo.name} ({t.valor!r})")
        self.pos += 1
        return t

    def _skip_newlines(self):
        while self.actual().tipo == TipoToken.NEWLINE:
            self.consumir()

    # ── Expresiones ──────────────────────────────────────────────────

    def parse_expr(self) -> Any:
        return self.parse_comparacion()

    def parse_comparacion(self) -> Any:
        izq = self.parse_aritmetica()
        while self.actual().tipo == TipoToken.COMP:
            op  = self.consumir().valor
            der = self.parse_aritmetica()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_aritmetica(self) -> Any:
        izq = self.parse_unaria()
        while (self.actual().tipo == TipoToken.OP and
               self.actual().valor in '+-&|^'):
            op  = self.consumir().valor
            der = self.parse_unaria()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_unaria(self) -> Any:
        if (self.actual().tipo == TipoToken.OP and
                self.actual().valor == '~'):
            self.consumir()
            return NodoUnOp('~', self.parse_primario())
        return self.parse_primario()

    def parse_primario(self) -> Any:
        t = self.actual()
        if t.tipo == TipoToken.NUM:
            self.consumir()
            return NodoNum(t.valor)
        if t.tipo == TipoToken.ID:
            if self.ver().tipo == TipoToken.LPAREN:
                return self.parse_llamada()
            self.consumir()
            return NodoID(t.valor)
        if t.tipo == TipoToken.LPAREN:
            self.consumir()
            e = self.parse_expr()
            self.consumir(TipoToken.RPAREN)
            return e
        raise SyntaxError(
            f"Línea {t.linea}: expresión inesperada: {t.valor!r}")

    def parse_llamada(self) -> Any:
        nombre = self.consumir(TipoToken.ID).valor
        self.consumir(TipoToken.LPAREN)
        args = []
        while self.actual().tipo != TipoToken.RPAREN:
            args.append(self.parse_expr())
            if (self.actual().tipo == TipoToken.OP and
                    self.actual().valor == ','):
                self.consumir()
        self.consumir(TipoToken.RPAREN)
        return NodoLlamar(nombre, args)

    # ── Sentencias ───────────────────────────────────────────────────

    def parse_sentencia(self) -> Any:
        t = self.actual()

        if t.tipo == TipoToken.LET:
            self.consumir()
            nombre = self.consumir(TipoToken.ID).valor
            self.consumir(TipoToken.IGUAL)
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoAsignar(nombre, expr)

        if (t.tipo == TipoToken.ID and
                self.ver().tipo == TipoToken.IGUAL):
            nombre = self.consumir().valor
            self.consumir(TipoToken.IGUAL)
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoAsignar(nombre, expr)

        if t.tipo == TipoToken.PRINT:
            self.consumir()
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoPrint(expr)

        if t.tipo == TipoToken.IF:
            return self.parse_if()

        if t.tipo == TipoToken.WHILE:
            return self.parse_while()

        if t.tipo == TipoToken.DEF:
            return self.parse_def()

        if t.tipo == TipoToken.RETURN:
            self.consumir()
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoReturn(expr)

        expr = self.parse_expr()
        self._skip_newlines()
        return expr

    def parse_bloque(self) -> List:
        self.consumir(TipoToken.INDENT)
        stmts = []
        while self.actual().tipo not in (
                TipoToken.DEDENT, TipoToken.EOF):
            if self.actual().tipo == TipoToken.NEWLINE:
                self.consumir()
                continue
            stmts.append(self.parse_sentencia())
        if self.actual().tipo == TipoToken.DEDENT:
            self.consumir()
        return stmts

    def parse_if(self) -> NodoIf:
        self.consumir(TipoToken.IF)
        cond = self.parse_expr()
        self.consumir(TipoToken.COLON)
        self._skip_newlines()
        cuerpo = self.parse_bloque()
        sino = []
        if self.actual().tipo == TipoToken.ELSE:
            self.consumir()
            self.consumir(TipoToken.COLON)
            self._skip_newlines()
            sino = self.parse_bloque()
        return NodoIf(cond, cuerpo, sino)

    def parse_while(self) -> NodoWhile:
        self.consumir(TipoToken.WHILE)
        cond = self.parse_expr()
        self.consumir(TipoToken.COLON)
        self._skip_newlines()
        cuerpo = self.parse_bloque()
        return NodoWhile(cond, cuerpo)

    def parse_def(self) -> NodoDef:
        self.consumir(TipoToken.DEF)
        nombre = self.consumir(TipoToken.ID).valor
        self.consumir(TipoToken.LPAREN)
        params = []
        while self.actual().tipo != TipoToken.RPAREN:
            params.append(self.consumir(TipoToken.ID).valor)
            if (self.actual().tipo == TipoToken.OP and
                    self.actual().valor == ','):
                self.consumir()
        self.consumir(TipoToken.RPAREN)
        self.consumir(TipoToken.COLON)
        self._skip_newlines()
        cuerpo = self.parse_bloque()
        return NodoDef(nombre, params, cuerpo)

    def parse(self) -> List:
        stmts = []
        while self.actual().tipo != TipoToken.EOF:
            if self.actual().tipo in (
                    TipoToken.NEWLINE, TipoToken.DEDENT):
                self.consumir()
                continue
            stmts.append(self.parse_sentencia())
        return stmts
