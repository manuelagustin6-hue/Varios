#!/usr/bin/env python3
"""Arma un Short vertical (1080x1920) a partir de una carpeta de producción.

Uso:  python3 herramientas/render.py produccion/001

La carpeta debe contener:
  config.json   escenas, textos destacados y reemplazos para los subtítulos
  palabras.json transcripción con marcas de tiempo por palabra (ElevenLabs)
  img/          imágenes de fondo

Genera produccion/NNN/video.mp4.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

from PIL import Image

W, H, FPS = 1080, 1920, 30
MAX_PLANO = 3.6          # segundos máximos por plano antes de cortar
FUENTE = "Liberation Sans"
DIR_FUENTES = "/usr/share/fonts/truetype/liberation"
AMARILLO = "&H0000D7FF&"  # #FFD700 en formato BGR de ASS
MARCA = "@datomillonario"


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9% ]", "", t).strip()


def cargar_palabras(ruta):
    datos = json.load(open(ruta))
    return [p for p in datos["words"] if p["type"] == "word"]


def buscar(palabras, frase, desde=0):
    """Índice de la primera palabra donde empieza `frase`, a partir de `desde`."""
    objetivo = normalizar(frase).split()
    norm = [normalizar(p["text"]) for p in palabras]
    for i in range(desde, len(palabras) - len(objetivo) + 1):
        if norm[i:i + len(objetivo)] == objetivo:
            return i
    raise SystemExit(f"No encontré la frase: {frase!r}")


def aplicar_reemplazos(palabras, reemplazos):
    """Une secuencias de palabras en un solo token (p. ej. «cincuenta millones» → «50 millones»)."""
    salida, i = [], 0
    reglas = [(normalizar(k).split(), v) for k, v in reemplazos.items()]
    while i < len(palabras):
        for patron, texto in reglas:
            tramo = [normalizar(p["text"]) for p in palabras[i:i + len(patron)]]
            if tramo == patron:
                ultimo = palabras[i + len(patron) - 1]
                puntuacion = re.sub(r"^.*?([.,;:!?»\"…]*)$", r"\1", ultimo["text"])
                salida.append({"text": texto + puntuacion, "start": palabras[i]["start"], "end": ultimo["end"]})
                i += len(patron)
                break
        else:
            salida.append(palabras[i])
            i += 1
    return salida


def tiempo_ass(s):
    s = max(0, s)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def bloques_subtitulos(palabras):
    """Agrupa de a 1–3 palabras, cortando en pausas y signos de puntuación."""
    bloques, actual = [], []
    for i, p in enumerate(palabras):
        if actual and len(" ".join(x["text"] for x in actual + [p])) > 16:
            bloques.append(actual)
            actual = []
        actual.append(p)
        siguiente = palabras[i + 1] if i + 1 < len(palabras) else None
        corte = (
            len(actual) == 3
            or re.search(r"[.,;:!?…]$", p["text"])
            or (siguiente and siguiente["start"] - p["end"] > 0.35)
        )
        if corte or not siguiente:
            bloques.append(actual)
            actual = []
    return bloques


def generar_ass(palabras, textos, duracion, ruta):
    estilos = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FUENTE},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Titulo,{FUENTE},74,&H00000000,&H00000000,&H0000D7FF,&H0000D7FF,-1,0,0,0,100,100,0,0,3,22,0,8,70,70,0,1
Style: Marca,{FUENTE},40,&H50FFFFFF,&H50FFFFFF,&H64000000,&H00000000,-1,0,0,0,100,100,1,0,1,2,0,8,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    eventos = [f"Dialogue: 0,{tiempo_ass(0)},{tiempo_ass(duracion)},Marca,,0,0,0,,{{\\pos(540,150)}}{MARCA}"]

    # Subtítulos palabra por palabra, con la palabra actual resaltada en amarillo.
    bloques = bloques_subtitulos(palabras)
    for b_i, bloque in enumerate(bloques):
        fin_bloque = bloque[-1]["end"]
        if b_i + 1 < len(bloques):
            prox = bloques[b_i + 1][0]["start"]
            fin_bloque = prox if prox - fin_bloque < 0.4 else fin_bloque + 0.15
        # Sin comas, puntos ni comillas rectas: en pantalla se lee más limpio.
        textos_b = [re.sub(r'[,.;:"]+$', "", p["text"].replace('"', "")).upper() for p in bloque]
        for j, p in enumerate(bloque):
            ini = p["start"]
            fin = bloque[j + 1]["start"] if j + 1 < len(bloque) else fin_bloque
            partes = [
                (f"{{\\c{AMARILLO}}}{t}{{\\c&H00FFFFFF&}}" if k == j else t)
                for k, t in enumerate(textos_b)
            ]
            # Achica la letra si el bloque es muy largo para el ancho de pantalla.
            largo = len(" ".join(textos_b))
            tam = 92 if largo <= 16 else max(60, int(92 * 16 / largo))
            pop = "{\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}" if j == 0 else ""
            eventos.append(
                f"Dialogue: 1,{tiempo_ass(ini)},{tiempo_ass(fin)},Sub,,0,0,0,,"
                f"{{\\pos(540,1260)\\fs{tam}}}{pop}{' '.join(partes)}"
            )

    # Títulos destacados en la parte superior.
    for t in textos:
        texto = t["texto"].replace("\n", "\\N")
        eventos.append(
            f"Dialogue: 2,{tiempo_ass(t['ini'])},{tiempo_ass(t['fin'])},Titulo,,0,0,0,,"
            f"{{\\pos(540,330)\\fad(120,120)\\fscx85\\fscy85\\t(0,120,\\fscx100\\fscy100)}}{texto}"
        )
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(estilos + "\n".join(eventos) + "\n")


def preparar_imagen(origen, destino):
    """Recorta la imagen a 9:16 y la agranda al doble para que el zoom sea suave."""
    img = Image.open(origen).convert("RGB")
    ratio = W / H
    w, h = img.size
    if w / h > ratio:
        nw = int(h * ratio)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / ratio)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img.resize((W * 2, H * 2), Image.LANCZOS).save(destino, quality=95)


def renderizar_plano(imagen, duracion, variante, destino):
    n = max(1, round(duracion * FPS))
    if variante % 2 == 0:   # acercamiento lento desde el plano general
        z = f"1+0.10*on/{n}"
    else:                   # alejamiento desde un plano más cerrado
        z = f"1.30-0.10*on/{n}"
    desplazamiento = ["0", "0.04", "-0.04"][variante % 3]
    x = f"(iw-iw/zoom)/2+iw*{desplazamiento}*on/{n}"
    y = "(ih-ih/zoom)/2"
    filtro = (
        f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},"
        f"eq=brightness=-0.04:saturation=1.08,vignette=PI/5,format=yuv420p"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", imagen, "-vf", filtro,
         "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", destino],
        check=True,
    )


def main(carpeta):
    cfg = json.load(open(os.path.join(carpeta, "config.json")))
    palabras = cargar_palabras(os.path.join(carpeta, "palabras.json"))
    audio = os.path.normpath(os.path.join(carpeta, cfg["audio"]))
    duracion = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]))

    # Tiempos de inicio de cada escena, según la frase en la que empieza.
    inicios, cursor = [], 0
    for k, esc in enumerate(cfg["escenas"]):
        if k == 0:
            inicios.append(0.0)
            continue
        idx = buscar(palabras, esc["desde"], cursor)
        cursor = idx
        inicios.append(palabras[idx]["start"])
    fines = inicios[1:] + [duracion]

    # Títulos destacados.
    textos, cursor = [], 0
    for t in cfg.get("textos", []):
        i0 = buscar(palabras, t["desde"], cursor) if t["desde"] != "INICIO" else 0
        ini = 0.0 if t["desde"] == "INICIO" else palabras[i0]["start"]
        if t["hasta"] == "FIN":
            fin = duracion
        else:
            i1 = buscar(palabras, t["hasta"], i0 + 1)
            fin = palabras[i1]["start"]
        cursor = i0
        textos.append({"texto": t["texto"], "ini": ini, "fin": fin})

    tmp = tempfile.mkdtemp(prefix="render_")
    try:
        preparadas = {}
        planos, variante = [], 0
        for esc, ini, fin in zip(cfg["escenas"], inicios, fines):
            origen = os.path.join(carpeta, esc["imagen"])
            if origen not in preparadas:
                destino = os.path.join(tmp, f"img{len(preparadas)}.jpg")
                preparar_imagen(origen, destino)
                preparadas[origen] = destino
            total = fin - ini
            partes = max(1, int(-(-total // MAX_PLANO)))
            for p in range(partes):
                archivo = os.path.join(tmp, f"plano{len(planos):03d}.mp4")
                renderizar_plano(preparadas[origen], total / partes, variante, archivo)
                planos.append(archivo)
                variante += 1

        lista = os.path.join(tmp, "lista.txt")
        with open(lista, "w") as f:
            f.writelines(f"file '{p}'\n" for p in planos)
        fondo = os.path.join(tmp, "fondo.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                        "-c", "copy", fondo], check=True)

        subs = aplicar_reemplazos(palabras, cfg.get("reemplazos", {}))
        ass = os.path.join(tmp, "subs.ass")
        generar_ass(subs, textos, duracion, ass)
        shutil.copy(ass, os.path.join(carpeta, "subtitulos.ass"))

        salida = os.path.join(carpeta, "video.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", fondo, "-i", audio,
            "-vf", f"ass={ass}:fontsdir={DIR_FUENTES}",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-map", "0:v", "-map", "1:a", "-t", f"{duracion:.2f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", salida,
        ], check=True)
        print(f"Listo: {salida} ({duracion:.1f} s, {len(planos)} planos)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1])
