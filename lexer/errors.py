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
