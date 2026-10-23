# Estructura objetivo (borrador para que el equipo ajuste)

> Basada en una versión simplificada del **TMF Reference Model** (estándar de la industria para el Trial Master File) más carpetas institucionales del Centro.
> Es un punto de partida: el equipo de regulatoria la ajusta con `/archivo:estructura` y esta copia en la carpeta de trabajo pasa a ser la vigente.
> Si el POE anterior o un sponsor exigen otra estructura para un estudio, se respeta para ese estudio.

## Nivel 1

```
00_CENTRO/                     documentos institucionales, no ligados a un estudio
<CODIGO-ESTUDIO>/              una carpeta por estudio o proyecto (ej. MORTALIDAD, GATES-RSV)
_RESTRINGIDO/                  documentos con datos identificables de pacientes (permisos aparte)
_REVISAR/                      lo que no se pudo clasificar con confianza
```

## 00_CENTRO

```
00_CENTRO/
  01_POEs/                     procedimientos operativos estándar, por código y versión
  02_Habilitaciones/           habilitaciones, inscripciones, registros del Centro
  03_Comite_etica_institucional/   (si el Centro tiene comité propio: actas, reglamento, miembros)
  04_Plantillas/               plantillas vigentes (CI, notas, logs en blanco)
  05_Personal/                 CVs, certificados BPC/GCP, entrenamientos del personal permanente
  06_Convenios_institucionales/
  07_Calidad_auditorias/       auditorías e inspecciones institucionales
  08_Administracion/           lo administrativo que no es de un estudio
```

## <CODIGO-ESTUDIO>

```
<CODIGO-ESTUDIO>/
  01_Gestion/                  contratos, presupuesto, convenios, correspondencia con sponsor o financiador, cronograma
  02_Protocolo/                protocolo y enmiendas (por versión), resumen, manual de procedimientos, CRF en blanco, folleto del investigador
  03_Regulatoria/              presentaciones y aprobaciones ante autoridades (ANMAT, Ministerio, registros), seguros, registro del estudio (ClinicalTrials.gov, RENIS)
  04_Comite_etica/             presentaciones, aprobaciones, renovaciones, informes de avance y final, correspondencia, por fecha
  05_Consentimientos/          modelos de CI/asentimiento APROBADOS por versión (los firmados van en _RESTRINGIDO)
  06_Equipo/                   delegation log, CVs y certificados BPC del equipo del estudio, registros de entrenamiento
  07_Seguridad/                eventos adversos serios, reportes de seguridad, DSMB
  08_Monitoreo/                visitas de monitoreo, informes, notas al archivo, desvíos
  09_Laboratorio_muestras/     manuales, certificados, rangos de referencia, registros de envío y temperatura
  10_Datos/                    plan de gestión de datos, diccionarios, plan de análisis, scripts (bases nominales → _RESTRINGIDO)
  11_Resultados/               informes, abstracts, manuscritos, presentaciones
  12_Cierre/                   cierre del sitio, archivo final
```

## _RESTRINGIDO

```
_RESTRINGIDO/<CODIGO-ESTUDIO>/
  Consentimientos_firmados/
  Bases_nominales/
  Documentos_fuente/           historias clínicas, certificados de defunción, informes con datos de pacientes
```

## Reglas
- Ninguna carpeta pasa de 3 niveles debajo del estudio (los detalles van en el nombre del archivo, no en más carpetas).
- Versiones viejas de un documento no se borran: conviven con su número de versión. Si molestan, `Versiones_anteriores/` dentro de la misma carpeta.
