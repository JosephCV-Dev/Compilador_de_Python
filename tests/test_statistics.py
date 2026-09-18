"""Estadisticas sobre tokens reconocidos, sin depender del motor del lexer."""

from copy import deepcopy

from token_stats import summarize_tokens


def test_empty_tokens():
    assert summarize_tokens([]) == {
        "total_tokens": 0, "distinct_types": 0, "by_type": [],
    }


def test_repeated_types_are_counted_and_sorted_by_frequency():
    tokens = [{"type": kind} for kind in ["IDENTIFIER", "PLUS", "IDENTIFIER", "NEWLINE"]]
    assert summarize_tokens(tokens) == {
        "total_tokens": 4,
        "distinct_types": 3,
        "by_type": [
            {"type": "IDENTIFIER", "count": 2, "percentage": 50.0},
            {"type": "NEWLINE", "count": 1, "percentage": 25.0},
            {"type": "PLUS", "count": 1, "percentage": 25.0},
        ],
    }


def test_structural_tokens_and_future_types_are_included():
    kinds = ["INDENT", "NEWLINE", "NEWLINE", "DEDENT", "FUTURE_TOKEN"]
    result = summarize_tokens([{"type": kind, "lexeme": ""} for kind in kinds])
    assert result["total_tokens"] == 5
    assert result["distinct_types"] == 4
    assert sum(entry["count"] for entry in result["by_type"]) == 5
    assert {entry["type"] for entry in result["by_type"]} == set(kinds)


def test_percentages_round_to_two_decimals():
    result = summarize_tokens([{"type": "A"}, {"type": "B"}, {"type": "B"}])
    assert [entry["percentage"] for entry in result["by_type"]] == [66.67, 33.33]


def test_does_not_mutate_input_or_accumulate_between_analyses():
    tokens = [{"type": "IDENTIFIER", "lexeme": "nombre", "line": 1}]
    original = deepcopy(tokens)
    first = summarize_tokens(tokens)
    second = summarize_tokens(tokens)
    assert tokens == original
    assert first == second
    assert first["by_type"] == [{"type": "IDENTIFIER", "count": 1, "percentage": 100.0}]
    assert summarize_tokens([])["total_tokens"] == 0
