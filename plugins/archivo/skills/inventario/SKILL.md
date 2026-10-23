---
name: inventario
description: Inventaría una carpeta del Drive sin modificar nada - cantidad de archivos, duplicados exactos, nativos de Google, temporales, sensibles, rutas largas, carpetas vacías. Usar cuando pida /archivo:inventario <carpeta>, "cuántos archivos hay", "qué hay en la carpeta de X", o como primer paso de una tanda.
argument-hint: <carpeta de origen> [nombre de la tanda]
---

# /archivo:inventario $ARGUMENTS

`RECURSOS` = `${CLAUDE_PLUGIN_ROOT}/recursos` (si no se expandió, Glob `**/archivo/recursos/archivo.py` en `~/.claude/plugins/`). Si no existe `config.md`, seguí primero la skill `archivo:empezar`.

## Pasos
1. **Carpeta**: la del argumento, relativa al origen de `config.md` o absoluta. Si no hay argumento, preguntá cuál (sugerí empezar por un solo estudio).
2. **Tanda**: nombre corto (ej. `piloto-mortalidad`); si no lo dieron, derivalo de la carpeta. Si `<tanda>/inventario/` ya existe, preguntá si se rehace.
3. **Avisá antes de correr**: con Google Drive para escritorio, calcular huellas de los archivos de tamaño repetido obliga a bajarlos; con miles de archivos puede tardar. Si son muchos (estimalo listando primero la cantidad con un conteo rápido), proponé `--hash no` para una primera vista y el hash después.
4. Corré en segundo plano si puede tardar más de 2 minutos:
   ```
   python -I "RECURSOS/archivo.py" inventario "<carpeta>" --salida "<tanda>/inventario" --sensibles sensibles.txt
   ```
   (`python3` en macOS/Linux.)
5. **Mostrá** el contenido de `resumen.md` y explicá en 3–5 líneas lo más relevante: duplicados y espacio, nativos de Google a exportar, sensibles (cuántos y de qué tipo), rutas largas, errores de lectura.
6. **No abras ningún archivo** del origen en esta skill.
7. Próximo paso: si `estructura.md` todavía es el borrador del plugin, `/archivo:estructura`; si ya está acordada, `/archivo:clasificar <tanda>`.
