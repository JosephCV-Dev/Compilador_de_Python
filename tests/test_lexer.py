"""Contrato del lexer y regresiones de cadenas, posiciones y lineas logicas."""

import keyword
import re

import pytest

from lexer import tokenize
from lexer.tokens import KEYWORDS

def test_identifier_assignment_integer():
    result = tokenize("x = 10")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "ASSIGN", "INTEGER", "NEWLINE"]
    assert result["errors"] == []

def test_float():
    result = tokenize("precio = 10.5")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "ASSIGN", "FLOAT", "NEWLINE"]
    assert result["errors"] == []

def test_string():
    result = tokenize('mensaje = "hola"')
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "ASSIGN", "STRING", "NEWLINE"]
    assert result["errors"] == []

def test_keyword():
    result = tokenize("if x:")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IF", "IDENTIFIER", "COLON", "NEWLINE"]
    assert result["errors"] == []

def test_multi_character_operator():
    result = tokenize("x == y")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "EQ", "IDENTIFIER", "NEWLINE"]
    assert result["errors"] == []

def test_lexical_error():
    result = tokenize("x = $")
    token_types = [token["type"] for token in result["tokens"]]
    error = result["errors"][0]

    assert token_types == ["IDENTIFIER", "ASSIGN", "NEWLINE"]
    assert result["success"] is False
    assert error["type"] == "LEXICAL_ERROR"
    assert error["lexeme"] == "$"

def test_indentation_tokens():
    source = "if x:\n    y = 1\nz = 2"
    result = tokenize(source)
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == [
        "IF",
        "IDENTIFIER",
        "COLON",
        "NEWLINE",
        "INDENT",
        "IDENTIFIER",
        "ASSIGN",
        "INTEGER",
        "NEWLINE",
        "DEDENT",
        "IDENTIFIER",
        "ASSIGN",
        "INTEGER",
        "NEWLINE",
    ]
    assert result["errors"] == []

def test_invalid_indentation():
    source = "if x:\n    y = 1\n  z = 2"
    result = tokenize(source)
    error_types = [error["type"] for error in result["errors"]]

    assert result["success"] is False
    assert "INDENTATION_ERROR" in error_types


@pytest.mark.parametrize("source", ["", "   ", "# comentario", "\n\t# comentario\r\n\r"])
def test_empty_and_comment_only_input(source):
    assert tokenize(source) == {"success": True, "tokens": [], "errors": []}


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_blank_lines_preserve_indentation_and_positions(newline):
    source = newline.join([
        "if x:", "    y = 1", "", "  # comentario", "\t", "    z = 2", "w = 3", "",
    ])
    result = tokenize(source)
    assert result["success"]
    types = [t["type"] for t in result["tokens"]]
    assert types.count("INDENT") == types.count("DEDENT") == 1
    assert types.count("NEWLINE") == 4
    z = next(t for t in result["tokens"] if t["lexeme"] == "z")
    assert (z["line"], z["column"]) == (6, 5)
    dedent = next(t for t in result["tokens"] if t["type"] == "DEDENT")
    assert (dedent["line"], dedent["column"]) == (7, 1)


@pytest.mark.parametrize("source", [
    "x = 10\ny = 20",
    "if x:\r\n    y = .5\r\n\r\n    z = 1e3",
    "x = (\r  1 + 2\r)\r",
    "x = 1 + \\\r\n    2\n",
    'x = "hola"\n# comentario\n',
])
def test_token_spans_and_positions_match_original_source(source):
    result = tokenize(source)
    assert result["success"]
    previous_end = 0
    for token in result["tokens"]:
        assert set(token) == {"type", "lexeme", "pattern", "line", "column", "start", "end"}
        assert previous_end <= token["start"] <= token["end"] <= len(source)
        assert token["lexeme"] == source[token["start"]:token["end"]]
        prefix = source[:token["start"]]
        line_ends = list(re.finditer(r"\r\n|\r|\n", prefix))
        assert token["line"] == len(line_ends) + 1
        assert token["column"] == len(prefix) - (line_ends[-1].end() if line_ends else 0) + 1
        assert token["pattern"]
        previous_end = token["end"]


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_newline_lexeme_is_original_text(newline):
    token = tokenize("x = 1" + newline)["tokens"][-1]
    assert token == {
        "type": "NEWLINE", "lexeme": newline,
        "pattern": "Salto de linea que marca el fin de una linea logica.",
        "line": 1, "column": 6, "start": 5, "end": 5 + len(newline),
    }


def test_eof_closes_line_before_block():
    source = "if x:\n    y = 1"
    tokens = tokenize(source)["tokens"]
    assert [t["type"] for t in tokens[-2:]] == ["NEWLINE", "DEDENT"]
    for token in tokens[-2:]:
        assert token["lexeme"] == ""
        assert token["start"] == token["end"] == len(source)


@pytest.mark.parametrize("source", [
    "x = (\n    1 + 2\n)\n",
    "x = [\n    1,\n    # comentario\n\n    2,\n]\n",
    'x = {\n    "a": (\n        1 + 2\n    )\n}\n',
])
def test_implicit_continuation_does_not_create_blocks(source):
    result = tokenize(source)
    assert result["success"]
    types = [t["type"] for t in result["tokens"]]
    assert "INDENT" not in types and "DEDENT" not in types
    assert types.count("NEWLINE") == 1


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_explicit_continuation(newline):
    source = f"if x:{newline}    y = 1 + \\{newline}        2{newline}    z = 3"
    result = tokenize(source)
    assert result["success"]
    types = [t["type"] for t in result["tokens"]]
    assert types.count("NEWLINE") == 3
    assert types.count("INDENT") == types.count("DEDENT") == 1
    two = next(t for t in result["tokens"] if t["lexeme"] == "2")
    assert (two["line"], two["column"]) == (3, 9)


@pytest.mark.parametrize("source", ["x = 1\\", "x = 1\\\n", "x = 1\\ \n2", "x = 1\\# comentario\n2"])
def test_invalid_continuation(source):
    result = tokenize(source)
    assert not result["success"]
    assert result["errors"][0]["type"] == "LINE_CONTINUATION_ERROR"


@pytest.mark.parametrize("source", ["x = (1", "x = [1)", "x = 1)"])
def test_unmatched_delimiters(source):
    result = tokenize(source)
    assert not result["success"]
    assert any(e["type"] == "DELIMITER_ERROR" for e in result["errors"])


def test_tabs_in_indentation_report_once_and_advance():
    result = tokenize("if x:\n\t\ty = 1\nz = 2")
    assert not result["success"]
    assert len(result["errors"]) == 1
    assert result["errors"][0]["type"] == "INDENTATION_ERROR"
    assert any(t["lexeme"] == "z" and t["line"] == 3 for t in result["tokens"])


@pytest.mark.parametrize("lexeme", ['"hola"', "'hola'", '""', r'"a\"b"', r'"a\nb"', '"# comentario"'])
def test_strings_preserve_lexemes(lexeme):
    result = tokenize("x = " + lexeme)
    assert result["success"]
    token = result["tokens"][2]
    assert token["type"] == "STRING"
    assert token["lexeme"] == lexeme


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("ending", ["", "\\"])
def test_unterminated_string_recovers_at_next_line(newline, ending):
    source = 'x = "hola' + ending + newline + 'y = 1'
    result = tokenize(source)
    assert not result["success"]
    error = result["errors"][0]
    assert (error["type"], error["line"], error["column"], error["position"]) == (
        "UNTERMINATED_STRING", 1, 5, 4,
    )
    assert not any(t["type"] == "STRING" for t in result["tokens"])
    y = next(t for t in result["tokens"] if t["lexeme"] == "y")
    assert (y["line"], y["column"]) == (2, 1)


def test_unterminated_string_at_eof():
    result = tokenize('x = "hola')
    assert not result["success"]
    assert result["errors"][0]["lexeme"] == '"hola'


@pytest.mark.parametrize("lexeme", ['r"hola"', 'f"{nombre}"', 'b"hola"', 'RF"hola"', '"""hola\r\nmundo"""'])
def test_unsupported_strings_are_not_misclassified(lexeme):
    result = tokenize(lexeme + "\ny = 1")
    assert not result["success"]
    assert len(result["errors"]) == 1
    assert result["errors"][0]["type"] == "UNSUPPORTED_STRING"
    assert result["errors"][0]["lexeme"] == lexeme
    y = next(t for t in result["tokens"] if t["lexeme"] == "y")
    assert y["line"] == 2 + lexeme.count("\n")


@pytest.mark.parametrize("lexeme, expected", [
    ("0", "INTEGER"), ("00", "INTEGER"), ("123", "INTEGER"),
    (".5", "FLOAT"), ("1.", "FLOAT"), ("10.5", "FLOAT"),
    ("1e3", "FLOAT"), ("2E-3", "FLOAT"), (".5e+2", "FLOAT"), ("1.e2", "FLOAT"),
])
def test_numeric_forms(lexeme, expected):
    result = tokenize(lexeme)
    assert result["success"]
    assert [(t["type"], t["lexeme"]) for t in result["tokens"]] == [(expected, lexeme), ("NEWLINE", "")]


@pytest.mark.parametrize("lexeme", ["012", "1e", "1e+", "1.2e-", "123abc", "0xff", "0b10", "0o77", "1_000", "2j"])
def test_invalid_or_unsupported_numbers(lexeme):
    result = tokenize(lexeme + "\ny = 1")
    assert not result["success"]
    assert result["errors"][0]["type"] == "INVALID_NUMBER"
    assert result["errors"][0]["lexeme"] == lexeme
    assert not any(t["type"] == "IDENTIFIER" and t["lexeme"] != "y" for t in result["tokens"])


def test_reserved_keyword_catalog_is_complete():
    assert set(KEYWORDS) == set(keyword.kwlist)
    result = tokenize("break continue is pass try except finally with yield")
    assert [t["type"] for t in result["tokens"]] == [
        "BREAK", "CONTINUE", "IS", "PASS", "TRY", "EXCEPT", "FINALLY", "WITH", "YIELD", "NEWLINE",
    ]


def test_builtin_and_contextual_names_remain_identifiers():
    tokens = tokenize("print len range match case type _ ifx")["tokens"]
    assert all(t["type"] == "IDENTIFIER" for t in tokens[:-1])


@pytest.mark.parametrize("lexeme, expected", [
    ("**=", "POWER_ASSIGN"), ("//=", "FLOOR_DIV_ASSIGN"),
    ("<<=", "LSHIFT_ASSIGN"), (">>=", "RSHIFT_ASSIGN"),
    (":=", "WALRUS"), ("->", "ARROW"), ("...", "ELLIPSIS"), ("@", "MATMUL"),
])
def test_longest_symbol_match(lexeme, expected):
    result = tokenize(lexeme)
    assert result["success"]
    assert [(t["type"], t["lexeme"]) for t in result["tokens"]] == [(expected, lexeme), ("NEWLINE", "")]


@pytest.mark.parametrize("source", [None, 123, [], {}])
def test_direct_call_requires_text(source):
    with pytest.raises(TypeError, match="source"):
        tokenize(source)


def test_original_addition_example():
    source = """# Suma directa

print(5 + 3)  # Resultado: 8

# Suma usando variables

numero1 = 10
numero2 = 20
resultado = numero1 + numero2

print(resultado)  # Resultado: 30
"""
    result = tokenize(source)
    assert result["success"]
    types = [t["type"] for t in result["tokens"]]
    assert types.count("NEWLINE") == 5
    assert "INDENT" not in types and "DEDENT" not in types
    assert all(t["type"] == "IDENTIFIER" for t in result["tokens"] if t["lexeme"] == "print")
    assert result["tokens"][0]["lexeme"] == "print"
