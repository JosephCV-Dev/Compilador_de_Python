"""Catalogo inicial de tokens para el lexer."""

KEYWORDS = {
    "if": "IF",
    "else": "ELSE",
    "elif": "ELIF",
    "for": "FOR",
    "while": "WHILE",
    "in": "IN",
    "def": "DEF",
    "return": "RETURN",
    "class": "CLASS",
    "import": "IMPORT",
    "from": "FROM",
    "as": "AS",
    "True": "TRUE",
    "False": "FALSE",
    "None": "NONE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}


MULTI_CHAR_OPERATORS = {
    "==": "EQ",
    "!=": "NE",
    "<=": "LE",
    ">=": "GE",
    "**": "POWER",
    "//": "FLOOR_DIV",
    "+=": "PLUS_ASSIGN",
    "-=": "MINUS_ASSIGN",
    "*=": "STAR_ASSIGN",
    "/=": "SLASH_ASSIGN",
}


SINGLE_CHAR_OPERATORS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "%": "MOD",
    "=": "ASSIGN",
    "<": "LT",
    ">": "GT",
}


DELIMITERS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
}


PUNCTUATION = {
    ",": "COMMA",
    ":": "COLON",
    ".": "DOT",
    ";": "SEMICOLON",
}
