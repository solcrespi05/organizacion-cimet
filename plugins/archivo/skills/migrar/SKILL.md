---
name: migrar
description: Copia a la estructura nueva en SharePoint los archivos aprobados del plan de una tanda - simula primero, nunca sobrescribe, verifica cada copia por SHA-256 y deja registro de trazabilidad. Los originales no se tocan. Usar cuando pida /archivo:migrar <tanda>, "pasalo a SharePoint", "ejecutá el plan".
argument-hint: <tanda>
---

# /archivo:migrar $ARGUMENTS

`RECURSOS` = `${CLAUDE_PLUGIN_ROOT}/recursos` (si no se expandió, Glob `**/archivo/recursos/archivo.py` en `~/.claude/plugins/`). Reglas de `CLAUDE.md` vigentes: solo lectura sobre el origen, nada sin aprobación, simular antes de ejecutar.

## 0. Precondiciones
- `<tanda>/plan.csv` existe y tiene filas con `aprobado = si`. Si no hay ninguna, explicá cómo aprobar (ver `/archivo:clasificar`, paso 5) y frená.
- `config.md` tiene destino. Verificá que la carpeta exista y sea una biblioteca de SharePoint sincronizada (está bajo la carpeta de la organización de OneDrive). Si no, frená y explicá cómo sincronizarla.
- Recordá (una vez) que `_RESTRINGIDO` debería tener sus permisos configurados en SharePoint antes de copiar ahí. Si no lo confirman, ofrecé migrar primero todo lo demás (filtrando: dejá esas filas sin `si` en una copia del plan).

## 1. Validar
`python -I "RECURSOS/archivo.py" validar "<tanda>/plan.csv"`. Si hay problemas en filas aprobadas, mostralos y frená (el script de migración también se niega).

## 2. Simular
```
python -I "RECURSOS/archivo.py" migrar "<tanda>/plan.csv" --origen "<origen>" --destino "<destino>" --registro "<tanda>/registros"
```
Mostrá: cuántos se copiarían, cuántos ya existen, errores, y cuántos nativos de Google quedan para exportar.

## 3. Confirmación explícita
Pedí un "sí" para ejecutar, diciendo cuántos archivos y a qué carpeta. Sin ese sí no sigas.

## 4. Ejecutar
El mismo comando con `--ejecutar`, en segundo plano si son muchos. Al terminar, mostrá el conteo por estado y la ruta del registro. Los `error:` se listan uno por uno con su causa.

## 5. Nativos de Google (filas `exportar` aprobadas)
SharePoint no puede guardar un .gdoc/.gsheet: hay que exportarlos a Office.
1. Generá `<tanda>/exportar.md` con una tabla: archivo original en Drive → nombre con el que guardarlo (`nombre_nuevo` del plan).
2. Explicá: abrir cada uno en Drive → Archivo → Descargar → Microsoft Word/Excel/PowerPoint, y guardarlo en `<tanda>/exportados/` con el nombre de la tabla. (Si son muchos, alternativa: pedir a quien administre Google Workspace un export masivo, o usar Migration Manager de Microsoft para esos archivos.)
3. Cuando estén: el mismo comando de migración con `--exportados "<tanda>/exportados"` (simular, confirmar, ejecutar).

## 6. Después
- Sugerí que alguien del equipo abra 5–10 archivos al azar en SharePoint para chequear.
- **Los originales en Drive siguen intactos.** Archivar o borrar las carpetas viejas es una decisión del equipo, recomendable recién después de un período de prueba (ej. 1–2 meses) y conservando los registros de `registros/` como trazabilidad. Esta skill nunca lo hace.
