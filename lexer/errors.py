"""Errores especificos del lexer."""

from models.diagnostics import Diagnostic


def build_lexical_error(character, line, column, position):
    return Diagnostic(
        type="LEXICAL_ERROR",
        message=f"Caracter no reconocido: {character}",
        lexeme=character,
        line=line,
        column=column,
        position=position,
        suggestion="Verifique si el caracter pertenece al subconjunto admitido.",
    )


def build_indentation_error(line, column, position, indent_level):
    return Diagnostic(
        type="INDENTATION_ERROR",
        message=f"Indentacion invalida: nivel {indent_level}",
        lexeme="",
        line=line,
        column=column,
        position=position,
        suggestion="Use un nivel de indentacion que coincida con un bloque abierto.",
    )
