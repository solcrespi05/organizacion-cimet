---
name: clasificar
description: Arma el plan de reorganización de una tanda - divide el inventario en lotes, los clasifica con agentes en paralelo (destino, nombre nuevo, confianza) y deja plan.csv listo para que el equipo lo apruebe. No toca ningún archivo. Usar cuando pida /archivo:clasificar <tanda>, "armá el plan", "proponé dónde va cada archivo".
argument-hint: <tanda> [--leer] [--planillas <carpeta>]
---

# /archivo:clasificar $ARGUMENTS

`RECURSOS` = `${CLAUDE_PLUGIN_ROOT}/recursos` (si no se expandió, Glob `**/archivo/recursos/archivo.py` en `~/.claude/plugins/`). Reglas de `CLAUDE.md` de la carpeta de trabajo vigentes.

## 0. Precondiciones
- Existe `<tanda>/inventario/inventario.csv`; si no, `/archivo:inventario` primero.
- `config.md` tiene la lista de estudios. Si `estructura.md` es el borrador sin acordar, avisá que el plan puede cambiar y preguntá si siguen igual (para un piloto está bien).
- `--leer` habilita abrir contenido mínimo de archivos no sensibles cuando el nombre no alcanza. `--planillas <carpeta>` habilita también las planillas `posible` de esa carpeta. Sin flags, solo nombre, carpeta y fecha.

## 1. Lotes
```
python -I "RECURSOS/archivo.py" dividir "<tanda>/inventario/inventario.csv" --salida "<tanda>/lotes" --filas 400
```
Si `<tanda>/lotes/` ya tiene lotes clasificados, preguntá si se reclasifica todo o solo los lotes sin completar.

## 2. Clasificación en paralelo
Lanzá un agente `archivo:clasificador` por lote, de a 5 en un mismo mensaje, con: ruta del lote; rutas absolutas a `estructura.md`, `nombres.md`, `sensibles.md`, `config.md`, `referencia/`; la ruta a `RECURSOS/docx_a_texto.py`; y si hay `--leer` / `--planillas`.
Después de la primera tanda de 5, juntá los "patrones" y "dudas generales" que devolvieron: si hay dudas que cambian muchas filas (ej. "¿'CEI' es siempre comité de ética?"), preguntalas al equipo **antes** de lanzar los lotes siguientes, y pasales las respuestas a los próximos agentes.

## 3. Unir y validar
```
python -I "RECURSOS/archivo.py" unir "<tanda>/lotes" --salida "<tanda>/plan.csv"
python -I "RECURSOS/archivo.py" validar "<tanda>/plan.csv" --salida "<tanda>/problemas.csv"
```
Corregí vos en `plan.csv` los problemas mecánicos (caracteres, colisiones entre lotes, largo de rutas) y volvé a validar. Los avisos `sensible=alto fuera de _RESTRINGIDO` no se corrigen solos: van a la lista para el equipo.

## 4. Mostrar
- Conteo por acción (copiar / no_migrar / revisar / exportar) y por confianza.
- Árbol de destino resultante (carpetas con cantidad de archivos), para ver de un vistazo si la estructura tiene sentido.
- 10 ejemplos representativos: nombre viejo → nombre nuevo.
- Lo que necesita decisión humana: filas `revisar` agrupadas por motivo, sensibles fuera de `_RESTRINGIDO`, dudas generales.

## 5. Cómo aprueba el equipo
Explicá: abrir `<tanda>/plan.csv` en Excel, filtrar por `confianza = alta` y poner `si` en `aprobado` (se puede rellenar de una vez), revisar `media` y `revisar` una por una (pueden corregir `carpeta_destino` o `nombre_nuevo` ahí mismo), y guardar como CSV. Lo que quede sin `si` no se migra. Cuando terminen: `/archivo:migrar <tanda>`.

No muevas, copies ni renombres nada en esta skill.
