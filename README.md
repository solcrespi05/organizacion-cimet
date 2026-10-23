# Organización del archivo — CIMET

Plugin de [Claude Code](https://claude.com/claude-code) para ordenar el archivo regulatorio del Centro (regulatoria, comité de ética, consentimientos, bases) y migrarlo de **Google Drive a SharePoint**, sin hacerlo a mano y **sin tocar los archivos originales**.

## Instalación (una sola vez)

En la **caja de mensajes de Claude Code** (no en PowerShell ni en la terminal):

```
/plugin marketplace add solcrespi05/organizacion-cimet
/plugin install archivo@organizacion-cimet
```

Después abrí una sesión nueva para que aparezcan los comandos.

**Requisitos:**
- Google Drive para escritorio (el Drive aparece como unidad `G:`). Si las carpetas del Centro están en "Compartidos conmigo", agregales un acceso directo a "Mi unidad" desde drive.google.com.
- La biblioteca de SharePoint de destino sincronizada con OneDrive (botón **Sincronizar** en SharePoint). Solo hace falta para el último paso.
- Python 3.

## Uso

Creá una carpeta de trabajo local, aparte del Drive y de SharePoint (ej. `Documentos/orden-archivo`), abrí Claude Code ahí y:

| Comando | Qué hace |
|---|---|
| `/archivo:empezar` | Configura origen (Drive), destino (SharePoint), códigos de estudio y material de referencia (POE anterior). |
| `/archivo:inventario <carpeta>` | Recorre la carpeta **sin modificar nada**: cuántos archivos, duplicados exactos, Google Docs a exportar, sensibles, rutas largas. |
| `/archivo:estructura` | Ajusta con el equipo la estructura de carpetas (basada en el TMF Reference Model) y la convención de nombres. Sirve de base para el POE nuevo. |
| `/archivo:clasificar <tanda>` | Agentes en paralelo proponen para cada archivo: destino, nombre nuevo, confianza y motivo. Resultado: `plan.csv`. |
| `/archivo:migrar <tanda>` | Copia **solo lo aprobado** a SharePoint: simula primero, nunca sobrescribe, verifica cada copia por huella (SHA-256) y guarda el registro. |
| `/archivo:archivar <archivo>` | Para el día a día: dónde va y cómo se llama un documento nuevo. |

### El circuito

1. **Inventario**: no toca nada; minutos u horas según el tamaño.
2. **Plan**: Claude propone; el equipo abre `plan.csv` en Excel, aprueba de una vez las filas de confianza alta y revisa las dudosas.
3. **Migración**: copia verificada a SharePoint. Los originales en Drive quedan intactos; archivarlos es decisión del equipo, después de un período de prueba.

Empezar con un **piloto de un estudio** antes de escalar.

## Seguridad

- **Los originales nunca se mueven, renombran ni borran.** Ni siquiera los duplicados.
- **Nada se copia sin aprobación** de una persona del equipo, y siempre se simula antes.
- **Claude clasifica por nombre, carpeta y fecha.** Bases de datos, consentimientos firmados, historias clínicas, certificados de defunción y escaneos **nunca se abren** (ver `sensibles.md`); van a `_RESTRINGIDO/`, que en SharePoint debe tener permisos propios.
- **Trazabilidad**: cada copia queda registrada con ruta vieja, ruta nueva y huella SHA-256, lo que demuestra que es idéntica al original.
- Las planillas de trabajo (con nombres de archivos del Centro) quedan en la computadora de quien lo corre; este repo no las incluye.

## Mantener el plugin

- `plugins/archivo/recursos/archivo.py`: inventario, división en lotes, validación y migración (solo biblioteca estándar de Python).
- `plugins/archivo/recursos/`: estructura y nombres por defecto, reglas de sensibles, reglas de la carpeta de trabajo.
- `plugins/archivo/agents/clasificador.md` y `plugins/archivo/skills/<nombre>/SKILL.md`.
- Al cambiar algo, subí `version` en `plugins/archivo/.claude-plugin/plugin.json` y en `.claude-plugin/marketplace.json`. Se actualiza con `/plugin marketplace update organizacion-cimet`.
