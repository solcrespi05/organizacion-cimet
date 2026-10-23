"""Convierte un .docx a Markdown simple usando solo la biblioteca estándar.

Uso: python docx_a_texto.py <archivo.docx> [salida.md]

- Títulos (estilos Heading/Título) -> #, ##, ...
- Tablas -> tablas Markdown.
- Control de cambios: el texto insertado se conserva; el borrado se omite
  (se informa cuántos cambios sin aceptar había).
- Comentarios de Word -> notas [COMENTARIO de <autor>: ...] al final del párrafo.
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def texto_run(elem):
    partes = []
    for nodo in elem.iter():
        if nodo.tag == W + "t":
            partes.append(nodo.text or "")
        elif nodo.tag == W + "tab":
            partes.append("\t")
        elif nodo.tag in (W + "br", W + "cr"):
            partes.append("\n")
    return "".join(partes)


def cargar_comentarios(z):
    if "word/comments.xml" not in z.namelist():
        return {}
    raiz = ET.fromstring(z.read("word/comments.xml"))
    comentarios = {}
    for c in raiz.findall(W + "comment"):
        texto = " ".join(texto_run(p) for p in c.findall(W + "p")).strip()
        comentarios[c.get(W + "id")] = (c.get(W + "author") or "?", texto)
    return comentarios


def nivel_titulo(p):
    estilo = p.find(f"{W}pPr/{W}pStyle")
    if estilo is None:
        return 0
    m = re.search(r"(?:heading|ttulo|titulo)\s*(\d)", (estilo.get(W + "val") or "").lower())
    return int(m.group(1)) if m else 0


def parrafo(p, comentarios, stats):
    partes, notas = [], []
    for hijo in p:
        if hijo.tag == W + "r":
            partes.append(texto_run(hijo))
        elif hijo.tag in (W + "ins", W + "hyperlink", W + "smartTag", W + "sdt"):
            if hijo.tag == W + "ins":
                stats["ins"] += 1
            partes.append(texto_run(hijo))
        elif hijo.tag == W + "del":
            stats["del"] += 1
        elif hijo.tag == W + "commentRangeStart":
            cid = hijo.get(W + "id")
            if cid in comentarios:
                autor, texto = comentarios[cid]
                notas.append(f"[COMENTARIO de {autor}: {texto}]")
    texto = "".join(partes).strip()
    nivel = nivel_titulo(p)
    if texto and nivel:
        texto = "#" * nivel + " " + texto
    if notas:
        texto = (texto + " " + " ".join(notas)).strip()
    return texto


def tabla(t, comentarios, stats):
    filas = []
    for tr in t.findall(W + "tr"):
        celdas = []
        for tc in tr.findall(W + "tc"):
            txt = " ".join(parrafo(p, comentarios, stats) for p in tc.findall(W + "p"))
            celdas.append(txt.replace("|", "\\|").strip())
        filas.append("| " + " | ".join(celdas) + " |")
    if filas:
        n = filas[0].count("|") - 1
        filas.insert(1, "|" + "---|" * n)
    return "\n".join(filas)


def convertir(ruta):
    with zipfile.ZipFile(ruta) as z:
        comentarios = cargar_comentarios(z)
        cuerpo = ET.fromstring(z.read("word/document.xml")).find(W + "body")
    stats = {"ins": 0, "del": 0}
    bloques = []
    for elem in cuerpo:
        if elem.tag == W + "p":
            bloques.append(parrafo(elem, comentarios, stats))
        elif elem.tag == W + "tbl":
            bloques.append(tabla(elem, comentarios, stats))
    md = re.sub(r"\n{3,}", "\n\n", "\n\n".join(bloques)).strip() + "\n"
    aviso = []
    if stats["ins"] or stats["del"]:
        aviso.append(f"<!-- control de cambios sin aceptar: {stats['ins']} inserciones (incluidas), "
                     f"{stats['del']} borrados (omitidos) -->")
    if comentarios:
        aviso.append(f"<!-- {len(comentarios)} comentarios de Word incluidos como [COMENTARIO ...] -->")
    return "\n".join(aviso + [md])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    salida = convertir(sys.argv[1])
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(salida)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(salida)
