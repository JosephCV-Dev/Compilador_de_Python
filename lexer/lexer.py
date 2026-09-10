"""Analizador lexico independiente de HTTP y de la interfaz web."""

import re

from lexer.patterns import (
    DEDENT_DESCRIPTION,
    DELIMITER_DESCRIPTIONS,
    FLOAT_DESCRIPTION,
    FLOAT_PATTERN,
    IDENTIFIER_DESCRIPTION,
    IDENTIFIER_PATTERN,
    INDENT_DESCRIPTION,
    INTEGER_DESCRIPTION,
    INTEGER_PATTERN,
    KEYWORD_DESCRIPTION,
    NEWLINE_DESCRIPTION,
    NEWLINE_PATTERN,
    OPERATOR_DESCRIPTIONS,
    PUNCTUATION_DESCRIPTIONS,
    STRING_DESCRIPTION,
    STRING_PATTERN,
    STRING_PREFIX_PATTERN,
)
from lexer.tokens import (
    DELIMITERS,
    DELIMITER_PAIRS,
    KEYWORDS,
    MULTI_CHAR_OPERATORS,
    PUNCTUATION,
    SINGLE_CHAR_OPERATORS,
)
from lexer.errors import (
    build_continuation_error,
    build_delimiter_error,
    build_indentation_error,
    build_lexical_error,
    build_number_error,
    build_string_error,
)
from models.token import Token

FLOAT_REGEX = re.compile(FLOAT_PATTERN)
INTEGER_REGEX = re.compile(INTEGER_PATTERN)
STRING_REGEX = re.compile(STRING_PATTERN)
IDENTIFIER_REGEX = re.compile(IDENTIFIER_PATTERN)
NEWLINE_REGEX = re.compile(NEWLINE_PATTERN)
STRING_PREFIX_REGEX = re.compile(STRING_PREFIX_PATTERN)
ORDERED_OPERATORS = sorted(MULTI_CHAR_OPERATORS.items(), key=lambda item: -len(item[0]))
ORDERED_PUNCTUATION = sorted(PUNCTUATION.items(), key=lambda item: -len(item[0]))


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


def _string_end(source, start, quote):
    """Busca el cierre para recuperar errores sin convertir su contenido en tokens."""
    i = start + len(quote)
    while i < len(source):
        if source.startswith(quote, i):
            return i + len(quote)
        if len(quote) == 1 and source[i] in "\r\n":
            return i
        if source[i] == "\\":
            if len(quote) == 1 and i + 1 < len(source) and source[i + 1] in "\r\n":
                return i + 1
            i += 2
        else:
            i += 1
    return len(source)


def _advance_position(text, line, column):
    parts = NEWLINE_REGEX.split(text)
    if len(parts) > 1:
        return line + len(parts) - 1, len(parts[-1]) + 1
    return line, column + len(text)


def tokenize(source):
    """Devuelve tokens y diagnosticos; success solo indica validez lexica."""
    if not isinstance(source, str):
        raise TypeError("source debe ser una cadena de texto")

    tokens = []
    errors = []
    i = 0
    line = 1
    column = 1
    at_line_start = True
    indent_stack = [0]
    delimiter_stack = []
    line_has_code = False
    pending_continuation = None

    while i < len(source):
        character = source[i]

        if at_line_start and not delimiter_stack:
            indent_start = i
            indent_column = column

            while i < len(source) and source[i] in " \t":
                i += 1
                column += 1

            if i >= len(source):
                break

            if source[i] not in "\r\n#":
                tab_offset = source.find("\t", indent_start, i)
                if tab_offset != -1:
                    errors.append(build_indentation_error(
                        line, indent_column + tab_offset - indent_start, tab_offset, "tab"
                    ))
                indent_level = i - indent_start

                if indent_level > indent_stack[-1]:
                    indent_stack.append(indent_level)
                    tokens.append(
                        build_token(
                            "INDENT",
                            source[indent_start:i],
                            INDENT_DESCRIPTION,
                            line,
                            indent_column,
                            indent_start,
                            i,
                        )
                    )
                elif indent_level < indent_stack[-1]:
                    while len(indent_stack) > 1 and indent_level < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(
                            build_token(
                                "DEDENT",
                                "",
                                DEDENT_DESCRIPTION,
                                line,
                                column,
                                i,
                                i,
                            )
                        )

                    if indent_level != indent_stack[-1]:
                        errors.append(
                            build_indentation_error(
                                line,
                                column,
                                i,
                                indent_level,
                            )
                        )

            at_line_start = False
            character = source[i]

        at_line_start = False
        if character in " \t":
            i += 1
            column += 1
            continue
        # Solo el fin de una linea logica produce NEWLINE.
        newline = NEWLINE_REGEX.match(source, i)
        if newline:
            if line_has_code and not delimiter_stack:
                tokens.append(
                    build_token(
                        "NEWLINE", newline.group(), NEWLINE_DESCRIPTION,
                        line, column, i, newline.end(),
                    )
                )
                line_has_code = False
            pending_continuation = None
            i = newline.end()
            line += 1
            column = 1
            at_line_start = True
            continue
        if character == "#":
            while i < len(source) and source[i] not in "\r\n":
                i += 1
                column += 1
            continue
        if character == "\\":
            newline = NEWLINE_REGEX.match(source, i + 1)
            if newline:
                pending_continuation = (line, column, i)
                i = newline.end()
                line += 1
                column = 1
            else:
                errors.append(build_continuation_error(line, column, i))
                i += 1
                column += 1
            continue

        pending_continuation = None
        line_has_code = True

        # Las formas no admitidas se consumen como un solo diagnostico.
        prefix = STRING_PREFIX_REGEX.match(source, i)
        quote_start = prefix.end() if prefix else i
        if source[quote_start] in "\"'":
            quote = source[quote_start]
            triple = source.startswith(quote * 3, quote_start)
            if prefix or triple:
                end = _string_end(source, quote_start, quote * 3 if triple else quote)
                lexeme = source[i:end]
                errors.append(build_string_error(lexeme, line, column, i, unsupported=True))
                line, column = _advance_position(lexeme, line, column)
                i = end
                continue

        match = STRING_REGEX.match(source, i)
        if match:
            lexeme = match.group()
            tokens.append(
                build_token(
                    "STRING",
                    lexeme,
                    STRING_DESCRIPTION,
                    line,
                    column,
                    i,
                    match.end(),
                )
            )
            column += len(lexeme)
            i = match.end()
            continue

        if character in "\"'":
            end = _string_end(source, i, character)
            lexeme = source[i:end]
            errors.append(build_string_error(lexeme, line, column, i))
            column += len(lexeme)
            i = end
            continue

        # FLOAT debe probarse antes que INTEGER para conservar el numero completo.
        match = FLOAT_REGEX.match(source, i)
        token_type, description = "FLOAT", FLOAT_DESCRIPTION
        if not match:
            match = INTEGER_REGEX.match(source, i)
            token_type, description = "INTEGER", INTEGER_DESCRIPTION
        if match:
            end = match.end()
            while end < len(source) and (source[end].isalnum() or source[end] == "_"):
                exponent = source[end] in "eE"
                end += 1
                if exponent and end < len(source) and source[end] in "+-":
                    end += 1
            lexeme = source[i:end]
            leading_zero = (
                token_type == "INTEGER" and lexeme.startswith("0")
                and any(digit != "0" for digit in lexeme)
            )
            if end != match.end() or leading_zero:
                errors.append(build_number_error(lexeme, line, column, i))
            else:
                tokens.append(
                    build_token(token_type, lexeme, description, line, column, i, end)
                )
            column += len(lexeme)
            i = end
            continue

        # Los nombres de funciones, incluidas las incorporadas, son identificadores.
        match = IDENTIFIER_REGEX.match(source, i)
        if match:
            lexeme = match.group()
            token_type = KEYWORDS.get(lexeme, "IDENTIFIER")
            pattern = KEYWORD_DESCRIPTION if token_type != "IDENTIFIER" else IDENTIFIER_DESCRIPTION

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
        for operator, token_type in ORDERED_OPERATORS:
            if source.startswith(operator, i):
                tokens.append(
                    build_token(
                        token_type,
                        operator,
                        OPERATOR_DESCRIPTIONS[token_type],
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
                    OPERATOR_DESCRIPTIONS[token_type],
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
            if character in DELIMITER_PAIRS:
                delimiter_stack.append((character, line, column, i))
            elif delimiter_stack and DELIMITER_PAIRS[delimiter_stack[-1][0]] == character:
                delimiter_stack.pop()
            else:
                errors.append(build_delimiter_error(character, line, column, i))
                if delimiter_stack:
                    delimiter_stack.pop()
            token_type = DELIMITERS[character]
            tokens.append(
                build_token(
                    token_type,
                    character,
                    DELIMITER_DESCRIPTIONS[token_type],
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
        found_punctuation = False
        for punctuation, token_type in ORDERED_PUNCTUATION:
            if source.startswith(punctuation, i):
                tokens.append(
                    build_token(
                        token_type, punctuation, PUNCTUATION_DESCRIPTIONS[token_type],
                        line, column, i, i + len(punctuation),
                    )
                )
                i += len(punctuation)
                column += len(punctuation)
                found_punctuation = True
                break
        if found_punctuation:
            continue

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

    if pending_continuation:
        errors.append(build_continuation_error(*pending_continuation))
    for delimiter in delimiter_stack:
        errors.append(build_delimiter_error(*delimiter))

    # El fin del archivo cierra la ultima linea logica aunque no tenga salto fisico.
    if line_has_code and not delimiter_stack:
        tokens.append(build_token("NEWLINE", "", NEWLINE_DESCRIPTION, line, column, i, i))

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(
            build_token(
                "DEDENT",
                "",
                DEDENT_DESCRIPTION,
                line,
                column,
                i,
                i,
            )
        )

    return {
        "success": len(errors) == 0,
        "tokens": [token.to_dict() for token in tokens],
        "errors": [error.to_dict() for error in errors],
    }
