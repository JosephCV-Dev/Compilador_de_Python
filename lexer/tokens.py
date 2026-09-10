"""Palabras reservadas y simbolos de Python 3.12; etiquetas visuales en static/."""

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
    "assert": "ASSERT",
    "async": "ASYNC",
    "await": "AWAIT",
    "break": "BREAK",
    "continue": "CONTINUE",
    "del": "DEL",
    "except": "EXCEPT",
    "finally": "FINALLY",
    "global": "GLOBAL",
    "is": "IS",
    "lambda": "LAMBDA",
    "nonlocal": "NONLOCAL",
    "pass": "PASS",
    "raise": "RAISE",
    "try": "TRY",
    "with": "WITH",
    "yield": "YIELD",
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
    "**=": "POWER_ASSIGN",
    "//=": "FLOOR_DIV_ASSIGN",
    "%=": "MOD_ASSIGN",
    "@=": "MATMUL_ASSIGN",
    "&=": "BIT_AND_ASSIGN",
    "|=": "BIT_OR_ASSIGN",
    "^=": "BIT_XOR_ASSIGN",
    "<<=": "LSHIFT_ASSIGN",
    ">>=": "RSHIFT_ASSIGN",
    "<<": "LSHIFT",
    ">>": "RSHIFT",
    ":=": "WALRUS",
    "->": "ARROW",
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
    "@": "MATMUL",
    "&": "BIT_AND",
    "|": "BIT_OR",
    "^": "BIT_XOR",
    "~": "BIT_NOT",
}


DELIMITERS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
}

DELIMITER_PAIRS = {"(": ")", "[": "]", "{": "}"}


PUNCTUATION = {
    ",": "COMMA",
    ":": "COLON",
    ".": "DOT",
    ";": "SEMICOLON",
    "...": "ELLIPSIS",
}
