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
        suggestion=(
            "Use solo espacios para indentar."
            if indent_level == "tab"
            else "Use un nivel de indentacion que coincida con un bloque abierto."
        ),
    )


def build_string_error(lexeme, line, column, position, unsupported=False):
    return Diagnostic(
        type="UNSUPPORTED_STRING" if unsupported else "UNTERMINATED_STRING",
        message=(
            "Cadenas con prefijo o comillas triples fuera del subconjunto admitido."
            if unsupported
            else "Cadena sin cierre en la misma linea."
        ),
        lexeme=lexeme,
        line=line,
        column=column,
        position=position,
        suggestion="Use comillas simples o dobles, sin prefijo, en una sola linea.",
    )


def build_number_error(lexeme, line, column, position):
    return Diagnostic(
        type="INVALID_NUMBER",
        message=f"Numero mal formado o fuera del subconjunto admitido: {lexeme}",
        lexeme=lexeme,
        line=line,
        column=column,
        position=position,
        suggestion="Use numeros decimales sin guiones bajos; se admite exponente e o E.",
    )


def build_continuation_error(line, column, position):
    return Diagnostic(
        type="LINE_CONTINUATION_ERROR",
        message="Continuacion de linea invalida o incompleta.",
        lexeme="\\",
        line=line,
        column=column,
        position=position,
        suggestion="La barra debe ir justo antes del salto y continuar en otra linea.",
    )


def build_delimiter_error(lexeme, line, column, position):
    return Diagnostic(
        type="DELIMITER_ERROR",
        message=f"Delimitador sin pareja compatible: {lexeme}",
        lexeme=lexeme,
        line=line,
        column=column,
        position=position,
        suggestion="Revise la apertura y el cierre de parentesis, corchetes y llaves.",
    )
