#!/usr/bin/env python3
"""Genera un clip vertical (1080x1920) con un gráfico de precio que se dibuja de forma animada.

Uso:  python3 herramientas/grafico_animado.py datos.json salida.mp4

datos.json:
{
  "titulo": "GAMESTOP (GME)",
  "nota": "Precio de cierre en dólares, antes del desdoblamiento de 2022",
  "duracion": 9,
  "puntos": [["04/01", 17.25], ["05/01", 17.37], ...],
  "destacados": [{"indice": 17, "valor": 483, "texto": "MÁXIMO: $483"}]
}
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONDO = "#0b0b0f"
DORADO = "#FFD700"
GRIS = "#8a8a99"


def suavizar(t):
    return t * t * (3 - 2 * t)


def main(ruta_datos, salida):
    d = json.load(open(ruta_datos))
    etiquetas = [p[0] for p in d["puntos"]]
    valores = [p[1] for p in d["puntos"]]
    n = len(valores)
    destacados = d.get("destacados", [])
    tope = max(valores + [x["valor"] for x in destacados]) * 1.15
    total = int(d.get("duracion", 9) * FPS)
    dibujo = int(total * 0.8)  # el 80 % del clip dibuja la línea; el resto la deja quieta

    tmp = tempfile.mkdtemp(prefix="grafico_")
    try:
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=FONDO)
        for f in range(total):
            fig.clf()
            ax = fig.add_axes([0.13, 0.42, 0.8, 0.30], facecolor=FONDO)
            prog = suavizar(min(1.0, f / dibujo)) * (n - 1)
            hasta = int(prog)
            frac = prog - hasta
            xs = list(range(hasta + 1))
            ys = valores[: hasta + 1]
            if hasta < n - 1:
                xs.append(hasta + frac)
                ys.append(valores[hasta] + (valores[hasta + 1] - valores[hasta]) * frac)
            ax.fill_between(xs, ys, color=DORADO, alpha=0.12)
            ax.plot(xs, ys, color=DORADO, lw=7, solid_capstyle="round")
            ax.scatter([xs[-1]], [ys[-1]], s=420, color=DORADO, zorder=5)
            ax.set_xlim(-0.3, n - 0.7)
            ax.set_ylim(0, tope)
            for lado in ("top", "right"):
                ax.spines[lado].set_visible(False)
            for lado in ("left", "bottom"):
                ax.spines[lado].set_color(GRIS)
            ax.tick_params(colors=GRIS, labelsize=22)
            paso = max(1, n // 5)
            ax.set_xticks(range(0, n, paso))
            ax.set_xticklabels(etiquetas[::paso])
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
            ax.grid(axis="y", color="#26262e", lw=1.5)

            # Precio actual en grande, encima del gráfico.
            fig.text(0.5, 0.79, f"${ys[-1]:,.0f}", color="white", fontsize=110, fontweight="bold",
                     ha="center", va="center")
            fig.text(0.5, 0.865, d["titulo"], color=DORADO, fontsize=48, fontweight="bold",
                     ha="center", va="center")
            fig.text(0.5, 0.07, d.get("nota", ""), color=GRIS, fontsize=24, ha="center", va="center", linespacing=1.4)

            for x in destacados:
                if prog >= x["indice"]:
                    ax.scatter([x["indice"]], [x["valor"]], s=700, color="#ff3b3b", zorder=6)
                    ax.annotate(x["texto"], (x["indice"], x["valor"]), xytext=(-20, 30),
                                textcoords="offset points", color="#ff3b3b", fontsize=30,
                                fontweight="bold", ha="right")
            fig.savefig(os.path.join(tmp, f"f{f:04d}.png"), facecolor=FONDO)
        plt.close(fig)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i",
                        os.path.join(tmp, "f%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "18", salida], check=True)
        print("Listo:", salida)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
