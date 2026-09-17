"""Validacion HTTP y contrato entre la API y el lexer."""

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize("body", ["null", "[]", "[1]", "false", "123", '"texto"', "{", "{}",
                                       '{"source": null}', '{"source": 123}', '{"source": []}'])
def test_invalid_request_returns_json_400(client, body):
    response = client.post("/api/lexer", data=body, content_type="application/json")
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["tokens"] == []
    error = response.json["errors"][0]
    assert error["type"] == "INVALID_REQUEST"
    assert "line" not in error and "column" not in error


def test_wrong_content_type(client):
    response = client.post("/api/lexer", data="x = 1", content_type="text/plain")
    assert response.status_code == 415
    assert response.json["errors"][0]["type"] == "INVALID_REQUEST"


def test_empty_source_is_valid(client):
    response = client.post("/api/lexer", json={"source": ""})
    assert response.status_code == 200
    assert response.json == {
        "success": True, "tokens": [], "errors": [],
        "statistics": {"total_tokens": 0, "distinct_types": 0, "by_type": []},
    }


def test_success_keeps_internal_types_descriptions_and_raw_lexemes(client):
    response = client.post("/api/lexer", json={"source": "x = 10\r\n"})
    assert response.status_code == 200
    tokens = response.json["tokens"]
    assert [t["type"] for t in tokens] == ["IDENTIFIER", "ASSIGN", "INTEGER", "NEWLINE"]
    assert tokens[2]["lexeme"] == "10"
    assert "digitos" in tokens[2]["pattern"]
    assert tokens[-1]["lexeme"] == "\r\n"
    assert (tokens[2]["line"], tokens[2]["column"]) == (1, 5)


def test_lexical_errors_are_analysis_results_not_http_errors(client):
    response = client.post("/api/lexer", json={"source": "x = $"})
    assert response.status_code == 200
    assert response.json["success"] is False
    assert response.json["errors"][0]["type"] == "LEXICAL_ERROR"


def test_page_and_static_modules(client):
    page = client.get("/")
    assert page.status_code == 200
    assert b'type="module"' in page.data
    assert page.data.count(b"<th>") == 4
    assert page.data.index(b'id="tokens-body"') < page.data.index(b'id="statistics-title"')
    assert b'class="diagnostics-panel" aria-labelledby="errors-title" hidden' in page.data
    for path in ("/static/js/app.js", "/static/js/token-labels.js", "/static/css/style.css"):
        assert client.get(path).status_code == 200


def test_statistics_count_the_tokens_in_the_same_response(client):
    result = client.post("/api/lexer", json={"source": "x + x"}).json
    assert result["statistics"] == {
        "total_tokens": 4,
        "distinct_types": 3,
        "by_type": [
            {"type": "IDENTIFIER", "count": 2, "percentage": 50.0},
            {"type": "NEWLINE", "count": 1, "percentage": 25.0},
            {"type": "PLUS", "count": 1, "percentage": 25.0},
        ],
    }
    assert result["statistics"]["total_tokens"] == len(result["tokens"])


def test_statistics_are_available_for_tokens_recovered_from_invalid_source(client):
    result = client.post("/api/lexer", json={"source": "x = $"}).json
    assert result["success"] is False
    assert result["statistics"]["total_tokens"] == len(result["tokens"]) == 3
    assert sum(row["count"] for row in result["statistics"]["by_type"]) == 3
    assert not any(row["type"] == "LEXICAL_ERROR" for row in result["statistics"]["by_type"])


def test_invalid_request_has_no_statistics(client):
    response = client.post("/api/lexer", json={"source": 123})
    assert response.status_code == 400
    assert "statistics" not in response.json
