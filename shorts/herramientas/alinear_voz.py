#!/usr/bin/env python3
"""Ajusta un video largo a una voz grabada por una persona.

Uso: python3 herramientas/alinear_voz.py <carpeta_largo> <carpeta_audio>

En <carpeta_audio> espera `voz-original.mp3` y `stt.json` (transcripción de ElevenLabs con tiempos
por palabra). Opcional: `cortes.json` = {"tomas_malas": [[palabra_desde, palabra_hasta], ...]} con
índices de palabras de la transcripción que se eliminan (hasta = primera palabra que se conserva).

Hace tres cosas:
  1. Recorta las tomas malas y acorta las pausas largas -> `voz-final.mp3`.
  2. Busca en la transcripción dónde empieza cada frase del guion (`largo.json`).
  3. Guarda `tiempos.json` en la carpeta del video; `largo.py` lo usa en lugar del ritmo teórico.
"""
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata

PAUSA_MAX = 1.1    # las pausas más largas se acortan...
PAUSA_DEJA = 0.75  # ...a esta duración
MARGEN = 0.12      # aire antes de la palabra donde se retoma tras un corte


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def main(carpeta, dir_audio):
    stt = json.load(open(os.path.join(dir_audio, "stt.json")))
    pal = [p for p in stt["words"] if p["type"] == "word"]
    ruta_cortes = os.path.join(dir_audio, "cortes.json")
    malas = json.load(open(ruta_cortes))["tomas_malas"] if os.path.exists(ruta_cortes) else []
    quitar = set()
    cortes = []  # intervalos de audio que se eliminan
    for a, b in malas:
        quitar.update(range(a, b))
        cortes.append((pal[a]["start"] - MARGEN, pal[b]["start"] - MARGEN))
    vivas = [i for i in range(len(pal)) if i not in quitar]
    for i, j in zip(vivas, vivas[1:]):
        if j != i + 1:
            continue  # ahí ya hay un corte de toma mala
        hueco = pal[j]["start"] - pal[i]["end"]
        if hueco > PAUSA_MAX:
            sobra = hueco - PAUSA_DEJA
            cortes.append((pal[i]["end"] + PAUSA_DEJA / 2, pal[i]["end"] + PAUSA_DEJA / 2 + sobra))
    ini = max(0.0, pal[vivas[0]]["start"] - 0.35)
    fin = pal[vivas[-1]]["end"] + 0.9
    cortes = sorted(cortes)
    tramos, t = [], ini
    for a, b in cortes:
        if a > t:
            tramos.append((t, a))
        t = max(t, b)
    tramos.append((t, fin))

    def nuevo(x):
        """Tiempo del audio original -> tiempo en el audio recortado."""
        acum = 0.0
        for a, b in tramos:
            if x <= b:
                return acum + max(0.0, x - a)
            acum += b - a
        return acum

    filtro = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,"
                     f"afade=t=out:st={b - a - 0.02:.3f}:d=0.02[s{n}];" for n, (a, b) in enumerate(tramos))
    filtro += "".join(f"[s{n}]" for n in range(len(tramos))) + f"concat=n={len(tramos)}:v=0:a=1[a]"
    salida = os.path.join(dir_audio, "voz-final.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(dir_audio, "voz-original.mp3"),
                    "-filter_complex", filtro, "-map", "[a]", "-b:a", "160k", salida], check=True)
    total = sum(b - a for a, b in tramos)

    # alineación guion <-> transcripción
    escenas = json.load(open(os.path.join(carpeta, "largo.json")))["escenas"]
    guion, inicio_frase = [], []
    for e in escenas:
        for f in e["frases"]:
            inicio_frase.append(len(guion))
            guion += [norm(x) for x in f.split() if norm(x)]
    dicho = [norm(pal[i]["text"]) for i in vivas]
    sm = difflib.SequenceMatcher(None, guion, dicho, autojunk=False)
    par = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            par[blk.a + k] = blk.b + k
    tiempos, sin_ancla, n = [], 0, 0
    for e in escenas:
        fila = []
        for _ in e["frases"]:
            g = inicio_frase[n]
            tope = inicio_frase[n + 1] if n + 1 < len(inicio_frase) else len(guion)
            ancla = next((k for k in range(g, tope) if k in par), None)
            if ancla is None:
                sin_ancla += 1
                fila.append(None)
            else:
                d = max(0, par[ancla] - (ancla - g))
                fila.append(round(nuevo(pal[vivas[d]]["start"]), 2))
            n += 1
        tiempos.append(fila)
    json.dump({"total": round(total, 2), "frases": tiempos},
              open(os.path.join(carpeta, "tiempos.json"), "w"), indent=1)
    print(f"Voz final: {total / 60:.2f} min ({len(tramos) - 1} cortes). Coincidencia guion/voz: "
          f"{sm.ratio():.0%}. Frases sin ancla: {sin_ancla}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
