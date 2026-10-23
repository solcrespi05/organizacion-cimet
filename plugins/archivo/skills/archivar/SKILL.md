---
name: archivar
description: Para el día a día después del orden - propone dónde va y cómo se llama un documento nuevo (o varios) según la estructura y la convención acordadas, y lo copia a SharePoint con aprobación. Usar cuando pida /archivo:archivar, "dónde guardo esto", "cómo nombro este archivo", "archivá esta aprobación del comité".
argument-hint: <archivo(s) o carpeta> [estudio]
---

# /archivo:archivar $ARGUMENTS

`RECURSOS` = `${CLAUDE_PLUGIN_ROOT}/recursos` (si no se expandió, Glob `**/archivo/recursos/archivo.py` en `~/.claude/plugins/`). Usá `estructura.md`, `nombres.md`, `sensibles.md` y `config.md` de la carpeta de trabajo.

## Pasos
1. **Archivos**: los del argumento (rutas o adjuntos). Si son más de 20, usá el circuito completo (`/archivo:inventario` + `/archivo:clasificar`).
2. **Clasificar** cada uno con las mismas reglas que el agente `archivo:clasificador`: por nombre y contexto; si no alcanza y no es sensible, podés abrir lo mínimo (primera página). Si el usuario dijo de qué se trata, usalo.
3. **Proponer** una tabla: archivo → carpeta destino → nombre nuevo → motivo. Avisá si ya existe un archivo con ese nombre en el destino o si parece una nueva versión de uno existente (mismo tipo y estudio): en ese caso proponé el número de versión siguiente.
4. **Con el ok** (puede corregir destino o nombre), copiá con verificación: armá un `plan.csv` de una sola tanda `archivados/AAAA-MM-DD/` con esas filas aprobadas y corré `migrar` (simular y ejecutar) igual que en `/archivo:migrar`, para que quede el registro. El archivo original queda donde estaba.
5. Mostrá dónde quedó cada uno.
