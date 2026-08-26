"""Rutas Flask de la aplicacion."""

from flask import Blueprint, jsonify, render_template, request

from lexer import tokenize

api_bp = Blueprint("api", __name__)


@api_bp.get("/")
def index():
    return render_template("index.html")


@api_bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.post("/api/lexer")
def run_lexer():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "")

    try:
        result = tokenize(source)
    except NotImplementedError as exc:
        return (
            jsonify(
                {
                    "success": False,
                    "tokens": [],
                    "errors": [
                        {
                            "type": "NOT_IMPLEMENTED",
                            "message": str(exc),
                            "lexeme": "",
                            "line": 1,
                            "column": 1,
                            "position": 0,
                            "suggestion": "Implementar lexer.tokenize(source).",
                        }
                    ],
                }
            ),
            501,
        )

    return jsonify(result)
