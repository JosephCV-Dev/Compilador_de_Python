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

  try {
    const response = await fetch("/api/lexer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ source: sourceCode.value }),
    });
    const result = await response.json();
    renderTokens(result.tokens || []);
    renderErrors(result.errors || []);
  } catch (error) {
    renderTokens([]);
    renderErrors([
      {
        message: "No se pudo conectar con la API.",
        line: 1,
        column: 1,
      },
    ]);
  } finally {
    analyzeButton.disabled = false;
  }
});

function renderTokens(tokens) {
  if (tokens.length === 0) {
    tokensBody.innerHTML = '<tr><td colspan="6">Sin tokens para mostrar.</td></tr>';
    return;
  }

  tokensBody.innerHTML = tokens
    .map(
      (token, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(token.type)}</td>
          <td>${escapeHtml(token.lexeme)}</td>
          <td>${escapeHtml(token.pattern)}</td>
          <td>${token.line}</td>
          <td>${token.column}</td>
        </tr>
      `,
    )
    .join("");
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
          <span>Linea ${error.line}, columna ${error.column}</span>
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
