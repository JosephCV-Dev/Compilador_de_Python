"""Reglas tecnicas y descripciones naturales del subconjunto admitido.

El orden de reconocimiento vive en lexer.py: cadenas antes de numeros,
FLOAT antes de INTEGER y simbolos por longitud descendente.
"""

IDENTIFIER_PATTERN = r"[A-Za-z_][A-Za-z0-9_]*"
INTEGER_PATTERN = r"[0-9]+"
FLOAT_PATTERN = (
    r"(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    r"|[0-9]+[eE][+-]?[0-9]+"
)
STRING_PATTERN = r"""("[^"\\\r\n]*(?:\\[^\r\n][^"\\\r\n]*)*"|'[^'\\\r\n]*(?:\\[^\r\n][^'\\\r\n]*)*')"""
STRING_PREFIX_PATTERN = r"(?i:br|rb|fr|rf|r|u|b|f)(?=['\"])"
NEWLINE_PATTERN = r"\r\n|\r|\n"

IDENTIFIER_DESCRIPTION = (
    "Nombre que inicia con letra de A a Z o guion bajo, "
    "y continua con esas letras, digitos o guion bajo; admite mayusculas y minusculas."
)

INTEGER_DESCRIPTION = (
    "Secuencia de digitos decimales sin ceros iniciales, salvo que todos sean cero."
)

FLOAT_DESCRIPTION = (
    "Numero con punto decimal y digitos a uno o ambos lados, o con exponente "
    "introducido por e o E, signo opcional y digitos."
)

STRING_DESCRIPTION = (
    "Texto en una sola linea encerrado entre comillas simples o dobles; "
    "permite caracteres escapados con barra invertida."
)

KEYWORD_DESCRIPTION = "Palabra reservada exacta del lenguaje Python."

NEWLINE_DESCRIPTION = "Salto de linea que marca el fin de una linea logica."

INDENT_DESCRIPTION = "Aumento de indentacion que marca el inicio de un bloque."
DEDENT_DESCRIPTION = "Reduccion de indentacion que marca el cierre de un bloque."

OPERATOR_DESCRIPTIONS = {
    "EQ": "Operador de comparacion de igualdad.",
    "NE": "Operador de comparacion de diferencia.",
    "LE": "Operador de comparacion menor o igual.",
    "GE": "Operador de comparacion mayor o igual.",
    "POWER": "Operador aritmetico de potencia.",
    "FLOOR_DIV": "Operador aritmetico de division entera.",
    "PLUS_ASSIGN": "Operador de asignacion con suma.",
    "MINUS_ASSIGN": "Operador de asignacion con resta.",
    "STAR_ASSIGN": "Operador de asignacion con multiplicacion.",
    "SLASH_ASSIGN": "Operador de asignacion con division.",
    "PLUS": "Operador aritmetico de suma.",
    "MINUS": "Operador aritmetico de resta.",
    "STAR": "Operador aritmetico de multiplicacion.",
    "SLASH": "Operador aritmetico de division.",
    "MOD": "Operador aritmetico de modulo.",
    "ASSIGN": "Operador de asignacion simple.",
    "LT": "Operador de comparacion menor que.",
    "GT": "Operador de comparacion mayor que.",
    "POWER_ASSIGN": "Operador de asignacion con potencia.",
    "FLOOR_DIV_ASSIGN": "Operador de asignacion con division entera.",
    "MOD_ASSIGN": "Operador de asignacion con modulo.",
    "MATMUL_ASSIGN": "Operador de asignacion con multiplicacion matricial.",
    "BIT_AND_ASSIGN": "Operador de asignacion con conjuncion de bits.",
    "BIT_OR_ASSIGN": "Operador de asignacion con disyuncion de bits.",
    "BIT_XOR_ASSIGN": "Operador de asignacion con disyuncion exclusiva de bits.",
    "LSHIFT_ASSIGN": "Operador de asignacion con desplazamiento de bits a la izquierda.",
    "RSHIFT_ASSIGN": "Operador de asignacion con desplazamiento de bits a la derecha.",
    "LSHIFT": "Operador de desplazamiento de bits a la izquierda.",
    "RSHIFT": "Operador de desplazamiento de bits a la derecha.",
    "WALRUS": "Operador de asignacion dentro de una expresion.",
    "ARROW": "Simbolo que introduce la anotacion del tipo de retorno.",
    "MATMUL": "Simbolo de multiplicacion matricial o introduccion de decorador.",
    "BIT_AND": "Operador de conjuncion de bits.",
    "BIT_OR": "Operador de disyuncion de bits.",
    "BIT_XOR": "Operador de disyuncion exclusiva de bits.",
    "BIT_NOT": "Operador de inversion de bits.",
}

DELIMITER_DESCRIPTIONS = {
    "LPAREN": "Delimitador de apertura de parentesis.",
    "RPAREN": "Delimitador de cierre de parentesis.",
    "LBRACKET": "Delimitador de apertura de corchete.",
    "RBRACKET": "Delimitador de cierre de corchete.",
    "LBRACE": "Delimitador de apertura de llave.",
    "RBRACE": "Delimitador de cierre de llave.",
}

PUNCTUATION_DESCRIPTIONS = {
    "COMMA": "Signo de puntuacion usado para separar elementos.",
    "COLON": "Signo de puntuacion que introduce un bloque o separa partes de una expresion.",
    "DOT": "Punto usado en acceso a atributos o importaciones relativas.",
    "SEMICOLON": "Signo de puntuacion usado para separar instrucciones.",
    "ELLIPSIS": "Tres puntos consecutivos que representan el literal de elipsis.",
}
