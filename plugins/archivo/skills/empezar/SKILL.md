---
name: empezar
description: Configura la carpeta de trabajo para ordenar el archivo regulatorio - dónde están los archivos (Drive), adónde van (SharePoint), códigos de estudio y material de referencia. Usar cuando pida /archivo:empezar, "quiero ordenar las carpetas", "configurar el orden del archivo", o cuando otra skill de archivo no encuentre config.md.
---

# /archivo:empezar

`RECURSOS` = `${CLAUDE_PLUGIN_ROOT}/recursos` (si no se expandió, buscá con Glob `**/archivo/recursos/archivo.py` dentro de `~/.claude/plugins/` y usá su carpeta).

## 1. Carpeta de trabajo
- Tiene que ser una carpeta **local y aparte**, ni dentro del Drive de origen ni dentro de la biblioteca de SharePoint (ej. `Documentos/orden-archivo`). Si la carpeta actual no cumple, proponé crearla y pedí que abran Claude Code ahí.
- Copiá desde `RECURSOS`: `CLAUDE.md`, `estructura.md`, `nombres.md`, `sensibles.md`. Creá `referencia/` y `sensibles.txt` vacío. Si ya existen, no los pises.

## 2. Origen (Google Drive)
- Los archivos se leen desde **Google Drive para escritorio** (unidad `G:` en Windows, `~/Library/CloudStorage/GoogleDrive-...` en macOS). Verificá que exista.
- Pedí la carpeta del Centro. Si está en "Compartidos conmigo" no aparece en `G:`: hay que agregarle un acceso directo a "Mi unidad" desde drive.google.com (clic derecho → Organizar → Agregar acceso directo) o estar en la unidad compartida. Explicalo paso a paso.
- Listá solo el primer nivel de carpetas para confirmar que es la correcta (nombres, sin abrir archivos).

## 3. Destino (SharePoint)
- La forma recomendada: crear en SharePoint el sitio o la biblioteca (ej. "Regulatoria"), y en el navegador tocar **Sincronizar** (o "Agregar acceso directo a Mis archivos"). Aparece como carpeta local en el Explorador (ej. `C:\Users\<usuario>\<Organización>\Regulatoria - Documentos`). Esa carpeta es el destino.
- Si todavía no existe la biblioteca, dejá el destino en `[FALTA]` y seguí: se puede inventariar, clasificar y aprobar sin destino; solo `/archivo:migrar` lo necesita.
- Recomendá a quien administre SharePoint: activar control de versiones en la biblioteca y crear `_RESTRINGIDO` con permisos propios **antes** de migrar.

## 4. Estudios y referencia
Preguntá en un solo mensaje:
- Lista de estudios o proyectos con el código corto que quieren usar (ej. "Mortalidad infantil → MORTALIDAD") y nombres alternativos con los que aparecen en carpetas y archivos.
- Quién aprueba los planes (una o dos personas).
- Si tienen el POE anterior, listados de documentos, o cualquier cosa que ayude a reconocer archivos: que lo pongan en `referencia/` (o que lo adjunten y lo guardás ahí).

## 5. config.md
Escribí `config.md`:
```
# Configuración
- Origen: <ruta en G:>
- Destino: <ruta de la biblioteca sincronizada o [FALTA]>
- Aprueban: <nombres>
## Estudios
| Código | Nombre | Cómo aparece en carpetas/archivos |
|---|---|---|
```

## 6. Cerrar
Resumí la configuración y proponé el primer paso: un piloto con una sola carpeta, por ejemplo `/archivo:inventario <carpeta de un estudio>`.
