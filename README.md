# Compilador de Python - Modulo lexer

Proyecto academico para construir, por etapas, una plataforma modular de compilador.
El primer modulo es un analizador lexico propio para un subconjunto controlado de Python 3.12.
Reconoce tokens y errores lexicos; no ejecuta el programa ni valida su sintaxis o semantica.

## Arquitectura

La carpeta actual funciona como la raiz del proyecto `compilador/` descrita en la propuesta.

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- api/
|-- lexer/
|-- models/
|-- templates/
|-- static/
|-- tests/
`-- uploads/
```

## Responsabilidades

- `lexer/tokens.py`: catalogo de palabras reservadas, operadores y delimitadores.
- `lexer/patterns.py`: expresiones regulares internas y descripciones en lenguaje natural.
- `lexer/lexer.py`: reconocimiento, posiciones, lineas logicas y pila de indentacion.
- `lexer/errors.py`: construccion de diagnosticos especificos del lexer.
- `lexer/__init__.py`: exporta `tokenize` como entrada publica del modulo.
- `models/`: contratos de datos como `Token` y diagnosticos.
- `api/`: validacion de solicitudes, rutas Flask y respuestas JSON.
- `templates/` y `static/`: interfaz web para cargar codigo y mostrar resultados.
- `static/js/token-labels.js`: traducciones visuales; no cambia los tipos internos.
- `tests/`: pruebas del lexer, la API y el renderizado JavaScript.
- `uploads/`: reserva sin uso actual. El navegador lee el archivo `.py` y envia su texto;
  el servidor no guarda archivos ni ejecuta su contenido.

Las fases parser, semantica y generacion de codigo son futuras; no necesitan carpetas vacias.
El lexer usa solamente la biblioteca estandar y los modelos, sin importar Flask ni la interfaz.
Por ahora su resultado es un diccionario serializable. Cualquier cambio a objetos compartidos
entre fases debera acordarse al introducir el parser, sin cambiar silenciosamente la API.

## Subconjunto admitido

- Identificadores ASCII: letras de A a Z, mayusculas o minusculas, guion bajo y digitos
  despues del primer caracter. `print`, `len` y otros nombres incorporados son identificadores.
- Las 35 palabras reservadas de Python 3.12. `match`, `case`, `_` y `type` se mantienen
  como identificadores; su significado contextual corresponde al futuro parser.
- Enteros decimales: `0`, `00`, `10`, `123`. Se rechazan ceros iniciales si hay otro digito,
  como `012`. El signo se emite como operador separado.
- Decimales y exponentes: `10.5`, `.5`, `1.`, `1e3`, `2E-3`, `.5e+2`.
- Cadenas en una sola linea con comillas simples o dobles y caracteres escapados.
  Se conserva el texto original; no se interpreta su valor ni se decodifican escapes.
- Operadores aritmeticos, comparaciones, asignaciones, operaciones de bits, `@`, `:=`,
  `->`, parentesis, corchetes, llaves y puntuacion, incluidos los tres puntos `...`.
- Comentarios con `#`, lineas vacias, saltos LF/CRLF/CR, bloques indentados con espacios,
  continuacion dentro de `()`, `[]`, `{}` y continuacion explicita con barra invertida.

Se diagnostican las cadenas sin cerrar, los delimitadores incompatibles, las continuaciones
incompletas, la indentacion inconsistente y los caracteres ajenos al subconjunto.
Las tabulaciones se admiten entre tokens y en continuaciones, pero no para indentar bloques.
Esta restriccion es del proyecto; Python tambien admite indentacion con tabulaciones.

Por ahora quedan fuera las cadenas triples o con prefijo (`r`, `u`, `b`, `f` y combinaciones),
los identificadores Unicode, los numeros binarios/octales/hexadecimales, imaginarios y con
guiones bajos. Se emite un diagnostico, en lugar de presentar esas formas como admitidas.
Las formas numericas mal escritas, como `1e+` o `123abc`, tambien se diagnostican.

Reconocer una palabra reservada o simbolo no significa implementar su ejecucion.
`success: true` tampoco garantiza que una secuencia de tokens forme un programa valido.
Por ejemplo, unir varias asignaciones con barras invertidas puede ser lexicamente valido
pero sintacticamente incorrecto.

## Prioridad y posiciones

El orden efectivo esta en `tokenize`: indentacion y espacios, saltos, comentarios,
continuaciones, cadenas, numeros (FLOAT antes de INTEGER), nombres, operadores,
delimitadores y puntuacion. Los simbolos de varias longitudes se ordenan de mayor a menor;
`**=` se reconoce antes que `**`. No existe una lista decorativa que aparente controlar el motor.

`line` y `column` empiezan en 1; `start` y `end` son indices de caracteres del texto original,
con inicio incluido y final excluido. La columna cuenta caracteres, no ancho visual de tabs.
Los CRLF se conservan en los lexemas y cuentan como un solo salto de linea.
Todo token cumple `token.lexeme == source[token.start:token.end]`.

Las lineas vacias y los comentarios completos no generan NEWLINE, INDENT ni DEDENT.
Tampoco hay NEWLINE o cambios de bloque dentro de una continuacion.
Al final de una linea logica se genera NEWLINE; si el archivo acaba sin salto fisico,
ese token tiene lexema vacio y `start == end == len(source)`.
Despues se emiten los DEDENT pendientes, tambien con lexema vacio.
No se emite ENDMARKER; el consumidor reconoce el fin por el final de la lista.

La interfaz convierte los saltos reales a las etiquetas visibles `\n`, `\r\n` o `\r`.
El lexer no guarda esas representaciones visuales en el lexema.

## Contrato del lexer

Ejemplo de `tokenize("nombre")`:

```json
{
  "success": true,
  "tokens": [
    {
      "type": "IDENTIFIER",
      "lexeme": "nombre",
      "pattern": "Nombre que inicia con letra de A a Z o guion bajo, y continua con esas letras, digitos o guion bajo; admite mayusculas y minusculas.",
      "line": 1,
      "column": 1,
      "start": 0,
      "end": 6
    },
    {
      "type": "NEWLINE",
      "lexeme": "",
      "pattern": "Salto de linea que marca el fin de una linea logica.",
      "line": 1,
      "column": 7,
      "start": 6,
      "end": 6
    }
  ],
  "errors": []
}
```

`pattern` describe la regla en lenguaje natural; la regex permanece en `patterns.py`.
`type` es la clave estable para otros modulos. Su etiqueta en espanol pertenece a la interfaz.
Los errores lexicos incluyen `type`, `message`, `lexeme`, `line`, `column`, `position`
y `suggestion`. `tokenize` requiere texto; una llamada directa con otro tipo lanza `TypeError`.

## API

`POST /api/lexer` requiere `Content-Type: application/json` y un objeto `{"source": "..."}`.
El campo `source` es obligatorio y debe ser texto. La cadena vacia es valida.

- HTTP 200: analisis completado, con `success` verdadero o falso segun los errores lexicos.
- HTTP 400: JSON mal formado, cuerpo distinto de objeto, campo ausente o tipo incorrecto.
- HTTP 415: tipo de contenido distinto de JSON.

Los errores de solicitud mantienen `success: false`, `tokens: []` y una lista `errors`
con `type: "INVALID_REQUEST"` y `message`. No tienen posiciones de codigo ficticias.
La interfaz diferencia errores de solicitud, errores lexicos, fallos HTTP y fallos de red.
`GET /` sirve la interfaz y `GET /api/health` permite comprobar el servicio.

## Ejecucion y pruebas

Desde la raiz, con Python 3.12 y el entorno del proyecto:

```sh
./env/bin/python -m pip install -r requirements.txt
./env/bin/python -m flask --app app run --debug
./env/bin/python -m pytest
```

Abrir `http://127.0.0.1:5000/` para cargar HTML, CSS y modulos JavaScript mediante Flask.
Las pruebas del frontend requieren Node.js 22 o superior y Python 3 accesible:

```sh
node --test tests/test_frontend.mjs
```

Se puede indicar otro interprete con la variable `PYTHON`. Estas pruebas verifican
etiquetas, renderizado y manejo de errores sin instalar dependencias JavaScript.

## Proximas fases

Definir la gramatica del parser y el intercambio de datos entre fases. Ampliar el subconjunto
lexico cuando lo exija esa gramatica, junto con sus descripciones, etiquetas y pruebas.

Referencia: [analisis lexico de Python 3.12](https://docs.python.org/3.12/reference/lexical_analysis.html).

#Añadimos a pedro novelo y emiliano medina
