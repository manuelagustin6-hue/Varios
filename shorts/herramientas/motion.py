#!/usr/bin/env python3
"""Arma un Short 100 % con código: ilustraciones planas y animaciones vectoriales (sin imágenes).

Uso:  python3 herramientas/motion.py produccion/NNN

La carpeta debe contener:
  motion.json   lista de escenas (tipo, frase de inicio y parámetros)
  palabras.json transcripción con marcas de tiempo por palabra
Genera produccion/NNN/video-motion.mp4.

Tipos de escena: cifra, icono, iconos (varios repetidos), sello, linea_tiempo, versus, grafico.
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile

import cairo

sys.path.insert(0, os.path.dirname(__file__))
import render  # noqa: E402  (reutiliza subtítulos, búsqueda de frases y recortes)

W, H, FPS = 1080, 1920, 30
FUENTE = "Liberation Sans"

# Paleta de la marca
FONDO1 = (0.055, 0.09, 0.15)
FONDO2 = (0.02, 0.035, 0.07)
DORADO = (1.0, 0.82, 0.29)
BLANCO = (1, 1, 1)
GRIS = (0.55, 0.6, 0.68)
ROJO = (1.0, 0.3, 0.3)
VERDE = (0.24, 0.86, 0.52)
AZUL = (0.25, 0.55, 1.0)
OSCURO = (0.08, 0.1, 0.16)


# ---------- utilidades ----------

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def texto(cr, s, x, y, tam, color=BLANCO, alinear="centro", alfa=1.0):
    cr.select_font_face(FUENTE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(tam)
    ext = cr.text_extents(s)
    if alinear == "centro":
        x0 = x - (ext.width / 2 + ext.x_bearing)
    elif alinear == "derecha":
        x0 = x - ext.width - ext.x_bearing
    else:
        x0 = x - ext.x_bearing
    cr.set_source_rgba(*color, alfa)
    cr.move_to(x0, y - (ext.height / 2 + ext.y_bearing))
    cr.show_text(s)
    return ext.width


def ancho_texto(cr, s, tam):
    cr.select_font_face(FUENTE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(tam)
    return cr.text_extents(s).width


def rrect(cr, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def rellenar(cr, color, alfa=1.0):
    cr.set_source_rgba(*color, alfa)
    cr.fill()


def titular(cr, s, t, y=330):
    """Cartel amarillo de la marca, entra con efecto de golpe."""
    if not s:
        return
    lineas = s.split("\n")
    tam = 84
    while max(ancho_texto(cr, l, tam) for l in lineas) > 900 and tam > 44:
        tam -= 4
    esc = 0.6 + 0.4 * ease_out_back(t / 0.35)
    alto = tam * 1.25 * len(lineas) + 40
    ancho = max(ancho_texto(cr, l, tam) for l in lineas) + 70
    cr.save()
    cr.translate(W / 2, y)
    cr.scale(esc, esc)
    rrect(cr, -ancho / 2, -alto / 2, ancho, alto, 18)
    rellenar(cr, DORADO)
    for i, l in enumerate(lineas):
        yy = -alto / 2 + 20 + tam * 1.25 * (i + 0.5)
        texto(cr, l, 0, yy, tam, OSCURO)
    cr.restore()


def fondo(cr, tg):
    """Degradado oscuro con partículas que flotan lento: siempre hay movimiento."""
    g = cairo.RadialGradient(W / 2, H * 0.42, 50, W / 2, H * 0.42, H * 0.8)
    g.add_color_stop_rgb(0, *FONDO1)
    g.add_color_stop_rgb(1, *FONDO2)
    cr.set_source(g)
    cr.paint()
    rnd = random.Random(7)
    for _ in range(40):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        vel, r = rnd.uniform(8, 30), rnd.uniform(2, 5)
        y = (y0 - tg * vel) % H
        cr.arc(x0 + math.sin(tg * 0.5 + x0) * 10, y, r, 0, 2 * math.pi)
        rellenar(cr, DORADO, 0.08)


# ---------- ilustraciones (centradas en 0,0; tamaño base ~400 px) ----------

def ic_dvd(cr, t):
    cr.save()
    cr.rotate(t * 1.5)
    g = cairo.LinearGradient(-200, -200, 200, 200)
    for i, c in enumerate([(0.85, 0.85, 0.9), (0.6, 0.8, 1), (1, 0.7, 0.9), (1, 0.95, 0.6), (0.85, 0.85, 0.9)]):
        g.add_color_stop_rgb(i / 4, *c)
    cr.arc(0, 0, 200, 0, 2 * math.pi)
    cr.set_source(g)
    cr.fill()
    cr.arc(0, 0, 60, 0, 2 * math.pi)
    rellenar(cr, (0.7, 0.72, 0.78))
    cr.arc(0, 0, 25, 0, 2 * math.pi)
    rellenar(cr, FONDO1)
    cr.restore()


def ic_sobre(cr, t):
    rrect(cr, -230, -150, 460, 300, 16)
    rellenar(cr, (0.85, 0.12, 0.15))
    cr.move_to(-230, -140)
    cr.line_to(0, 40)
    cr.line_to(230, -140)
    cr.set_line_width(14)
    cr.set_source_rgb(0.6, 0.05, 0.08)
    cr.stroke()
    # disco que asoma
    cr.save()
    cr.translate(120, -150 - 60 * ease_out_cubic(t / 0.6))
    cr.scale(0.45, 0.45)
    ic_dvd(cr, t)
    cr.restore()


def ic_tienda(cr, t, color=AZUL, cartel=""):
    rrect(cr, -220, -120, 440, 300, 10)
    rellenar(cr, (0.92, 0.92, 0.95))
    # toldo a rayas
    for i in range(8):
        cr.rectangle(-240 + i * 60, -170, 60, 60)
        rellenar(cr, color if i % 2 == 0 else (1, 1, 1))
    rrect(cr, -180, -250, 360, 80, 10)
    rellenar(cr, color)
    if cartel:
        texto(cr, cartel, 0, -210, 40, (1, 0.9, 0.2))
    cr.rectangle(-50, 40, 100, 140)
    rellenar(cr, (0.3, 0.35, 0.45))
    for x in (-180, 80):
        cr.rectangle(x, -80, 100, 100)
        rellenar(cr, (0.55, 0.75, 0.95))


def ic_avion(cr, t):
    cr.save()
    cr.rotate(-0.35)
    cr.translate(-60 + 120 * ease_in_out(t / 1.5), 0)
    rrect(cr, -220, -30, 440, 60, 30)
    rellenar(cr, BLANCO)
    cr.move_to(-40, -20); cr.line_to(60, -170); cr.line_to(110, -170); cr.line_to(60, -20)
    rellenar(cr, (0.8, 0.85, 0.95))
    cr.move_to(-40, 20); cr.line_to(60, 170); cr.line_to(110, 170); cr.line_to(60, 20)
    rellenar(cr, (0.8, 0.85, 0.95))
    cr.move_to(-200, -20); cr.line_to(-170, -100); cr.line_to(-140, -100); cr.line_to(-150, -20)
    rellenar(cr, DORADO)
    for i in range(5):
        cr.arc(-80 + i * 45, -5, 9, 0, 2 * math.pi)
        rellenar(cr, AZUL)
    cr.restore()


def ic_risa(cr, t):
    for i, (x, y, s) in enumerate([(-150, -60, 1.0), (150, 40, 0.85), (-40, 150, 0.7)]):
        a = ease_out_back((t - i * 0.2) / 0.35)
        if a <= 0:
            continue
        cr.save()
        cr.translate(x, y + math.sin(t * 6 + i) * 8)
        cr.scale(s * a, s * a)
        rrect(cr, -150, -80, 300, 160, 40)
        rellenar(cr, BLANCO)
        cr.move_to(-60, 70); cr.line_to(-100, 130); cr.line_to(-10, 75)
        rellenar(cr, BLANCO)
        texto(cr, "JA JA", 0, 0, 70, OSCURO)
        cr.restore()


def ic_pantalla(cr, t):
    rrect(cr, -260, -170, 520, 320, 20)
    rellenar(cr, (0.12, 0.14, 0.2))
    rrect(cr, -240, -150, 480, 280, 12)
    rellenar(cr, (0.6, 0.06, 0.1))
    p = 1 + 0.08 * math.sin(t * 5)
    cr.save()
    cr.scale(p, p)
    cr.move_to(-45, -70); cr.line_to(75, -10); cr.line_to(-45, 50)
    rellenar(cr, BLANCO)
    cr.restore()
    cr.rectangle(-60, 150, 120, 40)
    rellenar(cr, (0.3, 0.32, 0.4))
    rrect(cr, -150, 185, 300, 22, 10)
    rellenar(cr, (0.3, 0.32, 0.4))


def ic_pinos(cr, t):
    for x, s in [(-300, 0.8), (300, 0.9), (-380, 0.6), (380, 0.65)]:
        cr.save()
        cr.translate(x, 60)
        cr.scale(s, s)
        for k in range(3):
            cr.move_to(0, -260 + k * 70); cr.line_to(-110 + k * -10, -90 + k * 80); cr.line_to(110 + k * 10, -90 + k * 80)
            rellenar(cr, (0.13, 0.42, 0.28))
        cr.rectangle(-18, 70, 36, 60)
        rellenar(cr, (0.4, 0.27, 0.15))
        cr.restore()


def ic_dinero(cr, t):
    for i in range(6):
        a = ease_out_back((t - i * 0.08) / 0.3)
        if a <= 0:
            continue
        cr.save()
        cr.translate(0, 120 - i * 45 * a)
        rrect(cr, -200, -45, 400, 90, 10)
        rellenar(cr, (0.2, 0.6, 0.35))
        rrect(cr, -180, -30, 360, 60, 8)
        cr.set_line_width(4)
        cr.set_source_rgb(0.6, 0.9, 0.65)
        cr.stroke()
        texto(cr, "$", 0, 0, 50, (0.75, 0.95, 0.8))
        cr.restore()


ICONOS = {"dvd": ic_dvd, "sobre": ic_sobre, "tienda": ic_tienda, "avion": ic_avion, "risa": ic_risa,
          "pantalla": ic_pantalla, "dinero": ic_dinero}


def dibujar_icono(cr, nombre, t, x, y, escala, **kw):
    if escala <= 0.001:  # todavía no apareció (una escala cero rompe la librería de dibujo)
        return
    cr.save()
    cr.translate(x, y)
    cr.scale(escala, escala)
    if nombre == "tienda_pinos":
        ic_pinos(cr, t)
        ic_tienda(cr, t, **kw)
    else:
        ICONOS[nombre](cr, t, **kw) if kw else ICONOS[nombre](cr, t)
    cr.restore()


# ---------- tipos de escena ----------

def esc_icono(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    a = ease_out_back(t / 0.45)
    flot = math.sin(t * 2.2) * 12
    kw = {k: v for k, v in p.items() if k in ("cartel",)}
    if "color" in p:
        kw["color"] = tuple(p["color"])
    dibujar_icono(cr, p["icono"], t, W / 2, 790 + flot, 1.4 * a, **kw)
    if p.get("pie"):
        texto(cr, p["pie"], W / 2, 1130, 60, p.get("color_pie") and tuple(p["color_pie"]) or GRIS,
              alfa=ease_out_cubic((t - 0.3) / 0.3))


def esc_cifra(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    if p.get("icono"):
        dibujar_icono(cr, p["icono"], t, W / 2, 1040, 0.62 * ease_out_back(t / 0.4))
    k = ease_out_cubic(t / p.get("cuenta", 1.2))
    v = p.get("de", 0) + (p["a"] - p.get("de", 0)) * k
    num = f"{p.get('prefijo', '')}{v:,.0f}".replace(",", ".") + p.get("sufijo", "")
    esc = 1 + 0.06 * math.sin(clamp(t / 0.25) * math.pi)
    cr.save()
    cr.translate(W / 2, 660)
    cr.scale(esc, esc)
    tam = 260
    while ancho_texto(cr, num, tam) > 980:
        tam -= 6
    texto(cr, num, 0, 0, tam, tuple(p.get("color", DORADO)))
    cr.restore()
    if p.get("unidad"):
        texto(cr, p["unidad"], W / 2, 820, 68, BLANCO, alfa=ease_out_cubic((t - 0.2) / 0.3))


def esc_iconos(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    n, cols = p.get("cantidad", 12), p.get("columnas", 4)
    filas = math.ceil(n / cols)
    esc = p.get("escala", 0.36)
    dx, dy = 245, 230
    x0 = W / 2 - (cols - 1) * dx / 2
    y0 = 800 - (filas - 1) * dy / 2
    for i in range(n):
        a = ease_out_back((t - i * 0.06) / 0.3)
        if a <= 0:
            continue
        dibujar_icono(cr, p["icono"], t, x0 + (i % cols) * dx, y0 + (i // cols) * dy, esc * a)


def esc_sello(cr, t, p):
    base = dict(p.get("base", {}))
    tipo = base.pop("tipo", "cifra")
    ESCENAS[tipo](cr, t + p.get("desfase", 2.0), base)
    a = clamp(t / 0.18)
    esc = 2.2 - 1.2 * ease_out_cubic(a)
    cr.save()
    cr.translate(W / 2, 760)
    cr.rotate(-0.18)
    cr.scale(esc, esc)
    tam = 110
    w = ancho_texto(cr, p["texto"], tam) + 80
    rrect(cr, -w / 2, -95, w, 190, 20)
    cr.set_line_width(16)
    cr.set_source_rgba(*ROJO, a)
    cr.stroke()
    texto(cr, p["texto"], 0, 0, tam, ROJO, alfa=a)
    cr.restore()


def esc_linea_tiempo(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    anios = p["anios"]
    x0, x1, y = 160, W - 160, 850
    prog = ease_in_out(t / 1.2)
    cr.set_line_width(12)
    cr.set_source_rgba(*GRIS, 0.5)
    cr.move_to(x0, y); cr.line_to(x1, y); cr.stroke()
    cr.set_source_rgb(*DORADO)
    cr.move_to(x0, y); cr.line_to(x0 + (x1 - x0) * prog, y); cr.stroke()
    for i, (anio, etiqueta, color) in enumerate(anios):
        f = i / (len(anios) - 1)
        x = x0 + (x1 - x0) * f
        vis = prog >= f - 0.01
        cr.arc(x, y, 34 if vis else 22, 0, 2 * math.pi)
        rellenar(cr, tuple(color) if vis else GRIS)
        texto(cr, str(anio), x, y - 120, 96, BLANCO if vis else GRIS)
        if vis and etiqueta:
            texto(cr, etiqueta, x, y + 120, 66, tuple(color), alfa=ease_out_cubic((prog - f) / 0.2 + 0.3))


def esc_versus(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    for lado, s in ((-1, p["izq"]), (1, p["der"])):
        a = ease_out_back((t - (0 if lado < 0 else 0.25)) / 0.4)
        if a <= 0:
            continue
        x = W / 2 + lado * 260
        dibujar_icono(cr, s["icono"], t, x, 820, 0.55 * a)
        texto(cr, s["texto"], x, 1080, 56, tuple(s.get("color", BLANCO)))
    texto(cr, "VS", W / 2, 820, 90, DORADO, alfa=ease_out_cubic((t - 0.4) / 0.3))


def esc_grafico(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    vals = p["valores"]
    n = len(vals)
    x0, x1, y0, y1 = 140, W - 140, 1080, 600
    vmax = max(vals) * 1.1
    prog = ease_in_out(t / p.get("dibujo", 1.6)) * (n - 1)
    cr.set_line_width(3)
    cr.set_source_rgba(*GRIS, 0.4)
    cr.move_to(x0, y0); cr.line_to(x1, y0); cr.stroke()
    pts = []
    for i in range(n):
        if i > prog + 1:
            break
        v = vals[i] if i <= prog else vals[i - 1] + (vals[i] - vals[i - 1]) * (prog - (i - 1))
        xi = min(i, prog)
        pts.append((x0 + (x1 - x0) * xi / (n - 1), y0 - (y0 - y1) * v / vmax))
    if len(pts) > 1:
        cr.move_to(*pts[0])
        for q in pts[1:]:
            cr.line_to(*q)
        cr.set_line_width(14)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.set_source_rgb(*tuple(p.get("color", VERDE)))
        cr.stroke()
        cr.arc(*pts[-1], 22, 0, 2 * math.pi)
        rellenar(cr, tuple(p.get("color", VERDE)))
    if p.get("pie"):
        texto(cr, p["pie"], W / 2, 1150, 52, GRIS)


ESCENAS = {"icono": esc_icono, "cifra": esc_cifra, "iconos": esc_iconos, "sello": esc_sello,
           "linea_tiempo": esc_linea_tiempo, "versus": esc_versus, "grafico": esc_grafico}


# ---------- armado del video ----------

def main(carpeta):
    cfg = json.load(open(os.path.join(carpeta, "motion.json")))
    palabras = render.cargar_palabras(os.path.join(carpeta, "palabras.json"))
    audio = os.path.normpath(os.path.join(carpeta, cfg["audio"]))
    duracion = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]))
    inicio_audio = 0.0
    if cfg.get("empezar_en"):
        idx = render.buscar(palabras, cfg["empezar_en"])
        inicio_audio = max(0.0, palabras[idx]["start"] - 0.03)
        palabras = [dict(q, start=q["start"] - inicio_audio, end=q["end"] - inicio_audio) for q in palabras[idx:]]
        duracion -= inicio_audio
    if cfg.get("bucle"):
        duracion = min(duracion, palabras[-1]["end"] + 0.12)

    inicios, cursor = [], 0
    for k, e in enumerate(cfg["escenas"]):
        if k == 0:
            inicios.append(0.0)
            continue
        cursor = render.buscar(palabras, e["desde"], cursor)
        inicios.append(palabras[cursor]["start"])

    tmp = tempfile.mkdtemp(prefix="motion_")
    try:
        fondo_mp4 = os.path.join(tmp, "fondo.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset",
                               "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", fondo_mp4], stdin=subprocess.PIPE)
        sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        total = int(math.ceil(duracion * FPS))
        for f in range(total):
            tg = f / FPS
            k = max(i for i, s in enumerate(inicios) if s <= tg + 1e-6)
            e = cfg["escenas"][k]
            cr = cairo.Context(sup)
            fondo(cr, tg)
            ESCENAS[e["tipo"]](cr, tg - inicios[k], e)
            sup.flush()
            ff.stdin.write(bytes(sup.get_data()))
        ff.stdin.close()
        ff.wait()

        subs = render.aplicar_reemplazos(palabras, cfg.get("reemplazos", {}))
        ass = os.path.join(tmp, "subs.ass")
        render.generar_ass(subs, [], duracion, ass)
        salida = os.path.join(carpeta, cfg.get("salida", "video-motion.mp4"))
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", fondo_mp4, "-ss", f"{inicio_audio:.3f}", "-i", audio,
            "-vf", f"ass={ass}:fontsdir={render.DIR_FUENTES}", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-map", "0:v", "-map", "1:a", "-t", f"{duracion:.2f}", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", salida], check=True)
        print(f"Listo: {salida} ({duracion:.1f} s, {len(inicios)} escenas)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1])
