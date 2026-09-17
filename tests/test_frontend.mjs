import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { afterEach, test } from "node:test";
import { fileURLToPath } from "node:url";

import { getTokenLabel } from "../static/js/token-labels.js";

const originalDocument = globalThis.document;
const originalFetch = globalThis.fetch;
let instance = 0;

afterEach(() => {
  globalThis.document = originalDocument;
  globalThis.fetch = originalFetch;
});

async function loadApp(fetchImplementation) {
  const elements = new Map();
  globalThis.document = {
    querySelector(selector) {
      if (!elements.has(selector)) {
        elements.set(selector, {
          value: "x = 10",
          innerHTML: "",
          addEventListener(event, handler) { this[event] = handler; },
        });
      }
      return elements.get(selector);
    },
  };
  globalThis.fetch = fetchImplementation;
  await import(`../static/js/app.js?test=${instance++}`);
  return elements;
}

function response(body, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

test("todos los tipos del lexer tienen etiqueta visual", () => {
  const catalog = execFileSync(process.env.PYTHON || "python3", ["-c", `
import json
from lexer.tokens import KEYWORDS, MULTI_CHAR_OPERATORS, SINGLE_CHAR_OPERATORS, DELIMITERS, PUNCTUATION
kinds = {"IDENTIFIER", "INTEGER", "FLOAT", "STRING", "NEWLINE", "INDENT", "DEDENT"}
for catalog in (KEYWORDS, MULTI_CHAR_OPERATORS, SINGLE_CHAR_OPERATORS, DELIMITERS, PUNCTUATION):
    kinds.update(catalog.values())
print(json.dumps(sorted(kinds)))
`], { cwd: fileURLToPath(new URL("../", import.meta.url)), encoding: "utf8" });
  for (const kind of JSON.parse(catalog)) assert.notEqual(getTokenLabel(kind), kind);
  assert.equal(getTokenLabel("INTEGER"), "N\u00famero entero");
  assert.equal(getTokenLabel("FUTURE_TOKEN"), "FUTURE_TOKEN");
});

test("renderiza cuatro columnas, escapa HTML y conserva lexemas originales", async () => {
  const tokens = [
    { type: "INTEGER", lexeme: "10", pattern: "Numero" },
    { type: "STRING", lexeme: "<script>", pattern: "Texto" },
    { type: "NEWLINE", lexeme: "\r\n", pattern: "Fin de linea" },
    { type: "NEWLINE", lexeme: "", pattern: "Fin de linea" },
  ];
  const elements = await loadApp(async (url, options) => {
    assert.equal(url, "/api/lexer");
    assert.deepEqual(JSON.parse(options.body), { source: "x = 10" });
    return response({ success: true, tokens, errors: [] });
  });
  await elements.get("#analyze-button").click();
  const html = elements.get("#tokens-body").innerHTML;
  assert.ok(html.includes("N\u00famero entero"));
  assert.ok(html.includes("&lt;script&gt;"));
  assert.ok(html.includes("<td>\\r\\n</td>"));
  assert.equal((html.match(/<td>/g) || []).length, 16);
  assert.equal(tokens[2].lexeme, "\r\n");
  assert.equal(elements.get("#analyze-button").disabled, false);
});

test("errores lexicos conservan sus posiciones y escapan su mensaje", async () => {
  const elements = await loadApp(async () => response({
    success: false, tokens: [],
    errors: [{ message: "Error <texto>", line: 2, column: 5 }],
  }));
  await elements.get("#analyze-button").click();
  const html = elements.get("#errors-list").innerHTML;
  assert.ok(html.includes("Error &lt;texto&gt;"));
  assert.ok(html.includes("Linea 2, columna 5"));
  assert.ok(elements.get("#tokens-body").innerHTML.includes('colspan="4"'));
});

test("un error HTTP con JSON muestra el mensaje sin posiciones inventadas", async () => {
  const elements = await loadApp(async () => response({
    success: false, tokens: [], errors: [{ type: "INVALID_REQUEST", message: "Falta source." }],
  }, 400));
  await elements.get("#analyze-button").click();
  const html = elements.get("#errors-list").innerHTML;
  assert.ok(html.includes("Falta source."));
  assert.ok(!html.includes("Linea"));
  assert.equal(elements.get("#analyze-button").disabled, false);
});

test("una respuesta HTML de error se identifica por su estado HTTP", async () => {
  const elements = await loadApp(async () => ({
    ok: false, status: 500, json: async () => { throw new SyntaxError("HTML"); },
  }));
  await elements.get("#analyze-button").click();
  const html = elements.get("#errors-list").innerHTML;
  assert.ok(html.includes("HTTP 500"));
  assert.ok(!html.includes("No se pudo conectar"));
  assert.equal(elements.get("#analyze-button").disabled, false);
});

test("un fallo de red permite volver a analizar", async () => {
  const elements = await loadApp(async () => { throw new TypeError("network"); });
  await elements.get("#analyze-button").click();
  assert.ok(elements.get("#errors-list").innerHTML.includes("No se pudo conectar"));
  assert.equal(elements.get("#analyze-button").disabled, false);
  globalThis.fetch = async () => response({ success: true, tokens: [], errors: [] });
  await elements.get("#analyze-button").click();
  assert.ok(elements.get("#errors-list").innerHTML.includes("Sin diagnosticos"));
});

test("una respuesta JSON incompleta no se presenta como analisis exitoso", async () => {
  const elements = await loadApp(async () => response({}));
  await elements.get("#analyze-button").click();
  assert.ok(elements.get("#errors-list").innerHTML.includes("formato invalido"));
});
