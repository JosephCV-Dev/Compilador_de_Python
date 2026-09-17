"""Rutas Flask de la aplicacion."""

from flask import Blueprint, jsonify, render_template, request

from lexer import tokenize
from token_stats import summarize_tokens

api_bp = Blueprint("api", __name__)


@api_bp.get("/")
def index():
    return render_template("index.html")


@api_bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.post("/api/lexer")
def run_lexer():
    if not request.is_json:
        return _invalid_request("Se requiere Content-Type: application/json.", 415)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _invalid_request("El cuerpo debe ser un objeto JSON valido.")
    if "source" not in data:
        return _invalid_request("Falta el campo source.")
    if not isinstance(data["source"], str):
        return _invalid_request("El campo source debe ser una cadena de texto.")

    result = tokenize(data["source"])
    result["statistics"] = summarize_tokens(result["tokens"])
    return jsonify(result)


def _invalid_request(message, status=400):
    return jsonify({
        "success": False,
        "tokens": [],
        "errors": [{"type": "INVALID_REQUEST", "message": message}],
    }), status
