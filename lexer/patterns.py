"""Patrones base del lexer.

El orden de evaluacion debe documentarse junto al codigo porque `re`
elige la primera alternativa que coincide, no la coincidencia mas larga.
"""

IDENTIFIER_PATTERN = r"[A-Za-z_][A-Za-z0-9_]*"
INTEGER_PATTERN = r"[0-9]+"
FLOAT_PATTERN = r"[0-9]+\.[0-9]+"
STRING_PATTERN = r"""("[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')"""

PRIORITY_ORDER = [
    "WHITESPACE_AND_COMMENTS",
    "INDENTATION_AND_NEWLINE",
    "STRING",
    "FLOAT",
    "INTEGER",
    "IDENTIFIER_OR_KEYWORD",
    "MULTI_CHAR_OPERATOR",
    "SINGLE_CHAR_OPERATOR",
    "DELIMITER",
    "PUNCTUATION",
    "INVALID_CHARACTER",
]
