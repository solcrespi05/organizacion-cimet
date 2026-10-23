# Qué no se abre nunca

Claude clasifica **por nombre, carpeta, extensión, tamaño y fecha**. Abrir contenido es la excepción, y estos archivos **nunca** se abren (solo se inventarían y se mandan a `_RESTRINGIDO/` o a la carpeta que decida el equipo):

## `sensible = alto` (lo marca `inventario.py`)
- **Bases de datos**: `.csv .tsv .dta .sav .sas7bdat .xpt .rds .rdata .parquet .feather .sqlite .db .mdb .accdb .json` (export de REDCap y similares).
- **Nombres que sugieren datos de pacientes**: consentimiento firmado, historia clínica, HC, DNI, pacientes, nominal, identificados, certificado de defunción, defunción, óbito, autopsia, anatomía patológica / pathology report, epicrisis, resumen de alta, laboratorio de paciente, REDCap export, base, CRF completo.
- Escaneos de documentos firmados: `.jpg .jpeg .png .tif .heic` y PDFs con "escaneo", "scan", "firmado" en el nombre.

## `sensible = posible`
- Planillas `.xls .xlsx .xlsm .gsheet`: pueden ser logs administrativos o bases. No se abren sin permiso explícito del equipo para ese archivo o carpeta.

## Cuándo sí se puede abrir contenido
Solo si **todo** esto se cumple:
1. `sensible = no`.
2. El nombre y la carpeta no alcanzan para clasificarlo.
3. El equipo habilitó la lectura de contenido en esta corrida (`/archivo:clasificar --leer`).
4. Se lee lo mínimo: primera página de un PDF, primeras líneas de un Word, para sacar tipo, estudio, fecha y versión.

## Agregar reglas
El equipo puede sumar patrones en `sensibles.txt` de la carpeta de trabajo (una expresión regular por línea, sin distinguir mayúsculas ni tildes). `inventario.py` los aplica.
