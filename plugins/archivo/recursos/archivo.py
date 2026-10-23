"""Herramientas para ordenar el archivo regulatorio sin tocar los originales.

Solo biblioteca estándar. Las planillas son CSV con ';' y UTF-8 con BOM (se abren bien en Excel en castellano).

Subcomandos:
  inventario <raiz> --salida <dir> [--hash auto|todo|no] [--sensibles sensibles.txt]
      Recorre <raiz> sin modificar nada y escribe inventario.csv + resumen.md.
      --hash auto (por defecto) calcula SHA-256 solo de archivos con tamaño repetido (para detectar duplicados).
  dividir <inventario.csv> --salida <dir> [--filas 400]
      Parte el inventario en lotes por carpeta para que los clasifiquen varios agentes en paralelo.
  unir <dir_lotes> --salida plan.csv
      Junta los lotes clasificados en un único plan.
  validar <plan.csv> [--max-ruta 200]
      Controla nombres y rutas para SharePoint, colisiones, sensibles fuera de _RESTRINGIDO y filas sin decidir.
  migrar <plan.csv> --origen <raiz> --destino <raiz> --registro <dir> [--ejecutar]
      Copia las filas aprobadas (aprobado = si) con accion = copiar. Sin --ejecutar solo simula.
      Nunca modifica, mueve ni borra originales; nunca sobrescribe en el destino; verifica cada copia por SHA-256.
"""
import argparse
import csv
import datetime as dt
import hashlib
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict

SEP = ";"
GOOGLE_NATIVO = {".gdoc", ".gsheet", ".gslides", ".gdraw", ".gform", ".gmap", ".gsite", ".gjam", ".gtable"}
TEMPORALES = re.compile(r"^(~\$.*|\.~lock\..*|desktop\.ini|thumbs\.db|\.ds_store|.*\.tmp)$", re.I)
EXT_DATOS = {".csv", ".tsv", ".dta", ".sav", ".sas7bdat", ".xpt", ".rds", ".rdata", ".parquet", ".feather",
             ".sqlite", ".db", ".mdb", ".accdb", ".json"}
EXT_PLANILLA = {".xls", ".xlsx", ".xlsm", ".gsheet", ".ods"}
EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".bmp"}
PATRONES_ALTO = [
    r"consentimiento.{0,20}firmad", r"\bci\b.{0,10}firmad", r"firmad[oa]s?\b.*\b(ci|consent)",
    r"historia.?clinica", r"\bhc\b", r"\bdni\b", r"pacientes?", r"nominal", r"identificad",
    r"certificado.{0,5}defuncion", r"defuncion", r"obito", r"autopsia", r"anatomia.?patologica",
    r"pathology.?report", r"epicrisis", r"resumen.{0,5}alta", r"redcap.?export", r"\bbases?\b",
    r"\bdatos\b.*\b(crudos|raw|completos)\b", r"crf.{0,10}(complet|llen)", r"escaneo|\bscan",
]
COLUMNAS_INV = ["id", "origen", "carpeta", "nombre", "ext", "tamano", "modificado", "sha256",
                "google_nativo", "temporal", "sensible", "dup_grupo", "dup_principal", "largo_ruta"]
COLUMNAS_PLAN = COLUMNAS_INV + ["accion", "estudio", "carpeta_destino", "nombre_nuevo", "fecha_doc",
                                "fecha_fuente", "confianza", "motivo", "aprobado"]
ACCIONES = {"copiar", "no_migrar", "revisar", "exportar"}
PROHIBIDOS = re.compile(r'["*:<>?/\\|#%]')
RESERVADOS = re.compile(r"^(con|prn|aux|nul|com\d|lpt\d|desktop\.ini)(\..*)?$|_vti_", re.I)


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).lower()


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        muestra = f.read(4096)
        f.seek(0)
        sep = ";" if muestra.count(";") >= muestra.count(",") else ","
        return list(csv.DictReader(f, delimiter=sep))


def escribir_csv(ruta, filas, columnas):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, delimiter=SEP, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def cargar_patrones(extra):
    patrones = list(PATRONES_ALTO)
    if extra and os.path.exists(extra):
        with open(extra, encoding="utf-8") as f:
            patrones += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return [re.compile(sin_tildes(p)) for p in patrones]


def clasificar_sensible(rel, ext, patrones):
    texto = sin_tildes(rel)
    if ext in EXT_DATOS or ext in EXT_IMAGEN or any(p.search(texto) for p in patrones):
        return "alto"
    if ext in EXT_PLANILLA:
        return "posible"
    return "no"


# ---------- inventario ----------

def cmd_inventario(a):
    raiz = os.path.abspath(a.raiz)
    if not os.path.isdir(raiz):
        sys.exit(f"No existe la carpeta: {raiz}")
    patrones = cargar_patrones(a.sensibles)
    filas, errores, vacias = [], [], []

    def al_error(e):
        errores.append(f"{e.filename}: {e.strerror}")

    for dirpath, dirnames, filenames in os.walk(raiz, onerror=al_error, followlinks=False):
        dirnames.sort()
        if not dirnames and not filenames:
            vacias.append(os.path.relpath(dirpath, raiz))
        for nombre in sorted(filenames):
            ruta = os.path.join(dirpath, nombre)
            rel = os.path.relpath(ruta, raiz)
            ext = os.path.splitext(nombre)[1].lower()
            try:
                st = os.stat(ruta)
            except OSError as e:
                errores.append(f"{rel}: {e.strerror}")
                continue
            filas.append({
                "id": len(filas) + 1,
                "origen": rel,
                "carpeta": os.path.dirname(rel),
                "nombre": nombre,
                "ext": ext,
                "tamano": st.st_size,
                "modificado": dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d"),
                "sha256": "",
                "google_nativo": "si" if ext in GOOGLE_NATIVO else "no",
                "temporal": "si" if TEMPORALES.match(nombre) else "no",
                "sensible": clasificar_sensible(rel, ext, patrones),
                "dup_grupo": "",
                "dup_principal": "",
                "largo_ruta": len(rel),
            })

    # Duplicados exactos: solo se hashean los archivos con tamaño repetido (salvo --hash todo).
    if a.hash != "no":
        por_tamano = defaultdict(list)
        for f in filas:
            if f["google_nativo"] == "no" and f["tamano"] > 0:
                por_tamano[f["tamano"]].append(f)
        candidatos = [f for g in por_tamano.values() if len(g) > 1 for f in g] if a.hash == "auto" \
            else [f for g in por_tamano.values() for f in g]
        for i, f in enumerate(candidatos, 1):
            try:
                f["sha256"] = sha256(os.path.join(raiz, f["origen"]))
            except OSError as e:
                errores.append(f"{f['origen']}: no se pudo leer para hash ({e.strerror})")
            if i % 200 == 0:
                print(f"  hash {i}/{len(candidatos)}", file=sys.stderr)
        por_hash = defaultdict(list)
        for f in filas:
            if f["sha256"]:
                por_hash[f["sha256"]].append(f)
        grupo = 0
        for copias in por_hash.values():
            if len(copias) > 1:
                grupo += 1
                copias.sort(key=lambda x: (x["modificado"], x["largo_ruta"]))
                for j, f in enumerate(copias):
                    f["dup_grupo"] = grupo
                    f["dup_principal"] = "si" if j == 0 else "no"

    os.makedirs(a.salida, exist_ok=True)
    escribir_csv(os.path.join(a.salida, "inventario.csv"), filas, COLUMNAS_INV)
    escribir_resumen(os.path.join(a.salida, "resumen.md"), raiz, filas, vacias, errores)
    print(f"{len(filas)} archivos inventariados → {a.salida}")


def humano(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def escribir_resumen(ruta, raiz, filas, vacias, errores):
    total = sum(f["tamano"] for f in filas)
    dups = [f for f in filas if f["dup_principal"] == "no"]
    por_ext = Counter(f["ext"] or "(sin)" for f in filas)
    por_top = Counter(f["origen"].split(os.sep)[0] if os.sep in f["origen"] else "(raíz)" for f in filas)
    sens = Counter(f["sensible"] for f in filas)
    largos = [f for f in filas if f["largo_ruta"] > 200]
    L = [f"# Inventario de `{raiz}`", "",
         f"Generado {dt.date.today()} · solo lectura, no se modificó nada.", "",
         "| | |", "|---|---|",
         f"| Archivos | {len(filas)} ({humano(total)}) |",
         f"| Duplicados exactos (copias de más) | {len(dups)} ({humano(sum(f['tamano'] for f in dups))}) |",
         f"| Google nativos (.gdoc/.gsheet/...) — hay que exportarlos para SharePoint | {sum(f['google_nativo'] == 'si' for f in filas)} |",
         f"| Temporales / basura del sistema | {sum(f['temporal'] == 'si' for f in filas)} |",
         f"| Sensibles: alto / posible | {sens['alto']} / {sens['posible']} |",
         f"| Rutas de más de 200 caracteres | {len(largos)} |",
         f"| Carpetas vacías | {len(vacias)} |",
         f"| Errores de lectura | {len(errores)} |", "",
         "## Por carpeta de primer nivel", "", "| Carpeta | Archivos |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in por_top.most_common()]
    L += ["", "## Por extensión (top 20)", "", "| Ext | Archivos |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in por_ext.most_common(20)]
    if errores:
        L += ["", "## Errores", ""] + [f"- {e}" for e in errores[:100]]
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------- dividir / unir ----------

def cmd_dividir(a):
    filas = leer_csv(a.inventario)
    por_carpeta = defaultdict(list)
    for f in filas:
        por_carpeta[f["carpeta"]].append(f)
    lotes, actual = [], []
    for carpeta in sorted(por_carpeta):
        grupo = por_carpeta[carpeta]
        if actual and len(actual) + len(grupo) > a.filas:
            lotes.append(actual)
            actual = []
        actual += grupo
    if actual:
        lotes.append(actual)
    os.makedirs(a.salida, exist_ok=True)
    for i, lote in enumerate(lotes, 1):
        escribir_csv(os.path.join(a.salida, f"lote_{i:03d}.csv"), lote, COLUMNAS_PLAN)
    print(f"{len(filas)} filas en {len(lotes)} lotes → {a.salida}")


def cmd_unir(a):
    filas = []
    for nombre in sorted(os.listdir(a.dir_lotes)):
        if re.match(r"lote_\d+\.csv$", nombre):
            filas += leer_csv(os.path.join(a.dir_lotes, nombre))
    filas.sort(key=lambda f: int(f["id"]))
    ids = [f["id"] for f in filas]
    if len(ids) != len(set(ids)):
        sys.exit("Hay ids repetidos entre lotes: revisá antes de unir.")
    escribir_csv(a.salida, filas, COLUMNAS_PLAN)
    print(f"{len(filas)} filas → {a.salida}")


# ---------- validar ----------

def destino_de(f):
    return os.path.join(f.get("carpeta_destino", "").strip().strip("/\\"), f.get("nombre_nuevo", "").strip())


def problemas_fila(f, max_ruta):
    p = []
    acc = f.get("accion", "").strip()
    if acc not in ACCIONES:
        p.append(f"accion inválida o vacía: '{acc}'")
        return p
    if acc != "copiar":
        return p
    nombre, carpeta = f.get("nombre_nuevo", "").strip(), f.get("carpeta_destino", "").strip()
    if not nombre or not carpeta:
        p.append("falta carpeta_destino o nombre_nuevo")
        return p
    for parte in re.split(r"[/\\]", carpeta) + [nombre]:
        if PROHIBIDOS.search(parte):
            p.append(f"caracter prohibido en '{parte}'")
        if RESERVADOS.search(parte):
            p.append(f"nombre reservado '{parte}'")
        if parte != parte.strip() or parte.endswith("."):
            p.append(f"espacio o punto al borde en '{parte}'")
        if sin_tildes(parte) != parte.lower():
            p.append(f"tildes o ñ en '{parte}'")
    if len(nombre) > 120:
        p.append(f"nombre de {len(nombre)} caracteres (máx. 120)")
    if len(destino_de(f)) > max_ruta:
        p.append(f"ruta de {len(destino_de(f))} caracteres (máx. {max_ruta})")
    if os.path.splitext(nombre)[1].lower() != f.get("ext", "").lower() \
            and f.get("google_nativo") != "si" and f.get("exportado") != "si":
        p.append("la extensión nueva no coincide con la original")
    if f.get("sensible") == "alto" and not carpeta.replace("\\", "/").startswith("_RESTRINGIDO"):
        p.append("sensible=alto fuera de _RESTRINGIDO (confirmá que es intencional)")
    return p


def cmd_validar(a):
    filas = leer_csv(a.plan)
    errores = []
    destinos = defaultdict(list)
    for f in filas:
        for prob in problemas_fila(f, a.max_ruta):
            errores.append((f["id"], f["origen"], prob))
        if f.get("accion") == "copiar":
            destinos[destino_de(f).lower()].append(f["id"])
    for d, ids in destinos.items():
        if len(ids) > 1:
            errores.append((",".join(ids), d, "varios archivos con el mismo destino"))
    acciones = Counter(f.get("accion", "") or "(vacía)" for f in filas)
    aprob = Counter(sin_tildes(f.get("aprobado", "")).strip() or "(sin decidir)" for f in filas)
    conf = Counter(f.get("confianza", "") or "(vacía)" for f in filas if f.get("accion") == "copiar")
    print(f"Filas: {len(filas)}")
    print("Acciones: " + ", ".join(f"{k}={v}" for k, v in acciones.most_common()))
    print("Confianza (copiar): " + ", ".join(f"{k}={v}" for k, v in conf.most_common()))
    print("Aprobado: " + ", ".join(f"{k}={v}" for k, v in aprob.most_common()))
    print(f"Problemas: {len(errores)}")
    for e in errores[:200]:
        print(f"  [{e[0]}] {e[1]} → {e[2]}")
    if len(errores) > 200:
        print(f"  ... y {len(errores) - 200} más")
    if a.salida:
        escribir_csv(a.salida, [{"id": i, "origen": o, "problema": p} for i, o, p in errores],
                     ["id", "origen", "problema"])
    sys.exit(1 if errores else 0)


# ---------- migrar ----------

def cmd_migrar(a):
    filas = leer_csv(a.plan)
    origen, destino = os.path.abspath(a.origen), os.path.abspath(a.destino)
    try:
        anidados = os.path.commonpath([origen, destino]) in (origen, destino)
    except ValueError:  # distintas unidades (ej. G: y C:)
        anidados = False
    if anidados:
        sys.exit("Origen y destino no pueden estar uno dentro del otro.")
    aprobadas = [f for f in filas
                 if sin_tildes(f.get("aprobado", "")).strip() in ("si", "x", "ok")
                 and (f.get("accion") == "copiar" or (f.get("accion") == "exportar" and a.exportados))]
    if a.exportados:
        # Los nativos de Google ya exportados a Office (con el nombre_nuevo del plan) se copian desde ahí.
        for f in aprobadas:
            if f.get("accion") == "exportar":
                f["accion"], f["google_nativo"], f["exportado"] = "copiar", "no", "si"
                f["origen"] = os.path.join(os.path.abspath(a.exportados), f["nombre_nuevo"])  # ruta absoluta
    bloqueantes = [(f["id"], p) for f in aprobadas for p in problemas_fila(f, a.max_ruta)
                   if not p.startswith("sensible=alto")]
    if bloqueantes:
        for i, p in bloqueantes[:50]:
            print(f"  [{i}] {p}")
        sys.exit(f"{len(bloqueantes)} problemas en filas aprobadas: corregí el plan (validar) antes de migrar.")

    modo = "EJECUCIÓN" if a.ejecutar else "SIMULACIÓN (no se copia nada; agregá --ejecutar)"
    print(f"{modo}: {len(aprobadas)} filas aprobadas para copiar")
    marca = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    registro = []
    for i, f in enumerate(aprobadas, 1):
        src = os.path.join(origen, f["origen"])
        dst = os.path.join(destino, destino_de(f))
        r = {"fecha": dt.datetime.now().isoformat(timespec="seconds"), "id": f["id"],
             "origen": f["origen"], "destino": os.path.relpath(dst, destino), "sha256": "", "estado": ""}
        if f.get("google_nativo") == "si":
            r["estado"] = "exportar_manual (archivo nativo de Google)"
        elif not os.path.isfile(src):
            r["estado"] = "error: el original ya no está"
        elif os.path.exists(dst):
            same = a.ejecutar and sha256(src) == sha256(dst)
            r["estado"] = "ya_existe_identico" if same else "error: ya existe un archivo en el destino (no se sobrescribe)"
        elif not a.ejecutar:
            r["estado"] = "se_copiaria"
        else:
            try:
                h_src = f.get("sha256") or sha256(src)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                h_dst = sha256(dst)
                if h_dst != h_src:
                    os.remove(dst)  # es nuestra copia, nunca el original
                    r["estado"] = "error: la copia no coincide (se descartó la copia)"
                else:
                    r["sha256"], r["estado"] = h_dst, "copiado_verificado"
            except OSError as e:
                r["estado"] = f"error: {e.strerror}"
        registro.append(r)
        if i % 100 == 0:
            print(f"  {i}/{len(aprobadas)}", file=sys.stderr)
    nombre = f"{'migracion' if a.ejecutar else 'simulacion'}_{marca}.csv"
    escribir_csv(os.path.join(a.registro, nombre), registro,
                 ["fecha", "id", "origen", "destino", "sha256", "estado"])
    for estado, n in Counter(r["estado"].split(" (")[0] for r in registro).most_common():
        print(f"  {estado}: {n}")
    print(f"Registro → {os.path.join(a.registro, nombre)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("inventario"); x.add_argument("raiz"); x.add_argument("--salida", required=True)
    x.add_argument("--hash", choices=["auto", "todo", "no"], default="auto"); x.add_argument("--sensibles")
    x = s.add_parser("dividir"); x.add_argument("inventario"); x.add_argument("--salida", required=True)
    x.add_argument("--filas", type=int, default=400)
    x = s.add_parser("unir"); x.add_argument("dir_lotes"); x.add_argument("--salida", required=True)
    x = s.add_parser("validar"); x.add_argument("plan"); x.add_argument("--max-ruta", type=int, default=200)
    x.add_argument("--salida")
    x = s.add_parser("migrar"); x.add_argument("plan"); x.add_argument("--origen", required=True)
    x.add_argument("--destino", required=True); x.add_argument("--registro", required=True)
    x.add_argument("--ejecutar", action="store_true"); x.add_argument("--max-ruta", type=int, default=200)
    x.add_argument("--exportados", help="carpeta con los nativos de Google ya exportados, nombrados como nombre_nuevo")
    a = p.parse_args()
    {"inventario": cmd_inventario, "dividir": cmd_dividir, "unir": cmd_unir,
     "validar": cmd_validar, "migrar": cmd_migrar}[a.cmd](a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
