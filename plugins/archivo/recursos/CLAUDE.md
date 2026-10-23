# Orden del archivo regulatorio

Carpeta de trabajo del plugin `archivo` (CIMET). Acá viven el inventario, la estructura acordada, el plan y los registros. **Los archivos del Centro no se tocan desde acá.**

## Estructura

- `config.md` → origen (carpeta de Drive), destino (biblioteca de SharePoint sincronizada), códigos de estudio, quién aprueba.
- `estructura.md` → estructura de carpetas vigente (acordada con el equipo).
- `nombres.md` → convención de nombres vigente.
- `sensibles.md` / `sensibles.txt` → qué no se abre nunca y patrones extra.
- `referencia/` → POE anterior, listados de estudios, glosarios: lo que ayude a reconocer documentos.
- `<tanda>/` → una carpeta por tanda (ej. `piloto-mortalidad/`):
  - `inventario/` → `inventario.csv`, `resumen.md`.
  - `lotes/` → lotes que clasifican los agentes.
  - `plan.csv` → el plan unificado: lo que el equipo revisa y aprueba (columna `aprobado`).
  - `registros/` → simulaciones y migraciones con hash de cada copia (trazabilidad).

## Reglas (agentes, skills y sesión principal)

1. **Solo lectura sobre el origen.** Nunca se mueve, renombra, edita ni borra un archivo del Drive del Centro. Ni siquiera los duplicados o la basura: se marcan `no_migrar`.
2. **Nada se copia sin aprobación.** Solo filas con `aprobado = si` en `plan.csv`, aprobadas por una persona del equipo.
3. **Simular antes de ejecutar.** Toda migración corre primero en simulación y se muestra el resultado.
4. **Nunca se sobrescribe** en el destino; cada copia se verifica por SHA-256 y queda en `registros/`.
5. **Contenido: mínimo y nunca lo sensible.** Se clasifica por nombre, carpeta, extensión y fecha. Lo marcado `sensible = alto` jamás se abre; `posible` solo con permiso explícito. Ver `sensibles.md`.
6. **Ante la duda, `revisar`.** Mejor una fila para decisión humana que un documento regulatorio mal archivado.
7. Las planillas de esta carpeta contienen nombres de archivos del Centro: no se suben a ningún lado ni se comparten fuera del equipo.
