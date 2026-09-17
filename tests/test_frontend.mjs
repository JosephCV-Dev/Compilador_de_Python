import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { afterEach, test } from "node:test";
import { fileURLToPath } from "node:url";

import { getTokenLabel } from "../static/js/token-labels.js";

const originalDocument = globalThis.document;
const originalFetch = globalThis.fetch;
const templateElements = JSON.parse(execFileSync(process.env.PYTHON || "python3", ["-c", `
import json
import sys
from html.parser import HTMLParser

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.elements.append(attrs)

parser = Elements()
parser.feed(sys.stdin.read())
print(json.dumps(parser.elements))
`], {
  input: readFileSync(new URL("../templates/index.html", import.meta.url), "utf8"),
  encoding: "utf8",
}));
let instance = 0;
const emptyStatistics = { total_tokens: 0, distinct_types: 0, by_type: [] };
const sampleStatistics = {
  total_tokens: 4,
  distinct_types: 3,
  by_type: [
    { type: "IDENTIFIER", count: 2, percentage: 50 },
    { type: "NEWLINE", count: 1, percentage: 25 },
    { type: "PLUS", count: 1, percentage: 25 },
  ],
};

afterEach(() => {
  globalThis.document = originalDocument;
  globalThis.fetch = originalFetch;
});

async function loadApp(fetchImplementation, missingIds = []) {
  const elements = new Map(templateElements
    .filter(attrs => !missingIds.includes(attrs.id))
    .map(attrs => [`#${attrs.id}`, {
      value: "x = 10",
      innerHTML: "",
      hidden: Object.hasOwn(attrs, "hidden"),
      addEventListener(event, handler) { this[event] = handler; },
    }]));
  globalThis.document = {
    querySelector(selector) {
      return elements.get(selector) ?? null;
    },
  };
  globalThis.fetch = fetchImplementation;
  await import(`../static/js/app.js?test=${instance++}`);
  return elements;
}

function response(body, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

test("la plantilla real contiene todos los elementos usados por la interfaz", async () => {
  const elements = await loadApp(async () => response({}));
  for (const id of ["file-input", "source-code", "analyze-button", "tokens-body", "errors-list",
                    "statistics-body", "statistics-footer", "statistics-total",
                    "statistics-types", "statistics-percentage"]) {
    assert.ok(elements.has(`#${id}`), `Falta #${id} en templates/index.html`);
  }
  assert.equal(document.querySelector("#inexistente"), null);
});

test("la ausencia de estadisticas no bloquea el boton ni el analisis", async () => {
  let requests = 0;
  const elements = await loadApp(async () => {
    requests++;
    return response({
      success: true, errors: [], statistics: sampleStatistics,
      tokens: [{ type: "IDENTIFIER", lexeme: "x", pattern: "Nombre" }],
    });
  }, ["statistics-footer"]);
  await elements.get("#analyze-button").click();
  assert.equal(requests, 1);
  assert.equal(elements.get("#analyze-button").disabled, false);
  assert.ok(elements.get("#tokens-body").innerHTML.includes("Identificador"));
});

test("un fallo al mostrar el estado inicial vuelve a habilitar el boton", async () => {
  let requests = 0;
  let failed = false;
  const elements = await loadApp(async () => { requests++; });
  Object.defineProperty(elements.get("#statistics-body"), "innerHTML", {
    set() {
      if (!failed) {
        failed = true;
        throw new Error("fallo de renderizado");
      }
    },
  });
  await elements.get("#analyze-button").click();
  assert.equal(requests, 0);
  assert.equal(elements.get("#analyze-button").disabled, false);
  assert.ok(elements.get("#errors-list").innerHTML.includes("No se pudo actualizar"));
});

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
    return response({ success: true, tokens, errors: [], statistics: {
      total_tokens: 4, distinct_types: 3, by_type: [
        { type: "NEWLINE", count: 2, percentage: 50 },
        { type: "INTEGER", count: 1, percentage: 25 },
        { type: "STRING", count: 1, percentage: 25 },
      ],
    } });
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
    statistics: emptyStatistics,
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
  globalThis.fetch = async () => response({ success: true, tokens: [], errors: [], statistics: emptyStatistics });
  await elements.get("#analyze-button").click();
  assert.ok(elements.get("#errors-list").innerHTML.includes("Sin diagnosticos"));
});

test("una respuesta JSON incompleta no se presenta como analisis exitoso", async () => {
  const elements = await loadApp(async () => response({}));
  await elements.get("#analyze-button").click();
  assert.ok(elements.get("#errors-list").innerHTML.includes("formato invalido"));
});

test("estadisticas muestran conteos, porcentajes y nombres en espanol", async () => {
  const elements = await loadApp(async () => response({
    success: true, tokens: [], errors: [], statistics: sampleStatistics,
  }));
  await elements.get("#analyze-button").click();
  const html = elements.get("#statistics-body").innerHTML;
  assert.ok(html.includes("Identificador"));
  assert.ok(html.includes("Salto de l\u00ednea"));
  assert.ok(html.includes("50.00 %"));
  assert.ok(html.includes("25.00 %"));
  assert.equal((html.match(/<tr>/g) || []).length, 3);
  assert.equal(String(elements.get("#statistics-total").textContent), "4");
  assert.equal(String(elements.get("#statistics-types").textContent), "3");
  assert.equal(elements.get("#statistics-footer").hidden, false);
});

test("un analisis vacio reemplaza los conteos anteriores por ceros", async () => {
  const elements = await loadApp(async () => response({
    success: true, tokens: [], errors: [], statistics: sampleStatistics,
  }));
  await elements.get("#analyze-button").click();
  globalThis.fetch = async () => response({
    success: true, tokens: [], errors: [], statistics: emptyStatistics,
  });
  await elements.get("#analyze-button").click();
  assert.equal(String(elements.get("#statistics-total").textContent), "0");
  assert.equal(String(elements.get("#statistics-types").textContent), "0");
  assert.equal(elements.get("#statistics-percentage").textContent, "0 %");
  assert.ok(elements.get("#statistics-body").innerHTML.includes("Sin tokens para contar"));
});

test("al cargar y fallar se retiran las estadisticas anteriores", async () => {
  const elements = await loadApp(async () => response({
    success: true, tokens: [], errors: [], statistics: sampleStatistics,
  }));
  await elements.get("#analyze-button").click();
  globalThis.fetch = async () => {
    assert.equal(elements.get("#statistics-footer").hidden, true);
    assert.ok(elements.get("#statistics-body").innerHTML.includes("Analizando"));
    throw new TypeError("network");
  };
  await elements.get("#analyze-button").click();
  assert.equal(elements.get("#statistics-footer").hidden, true);
  assert.ok(elements.get("#statistics-body").innerHTML.includes("no disponibles"));
  assert.ok(!elements.get("#statistics-body").innerHTML.includes("Identificador"));
});

test("errores HTTP no muestran un conteo de cero como analisis valido", async () => {
  const elements = await loadApp(async () => response({
    success: false, tokens: [], errors: [{ message: "Falta source." }],
  }, 400));
  await elements.get("#analyze-button").click();
  assert.equal(elements.get("#statistics-footer").hidden, true);
  assert.ok(elements.get("#statistics-body").innerHTML.includes("no disponibles"));
});

test("tipos nuevos en estadisticas se escapan antes de mostrar su etiqueta", async () => {
  const elements = await loadApp(async () => response({
    success: true, tokens: [], errors: [], statistics: {
      total_tokens: 1, distinct_types: 1,
      by_type: [{ type: "<nuevo>", count: 1, percentage: 100 }],
    },
  }));
  await elements.get("#analyze-button").click();
  assert.ok(elements.get("#statistics-body").innerHTML.includes("&lt;nuevo&gt;"));
});
