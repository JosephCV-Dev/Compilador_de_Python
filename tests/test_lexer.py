"""Pruebas del lexer.

Estas pruebas se completaran cuando se implemente `lexer.tokenize`.
"""

from lexer.lexer import tokenize
def test_identifier_assignment_integer():
    result = tokenize("x = 10")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "ASSIGN", "INTEGER"]
    assert result["errors"] == []

def test_float():
    result = tokenize("precio = 10.5")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "ASSIGN", "FLOAT"]
    assert result["errors"] == []

def test_string():
    result = tokenize('mensaje = "hola"')
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "ASSIGN", "STRING"]
    assert result["errors"] == []

def test_keyword():
    result = tokenize("if x:")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IF", "IDENTIFIER", "COLON"]
    assert result["errors"] == []

def test_multi_character_operator():
    result = tokenize("x == y")
    token_types = [token["type"] for token in result["tokens"]]

    assert token_types == ["IDENTIFIER", "EQ", "IDENTIFIER"]
    assert result["errors"] == []

def test_lexical_error():
    result = tokenize("x = @")
    token_types = [token["type"] for token in result["tokens"]]
    error = result["errors"][0]

    assert token_types == ["IDENTIFIER", "ASSIGN"]
    assert result["success"] is False
    assert error["type"] == "LEXICAL_ERROR"
    assert error["lexeme"] == "@"

