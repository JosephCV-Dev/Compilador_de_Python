"""Punto de entrada del lexer.

La implementacion real se agregara en el siguiente incremento.
Debe recorrer el codigo fuente de izquierda a derecha y devolver
tokens + errores sin depender de Flask ni del navegador.
"""

import re
from lexer.patterns import (
    FLOAT_PATTERN,
    IDENTIFIER_PATTERN,
    INTEGER_PATTERN,
    STRING_PATTERN,
)
from lexer.tokens import(
    DELIMITERS,
    KEYWORDS,
    MULTI_CHAR_OPERATORS,
    PUNCTUATION,
    SINGLE_CHAR_OPERATORS
)
from lexer.errors import build_lexical_error
from models.token import Token

FLOAT_REGEX = re.compile(FLOAT_PATTERN)
INTEGER_REGEX = re.compile(INTEGER_PATTERN)
STRING_REGEX = re.compile(STRING_PATTERN)
IDENTIFIER_REGEX = re.compile(IDENTIFIER_PATTERN)

def build_token(token_type, lexeme, pattern, line, column, start, end):
    return Token(
        type=token_type,
        lexeme=lexeme,
        pattern=pattern,
        line=line,
        column=column,
        start=start,
        end=end,
    )


def tokenize(source):
    tokens = []
    errors = []
    i = 0
    line = 1
    column = 1
    while i < len(source):
        character = source[i]
        #Bloque de reconocimiento y omisión de espacios en blanco
        if character in " \t\r":
            i += 1
            column += 1
            continue
        #Bloque de reconocimiento de saltos de linea. Muy importante porque marca la pauta para filas
        if character == "\n":
            tokens.append(
                build_token(
                    "NEWLINE",
                    "\\n",
                    r"\n",
                    line,
                    column,
                    i,
                    i+1
                )
            )
            i += 1
            line += 1
            column = 1
            continue
        #Bloque para reconocer y omitir comentarios
        if character == "#":
            while i < len(source) and source[i] != "\n":
                i += 1
                column += 1
            continue
        #Bloque para detectar strigs
        match = STRING_REGEX.match(source, i)
        if match:
            lexeme = match.group()
            tokens.append(
                build_token(
                    "STRING",
                    lexeme,
                    STRING_PATTERN,
                    line,
                    column,
                    i,
                    match.end(),
                )
            )
            column += len(lexeme)
            i = match.end()
            continue
        #Bloque para detectar numero decimales (Importante antes que los enteros)
        match = FLOAT_REGEX.match(source, i)
        if match:
            lexeme = match.group()
            tokens.append(
                build_token(
                    "FLOAT",
                    lexeme,
                    FLOAT_PATTERN,
                    line,
                    column,
                    i,
                    match.end(),
                )
            )
            column += len(lexeme)
            i = match.end()
            continue
        #Bloque para reconocer números enteros
        match = INTEGER_REGEX.match(source, i)
        if match:
            lexeme = match.group()
            tokens.append(
                build_token(
                    "INTEGER",
                    lexeme,
                    INTEGER_PATTERN,
                    line,
                    column,
                    i,
                    match.end(),
                )
            )
            column += len(lexeme)
            i = match.end()
            continue
        #Bloque de reconocimiento de Identificadores(variables) y palabras reservadas
        match = IDENTIFIER_REGEX.match(source, i)
        if match:
            lexeme = match.group()
            token_type = KEYWORDS.get(lexeme, "IDENTIFIER")
            pattern = lexeme if token_type != "IDENTIFIER" else IDENTIFIER_PATTERN

            tokens.append(
                build_token(
                    token_type,
                    lexeme,
                    pattern,
                    line,
                    column,
                    i,
                    match.end(),
                )
            )
            column += len(lexeme)
            i = match.end()
            continue
        # Bloque para identificar operadores multi-caracter.
        found_operator = False
        for operator, token_type in MULTI_CHAR_OPERATORS.items():
            if source.startswith(operator, i):
                tokens.append(
                    build_token(
                        token_type,
                        operator,
                        operator,
                        line,
                        column,
                        i,
                        i + len(operator),
                    )
                )
                column += len(operator)
                i += len(operator)
                found_operator = True
                break
        if found_operator:
            continue
        # Bloque para identificar operadores sencillos de un caracter.
        if character in SINGLE_CHAR_OPERATORS:
            token_type = SINGLE_CHAR_OPERATORS[character]
            tokens.append(
                build_token(
                    token_type,
                    character,
                    character,
                    line,
                    column,
                    i,
                    i + 1,
                )
            )
            i += 1
            column += 1
            continue
        # Bloque para reconocer caracteres de delimitacion.
        if character in DELIMITERS:
            token_type = DELIMITERS[character]
            tokens.append(
                build_token(
                    token_type,
                    character,
                    character,
                    line,
                    column,
                    i,
                    i + 1,
                )
            )
            i += 1
            column += 1
            continue
        # Bloque para reconocer signos de puntuacion.
        if character in PUNCTUATION:
            token_type = PUNCTUATION[character]
            tokens.append(
                build_token(
                    token_type,
                    character,
                    character,
                    line,
                    column,
                    i,
                    i + 1,
                )
            )
            i += 1
            column += 1
            continue
        #Delimitados el compilador hasta este error
        errors.append(
            build_lexical_error(
                character,
                line,
                column,
                i,
            )
        )
        i += 1
        column += 1
    return {
        "success": len(errors) == 0,
        "tokens": [token.to_dict() for token in tokens],
        "errors": [error.to_dict() for error in errors],
    }