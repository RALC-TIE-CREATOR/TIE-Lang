"""
compiler/parser.py
------------------
Analizador sintáctico de TIE-Lang.
Convierte tokens en AST (Abstract Syntax Tree).

Gramática:
    programa    = sentencia*
    sentencia   = asignar | print | if | while | break | continue | def | return | expr
    asignar     = ('let')? ID '=' expr | ID '[' expr ']' '=' expr
    expr        = disyuncion
    disyuncion  = conjuncion ('or' conjuncion)*
    conjuncion  = comparacion ('and' comparacion)*
    comparacion = aritmetica (COMP aritmetica)?
    aritmetica  = termino (('+' | '-' | '&' | '|' | '^') termino)*
    termino     = unaria ('*' unaria)*
    unaria      = ('~' | 'not') primario | primario
    primario    = NUM | SYMBOL | lista | llamada | index | ID | '(' expr ')'
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
class NodoBool:
    valor: bool

@dataclass
class NodoID:
    nombre: str

@dataclass
class NodoSymbol:
    nombre: str

@dataclass
class NodoLista:
    elementos: List[Any]

@dataclass
class NodoIndex:
    nombre: str
    indice: Any

@dataclass
class NodoBinOp:
    op:  str
    izq: Any
    der: Any

@dataclass
class NodoCompareChain:
    primero: Any
    comparaciones: List[tuple[str, Any]]

@dataclass
class NodoUnOp:
    op:       str
    operando: Any

@dataclass
class NodoAsignar:
    nombre: str
    expr:   Any
    declaracion: bool = False

@dataclass
class NodoGlobalAsignar:
    nombre: str
    expr:   Any

@dataclass
class NodoIndexAsignar:
    nombre: str
    indice: Any
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

@dataclass
class NodoBreak:
    pass

@dataclass
class NodoContinue:
    pass


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

    def _is_index_assignment(self) -> bool:
        if self.actual().tipo != TipoToken.ID:
            return False
        if self.ver().tipo != TipoToken.LBRACKET:
            return False

        pos = self.pos + 1
        depth = 0
        while pos < len(self.tokens):
            tok = self.tokens[pos]
            if tok.tipo == TipoToken.LBRACKET:
                depth += 1
            elif tok.tipo == TipoToken.RBRACKET:
                depth -= 1
                if depth == 0:
                    siguiente = (self.tokens[pos + 1]
                                 if pos + 1 < len(self.tokens)
                                 else Token(TipoToken.EOF, None))
                    return siguiente.tipo == TipoToken.IGUAL
            pos += 1
        return False

    # ── Expresiones ──────────────────────────────────────────────────

    def parse_expr(self) -> Any:
        return self.parse_disyuncion()

    def parse_disyuncion(self) -> Any:
        izq = self.parse_conjuncion()
        while self.actual().tipo == TipoToken.OR_KW:
            self.consumir()
            der = self.parse_conjuncion()
            izq = NodoBinOp('or', izq, der)
        return izq

    def parse_conjuncion(self) -> Any:
        izq = self.parse_comparacion()
        while self.actual().tipo == TipoToken.AND:
            self.consumir()
            der = self.parse_comparacion()
            izq = NodoBinOp('and', izq, der)
        return izq

    def parse_comparacion(self) -> Any:
        izq = self.parse_aritmetica()
        comparaciones = []
        while self.actual().tipo == TipoToken.COMP:
            op  = self.consumir().valor
            der = self.parse_aritmetica()
            comparaciones.append((op, der))
        if not comparaciones:
            return izq
        return NodoCompareChain(izq, comparaciones)

    def parse_aritmetica(self) -> Any:
        izq = self.parse_termino()
        while (self.actual().tipo == TipoToken.OP and
               self.actual().valor in '+-&|^'):
            op  = self.consumir().valor
            der = self.parse_termino()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_termino(self) -> Any:
        izq = self.parse_unaria()
        while (self.actual().tipo == TipoToken.OP and
               self.actual().valor == '*'):
            op  = self.consumir().valor
            der = self.parse_unaria()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_unaria(self) -> Any:
        if (self.actual().tipo == TipoToken.OP and
                self.actual().valor == '~'):
            self.consumir()
            return NodoUnOp('~', self.parse_primario())
        if self.actual().tipo == TipoToken.NOT_KW:
            self.consumir()
            return NodoUnOp('not', self.parse_primario())
        return self.parse_primario()

    def parse_primario(self) -> Any:
        t = self.actual()
        if t.tipo == TipoToken.NUM:
            self.consumir()
            return NodoNum(t.valor)
        if t.tipo == TipoToken.TRUE:
            self.consumir()
            return NodoBool(True)
        if t.tipo == TipoToken.FALSE:
            self.consumir()
            return NodoBool(False)
        if t.tipo == TipoToken.SYMBOL:
            self.consumir()
            return NodoSymbol(t.valor)
        if t.tipo == TipoToken.LBRACKET:
            return self.parse_lista()
        if t.tipo == TipoToken.ID:
            if self.ver().tipo == TipoToken.LPAREN:
                return self.parse_llamada()
            if self.ver().tipo == TipoToken.LBRACKET:
                return self.parse_index()
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

    def parse_index(self) -> Any:
        nombre = self.consumir(TipoToken.ID).valor
        self.consumir(TipoToken.LBRACKET)
        indice = self.parse_expr()
        self.consumir(TipoToken.RBRACKET)
        return NodoIndex(nombre, indice)

    def parse_lista(self) -> Any:
        self.consumir(TipoToken.LBRACKET)
        elementos = []
        while self.actual().tipo != TipoToken.RBRACKET:
            elementos.append(self.parse_expr())
            if (self.actual().tipo == TipoToken.OP and
                    self.actual().valor == ','):
                self.consumir()
        self.consumir(TipoToken.RBRACKET)
        return NodoLista(elementos)

    # ── Sentencias ───────────────────────────────────────────────────

    def parse_sentencia(self) -> Any:
        t = self.actual()

        if t.tipo == TipoToken.LET:
            self.consumir()
            nombre = self.consumir(TipoToken.ID).valor
            self.consumir(TipoToken.IGUAL)
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoAsignar(nombre, expr, declaracion=True)

        if self._is_index_assignment():
            nombre = self.consumir(TipoToken.ID).valor
            self.consumir(TipoToken.LBRACKET)
            indice = self.parse_expr()
            self.consumir(TipoToken.RBRACKET)
            self.consumir(TipoToken.IGUAL)
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoIndexAsignar(nombre, indice, expr)

        if (t.tipo == TipoToken.ID and
                self.ver().tipo == TipoToken.IGUAL):
            nombre = self.consumir().valor
            self.consumir(TipoToken.IGUAL)
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoAsignar(nombre, expr, declaracion=False)

        if t.tipo == TipoToken.PRINT:
            self.consumir()
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoPrint(expr)

        if t.tipo == TipoToken.GLOBAL:
            self.consumir()
            nombre = self.consumir(TipoToken.ID).valor
            self.consumir(TipoToken.IGUAL)
            expr = self.parse_expr()
            self._skip_newlines()
            return NodoGlobalAsignar(nombre, expr)

        if t.tipo == TipoToken.IF:
            return self.parse_if()

        if t.tipo == TipoToken.WHILE:
            return self.parse_while()

        if t.tipo == TipoToken.BREAK:
            self.consumir()
            self._skip_newlines()
            return NodoBreak()

        if t.tipo == TipoToken.CONTINUE:
            self.consumir()
            self._skip_newlines()
            return NodoContinue()

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
        if self.actual().tipo == TipoToken.ELIF:
            sino = [self.parse_elif()]
        elif self.actual().tipo == TipoToken.ELSE:
            self.consumir()
            self.consumir(TipoToken.COLON)
            self._skip_newlines()
            sino = self.parse_bloque()
        return NodoIf(cond, cuerpo, sino)

    def parse_elif(self) -> NodoIf:
        self.consumir(TipoToken.ELIF)
        cond = self.parse_expr()
        self.consumir(TipoToken.COLON)
        self._skip_newlines()
        cuerpo = self.parse_bloque()
        sino = []
        if self.actual().tipo == TipoToken.ELIF:
            sino = [self.parse_elif()]
        elif self.actual().tipo == TipoToken.ELSE:
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
