import { getTokenLabel } from "./token-labels.js";

const fileInput = document.querySelector("#file-input");
const sourceCode = document.querySelector("#source-code");
const analyzeButton = document.querySelector("#analyze-button");
const tokensBody = document.querySelector("#tokens-body");
const errorsList = document.querySelector("#errors-list");

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) {
    return;
  }

  sourceCode.value = await file.text();
});

analyzeButton.addEventListener("click", async () => {
  analyzeButton.disabled = true;
  let failureMessage = "No se pudo conectar con la API.";

  try {
    const response = await fetch("/api/lexer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ source: sourceCode.value }),
    });
    failureMessage = response.ok
      ? "La API devolvio una respuesta con formato invalido."
      : `La API no pudo procesar la solicitud (HTTP ${response.status}).`;
    const result = await response.json();
    if (
      !result || typeof result.success !== "boolean" ||
      !Array.isArray(result.tokens) || !Array.isArray(result.errors)
    ) {
      throw new Error(failureMessage);
    }
    renderTokens(response.ok ? result.tokens : []);
    renderErrors(!response.ok && result.errors.length === 0
      ? [{ message: failureMessage }]
      : result.errors);
  } catch (error) {
    renderTokens([]);
    renderErrors([
      {
        message: failureMessage,
      },
    ]);
  } finally {
    analyzeButton.disabled = false;
  }
});

function renderTokens(tokens) {
  if (tokens.length === 0) {
    tokensBody.innerHTML = '<tr><td colspan="4">Sin tokens para mostrar.</td></tr>';
    return;
  }

  tokensBody.innerHTML = tokens
    .map(
      (token, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(getTokenLabel(token.type))}</td>
          <td>${escapeHtml(formatLexeme(token))}</td>
          <td>${escapeHtml(token.pattern)}</td>
        </tr>
      `,
    )
    .join("");
}

function formatLexeme(token) {
  if (token.type === "NEWLINE") {
    return token.lexeme.replaceAll("\r", "\\r").replaceAll("\n", "\\n");
  }
  return token.lexeme;
}

function renderErrors(errors) {
  if (errors.length === 0) {
    errorsList.innerHTML = "<li>Sin diagnosticos.</li>";
    return;
  }

  errorsList.innerHTML = errors
    .map(
      (error) => `
        <li>
          ${escapeHtml(error.message)}
          ${Number.isInteger(error.line) && Number.isInteger(error.column)
            ? `<span>Linea ${error.line}, columna ${error.column}</span>`
            : ""}
        </li>
      `,
    )
    .join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
