"""Catalogo inicial de tokens para el lexer."""

KEYWORDS = {
    "if",
    "else",
    "elif",
    "for",
    "while",
    "in",
    "def",
    "return",
    "class",
    "import",
    "from",
    "as",
    "True",
    "False",
    "None",
    "and",
    "or",
    "not",
}

MULTI_CHAR_OPERATORS = {
    "==": "EQ",
    "!=": "NE",
    "<=": "LE",
    ">=": "GE",
    "//": "FLOOR_DIV",
    "**": "POWER",
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

STRUCTURAL_TOKENS = {
    "NEWLINE",
    "INDENT",
    "DEDENT",
}
