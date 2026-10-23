---
name: estructura
description: Ajusta con el equipo la estructura de carpetas y la convención de nombres del archivo regulatorio (basadas en el TMF Reference Model), usando el inventario real y el POE anterior si existe. Usar cuando pida /archivo:estructura, "armemos la estructura", "cómo nombramos los archivos", "agregá una carpeta para X".
argument-hint: (opcional) tanda cuyo inventario usar como referencia, o el cambio a hacer
---

# /archivo:estructura $ARGUMENTS

Trabajás sobre `estructura.md` y `nombres.md` de la carpeta de trabajo (copias del borrador del plugin). La decisión final es del equipo de regulatoria.

## Si es un cambio puntual
("agregá un tipo de documento", "las aprobaciones van por año") → editá el archivo, mostrá el diff en 3–5 líneas y avisá si afecta planes ya clasificados (qué tandas habría que reclasificar).

## Si es la primera vez
1. Leé `estructura.md`, `nombres.md`, `config.md` y lo que haya en `referencia/` (POE anterior: estructura y nomenclatura que ya usaban, para no romper costumbres que funcionan).
2. Si hay inventario, mirá en `inventario.csv` solo las columnas `carpeta`, `nombre` y `ext`: qué tipos de documento aparecen realmente, cómo los llaman (ej. "CEI", "comité", "aprob"), qué carpetas existen. No abras archivos.
3. Proponé ajustes concretos al borrador, cada uno con su motivo: carpetas que sobran o faltan para lo que tienen, tipos de documento con el nombre que ya usa el equipo, cómo tratar lo que no es de estudios (administración, docencia).
4. Hacé las 3–5 preguntas que solo el equipo puede responder, juntas (ej. "¿Las aprobaciones de comité van todas juntas o por enmienda?", "¿Cada estudio tiene un código oficial?", "¿Hay sponsors que exijan su propia estructura?").
5. Con las respuestas, actualizá `estructura.md` y `nombres.md` y mostrá el árbol final.
6. Recordá: si el Centro va a usar esta estructura en un POE nuevo, `estructura.md` + `nombres.md` son la base del documento; ofrecé redactar el borrador del POE (queda como borrador para que el equipo lo apruebe).
