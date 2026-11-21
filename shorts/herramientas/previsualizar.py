#!/usr/bin/env python3
"""Vista previa rápida de un Short animado: dibuja cuadros sueltos sin generar el video.

Uso:
  python3 herramientas/previsualizar.py <carpeta> <archivo.json> <salida.png> [t1 t2 ...]

Sin tiempos, toma tres cuadros por escena (comienzo, mitad y final). Cada cuadro lleva arriba la
escena y el segundo, y abajo el texto del subtítulo que se verá en ese momento (aproximado: en el
video final lo dibuja ffmpeg con otra tipografía). Sirve para revisar composición, superposiciones
y sincronía con la voz en segundos en lugar de minutos.
"""
import math
import os
import sys

import cairo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motion  # noqa: E402
import render  # noqa: E402


def main(carpeta, archivo, salida, tiempos):
    pre = motion.preparar(carpeta, archivo)
    ini, dur = pre["inicios"], pre["duracion"]
    etiquetas = []
    if not tiempos:
        for k, a in enumerate(ini):
            b = ini[k + 1] if k + 1 < len(ini) else dur
            for t in (a + min(0.45, (b - a) * 0.3), (a + b) / 2, b - 0.2):
                tiempos.append(max(0.0, min(dur - 0.05, t)))
    subs = render.aplicar_reemplazos(pre["palabras"], pre["cfg"].get("reemplazos", {}))
    bloques = render.bloques_subtitulos(subs)
    y_sub = pre["cfg"].get("y_sub", 1350)
    esc = 0.3
    w, h = int(motion.W * esc), int(motion.H * esc)
    cols = min(len(tiempos), 9)
    filas = math.ceil(len(tiempos) / cols)
    hoja = cairo.ImageSurface(cairo.FORMAT_ARGB32, cols * w, filas * (h + 34))
    ch = cairo.Context(hoja)
    ch.set_source_rgb(0.05, 0.05, 0.07)
    ch.paint()
    sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, motion.W, motion.H)
    for n, t in enumerate(tiempos):
        cr = cairo.Context(sup)
        motion.dibujar_cuadro(cr, pre, t)
        # subtítulo aproximado del momento
        txt = ""
        for b in bloques:
            if b[0]["start"] - 0.05 <= t <= b[-1]["end"] + 0.25:
                txt = " ".join(p["text"] for p in b).upper()
        if txt:
            cr.new_path()
            motion.texto(cr, txt, motion.W / 2 + 4, y_sub + 4, 84, (0, 0, 0))
            motion.texto(cr, txt, motion.W / 2, y_sub, 84, (1, 1, 1))
        k = max(i for i, s in enumerate(ini) if s <= t + 1e-6)
        x, y = (n % cols) * w, (n // cols) * (h + 34)
        ch.save()
        ch.translate(x, y + 34)
        ch.scale(esc, esc)
        ch.set_source_surface(sup, 0, 0)
        ch.paint()
        ch.restore()
        ch.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ch.set_font_size(19)
        ch.set_source_rgb(1, 0.85, 0.5)
        ch.move_to(x + 8, y + 24)
        ch.show_text(f"esc {k + 1}  ·  {t:.1f} s")
        ch.new_path()
        etiquetas.append((k + 1, round(t, 2)))
    hoja.write_to_png(salida)
    print(f"Hoja: {salida} · {len(tiempos)} cuadros · duración {dur:.1f} s · inicios de escena: "
          + ", ".join(f"{k + 1}={s:.1f}" for k, s in enumerate(ini)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4:]])
