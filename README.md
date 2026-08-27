# Compilador de Python - Modulo lexer

Proyecto academico para construir, por etapas, una plataforma modular de compilador.
El primer modulo sera un analizador lexico propio para un subconjunto controlado de Python.

## Arquitectura

La carpeta actual funciona como la raiz del proyecto `compilador/` descrita en la propuesta.

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- api/
|-- lexer/  
|-- parser/    -- FUTURAMENTE --
|-- semantic/    -- FUTURAMENTE --
|-- intermediate/   -- FUTURAMENTE --
|-- codegen/    -- FUTURAMENTE --
|-- models/
|-- templates/
|-- static/
|-- tests/
`-- uploads/
```

## Responsabilidades

- `lexer/`: reglas, patrones y algoritmo del analizador lexico.
- `models/`: contratos de datos como `Token` y diagnosticos.
- `api/`: rutas Flask y serializacion de respuestas JSON.
- `templates/` y `static/`: interfaz web para cargar codigo y mostrar resultados.
- `parser/`, `semantic/`, `intermediate/`, `codegen/`: espacios reservados para futuras fases.
- `tests/`: pruebas unitarias del lexer y pruebas de integracion.
- `uploads/`: carpeta para archivos `.py` cargados durante pruebas manuales.

## Contrato esperado del lexer

```json
{
  "success": true,
  "tokens": [
    {
      "type": "IDENTIFIER",
      "lexeme": "nombre",
      "pattern": "[A-Za-z_][A-Za-z0-9_]*",
      "line": 1,
      "column": 1,
      "start": 0,
      "end": 6
    }
  ],
  "errors": []
}
```

## Siguiente paso

Implementar el lexer en incrementos pequenos:

1. Modelos `Token` y `LexicalError`.
2. Catalogo de tokens, patrones y orden de prioridad.
3. Funcion `tokenize(source)`.
4. Pruebas de identificadores, numeros, operadores, cadenas, indentacion y errores.
5. Endpoint `/api/lexer`.
6. Integracion con la interfaz.

#Añadimos a pedro novelo y emiliano medina