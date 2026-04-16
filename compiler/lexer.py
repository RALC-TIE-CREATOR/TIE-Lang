"""
compiler/lexer.py
-----------------
Analizador léxico de TIE-Lang.
Convierte código fuente en tokens.

Maneja indentación estilo Python para bloques.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Any


class TipoToken(Enum):
    NUM     = auto()   # 42
    ID      = auto()   # nombre_variable
    LET     = auto()   # let
    IF      = auto()   # if
    ELSE    = auto()   # else
    WHILE   = auto()   # while
    DEF     = auto()   # def
    RETURN  = auto()   # return
    PRINT   = auto()   # print
    OP      = auto()   # + - & | ^ ~ ,
    COMP    = auto()   # == != < > <= >=
    IGUAL   = auto()   # =
    LPAREN  = auto()   # (
    RPAREN  = auto()   # )
    COLON   = auto()   # :
    NEWLINE = auto()
    INDENT  = auto()
    DEDENT  = auto()
    EOF     = auto()


PALABRAS_CLAVE = {
    'let':    TipoToken.LET,
    'if':     TipoToken.IF,
    'else':   TipoToken.ELSE,
    'while':  TipoToken.WHILE,
    'def':    TipoToken.DEF,
    'return': TipoToken.RETURN,
    'print':  TipoToken.PRINT,
}


@dataclass
class Token:
    tipo:  TipoToken
    valor: Any
    linea: int = 0

    def __repr__(self):
        return f"Token({self.tipo.name}, {self.valor!r})"


class Lexer:
    """
    Tokenizador para TIE-Lang.

    Uso:
        lexer  = Lexer(fuente)
        tokens = lexer.tokens
    """

    def __init__(self, fuente: str):
        self.fuente = fuente
        self.tokens: List[Token] = []
        self._tokenizar()

    def _tokenizar(self):
        pila_indent = [0]

        for nlinea, linea in enumerate(self.fuente.splitlines(), 1):
            stripped = linea.strip()
            if not stripped or stripped.startswith('#'):
                continue

            espacios = len(linea) - len(linea.lstrip())
            nivel    = pila_indent[-1]

            if espacios > nivel:
                pila_indent.append(espacios)
                self.tokens.append(
                    Token(TipoToken.INDENT, espacios, nlinea))
            while espacios < pila_indent[-1]:
                pila_indent.pop()
                self.tokens.append(
                    Token(TipoToken.DEDENT, espacios, nlinea))

            i = 0
            while i < len(stripped):
                c = stripped[i]

                if c == ' ':
                    i += 1
                    continue

                if c == '#':
                    break

                if c.isdigit():
                    j = i
                    while j < len(stripped) and stripped[j].isdigit():
                        j += 1
                    self.tokens.append(
                        Token(TipoToken.NUM, int(stripped[i:j]), nlinea))
                    i = j
                    continue

                if c.isalpha() or c == '_':
                    j = i
                    while j < len(stripped) and (
                            stripped[j].isalnum() or stripped[j] == '_'):
                        j += 1
                    palabra = stripped[i:j]
                    tipo = PALABRAS_CLAVE.get(palabra, TipoToken.ID)
                    self.tokens.append(Token(tipo, palabra, nlinea))
                    i = j
                    continue

                if (i + 1 < len(stripped) and
                        stripped[i:i+2] in ('==', '!=', '<=', '>=')):
                    self.tokens.append(
                        Token(TipoToken.COMP, stripped[i:i+2], nlinea))
                    i += 2
                    continue

                if c == '=' and (i + 1 >= len(stripped) or
                                  stripped[i+1] != '='):
                    self.tokens.append(
                        Token(TipoToken.IGUAL, '=', nlinea))
                    i += 1
                    continue

                if c in '<>':
                    self.tokens.append(
                        Token(TipoToken.COMP, c, nlinea))
                    i += 1
                    continue

                if c in '+-&|^~,':
                    self.tokens.append(
                        Token(TipoToken.OP, c, nlinea))
                    i += 1
                    continue

                mapa = {
                    '(': TipoToken.LPAREN,
                    ')': TipoToken.RPAREN,
                    ':': TipoToken.COLON,
                }
                if c in mapa:
                    self.tokens.append(Token(mapa[c], c, nlinea))
                    i += 1
                    continue

                i += 1

            self.tokens.append(Token(TipoToken.NEWLINE, '\n', nlinea))

        while self.tokens and self.tokens[-1].tipo == TipoToken.NEWLINE:
            self.tokens.pop()

        self.tokens.append(Token(TipoToken.EOF, None))
