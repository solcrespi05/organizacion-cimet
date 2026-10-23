# Convención de nombres (borrador)

```
AAAA-MM-DD_ESTUDIO_TipoDoc_Descripcion_vX.Y[_Estado].ext
```

| Parte | Regla | Ejemplo |
|---|---|---|
| `AAAA-MM-DD` | Fecha **del documento** (aprobación, firma, emisión), no la de modificación del archivo. Si no se conoce, la de modificación y en el plan `fecha_fuente = archivo`. | `2024-03-15` |
| `ESTUDIO` | Código corto del estudio en mayúsculas, igual que su carpeta. `CENTRO` para institucionales. | `MORTALIDAD` |
| `TipoDoc` | De la lista de abajo. | `AprobCE` |
| `Descripcion` | 1–5 palabras en CamelCase o con guiones, sin espacios. | `Enmienda2-Protocolo` |
| `vX.Y` | Versión si el documento la tiene. Si no, se omite. | `v2.0` |
| `Estado` | Solo si aplica: `borrador`, `firmado`, `aprobado`, `presentado`. | `firmado` |

## Tipos de documento (TipoDoc)
`Protocolo` · `Enmienda` · `Resumen` · `Manual` · `CRF` · `FolletoInv` · `CI` (modelo de consentimiento) · `Asentimiento` · `PresentCE` (presentación al comité) · `AprobCE` (aprobación del comité) · `InformeCE` (avance/final) · `PresentReg` / `AprobReg` (autoridad regulatoria) · `Seguro` · `Registro` (ClinicalTrials, RENIS) · `Contrato` · `Convenio` · `Presupuesto` · `Correspondencia` · `DelegationLog` · `CV` · `CertBPC` · `Entrenamiento` · `EAS` (evento adverso serio) · `ReporteSeg` · `Monitoreo` · `NotaArchivo` · `Desvio` · `ManualLab` · `CertLab` · `RegTemperatura` · `Envio` · `PlanDatos` · `Diccionario` · `PlanAnalisis` · `Script` · `Base` · `Informe` · `Abstract` · `Manuscrito` · `Presentacion` · `POE` · `Plantilla` · `Habilitacion` · `Acta` · `Otro`

El equipo puede agregar tipos: editá esta lista en la copia de la carpeta de trabajo.

## Restricciones de SharePoint / OneDrive (las controla `plan.py validar`)
- Caracteres prohibidos: `" * : < > ? / \ |` y tampoco `#` `%` por compatibilidad. Sin espacios al inicio o al final, sin punto final.
- Nombres reservados: `CON`, `PRN`, `AUX`, `NUL`, `COM1`…, `LPT1`…, `_vti_`, `desktop.ini`.
- Ruta completa (desde la biblioteca) ≤ 400 caracteres; apuntá a ≤ 200 para que sincronice bien en Windows.
- Nombre de archivo ≤ 120 caracteres.
- Sin tildes ni ñ en los nombres nuevos (se ven mal en algunos sistemas y en links): `Comite`, `Anio`.
