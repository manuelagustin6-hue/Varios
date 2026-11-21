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
import personajes  # noqa: E402  (personajes animados y escenarios)

W, H, FPS = 1080, 1920, 30
FUENTE = "Liberation Sans"
PESO = cairo.FONT_WEIGHT_BOLD
V2 = False  # calidad v2: tipografía propia, cámara, transiciones, viñeta y efectos de sonido
DIR_FUENTES_V2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes")

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
TITULAR_FONDO = TITULAR_TEXTO = None  # si no se definen, cartel dorado con letras oscuras


def paleta_roja():
    """Paleta del canal desde el video 014: fondo vino, cartel rojo con letras blancas y resaltado
    durazno. Regla: nunca combinar azul con amarillo."""
    global FONDO1, FONDO2, DORADO, TITULAR_FONDO, TITULAR_TEXTO, ROJO
    FONDO1, FONDO2 = (0.22, 0.08, 0.24), (0.09, 0.03, 0.11)
    DORADO = (1.0, 0.72, 0.50)
    ROJO = (1.0, 0.30, 0.36)
    TITULAR_FONDO, TITULAR_TEXTO = (0.86, 0.10, 0.16), (1, 1, 1)
    render.AMARILLO = "&H0080B8FF&"  # durazno, para la palabra resaltada del subtítulo


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
    cr.select_font_face(FUENTE, cairo.FONT_SLANT_NORMAL, PESO)
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
    cr.new_path()  # que el texto no deje un trazo abierto que se una al próximo dibujo
    return ext.width


def ancho_texto(cr, s, tam):
    cr.select_font_face(FUENTE, cairo.FONT_SLANT_NORMAL, PESO)
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


def titular(cr, s, t, y=300):
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
    rellenar(cr, TITULAR_FONDO or DORADO)
    for i, l in enumerate(lineas):
        yy = -alto / 2 + 20 + tam * 1.25 * (i + 0.5)
        texto(cr, l, 0, yy, tam, TITULAR_TEXTO or OSCURO)
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

def ic_dvd(cr, t, **kw):
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


def ic_sobre(cr, t, **kw):
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


def ic_tienda(cr, t, color=AZUL, cartel="", **kw):
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


def ic_avion(cr, t, **kw):
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


def ic_risa(cr, t, **kw):
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


def ic_pantalla(cr, t, **kw):
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


def ic_pinos(cr, t, **kw):
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


def ic_dinero(cr, t, **kw):
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
    cr.new_path()
    cr.save()
    cr.translate(x, y)
    cr.scale(escala, escala)
    if nombre == "tienda_pinos":
        ic_pinos(cr, t)
        ic_tienda(cr, t, **kw)
    else:
        ICONOS[nombre](cr, t, **kw)
    cr.restore()


# ---------- tipos de escena ----------

def esc_icono(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    a = ease_out_back(t / 0.45)
    flot = math.sin(t * 2.2) * 12
    kw = dict(p.get("args", {}))
    if "cartel" in p:
        kw["cartel"] = p["cartel"]
    if "color" in p:
        kw["color"] = tuple(p["color"])
    dibujar_icono(cr, p["icono"], t, W / 2, 840 + flot, 1.05 * a, **kw)
    if p.get("pie"):
        texto(cr, p["pie"], W / 2, 1225, 58, p.get("color_pie") and tuple(p["color_pie"]) or GRIS,
              alfa=ease_out_cubic((t - 0.3) / 0.3))


def esc_cifra(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    if p.get("icono"):
        dibujar_icono(cr, p["icono"], t, W / 2, 1060, 0.6 * ease_out_back(t / 0.4), **p.get("args", {}))
    k = ease_out_cubic(t / p.get("cuenta", 1.2))
    v = p.get("de", 0) + (p["a"] - p.get("de", 0)) * k
    num = f"{p.get('prefijo', '')}{v:,.0f}".replace(",", ".") + p.get("sufijo", "")
    esc = 1 + 0.06 * math.sin(clamp(t / 0.25) * math.pi)
    cr.save()
    cr.translate(W / 2, 680)
    cr.scale(esc, esc)
    tam = 250
    while ancho_texto(cr, num, tam) > 980:
        tam -= 6
    texto(cr, num, 0, 0, tam, tuple(p.get("color", DORADO)))
    cr.restore()
    if p.get("unidad"):
        texto(cr, p["unidad"], W / 2, 835, 66, BLANCO, alfa=ease_out_cubic((t - 0.2) / 0.3))


def esc_iconos(cr, t, p):
    titular(cr, p.get("titulo", ""), t)
    n, cols = p.get("cantidad", 12), p.get("columnas", 4)
    filas = math.ceil(n / cols)
    esc = p.get("escala", 0.36)
    dx, dy = 245, 230
    x0 = W / 2 - (cols - 1) * dx / 2
    y0 = 840 - (filas - 1) * dy / 2
    for i in range(n):
        a = ease_out_back((t - i * 0.06) / 0.3)
        if a <= 0:
            continue
        dibujar_icono(cr, p["icono"], t, x0 + (i % cols) * dx, y0 + (i // cols) * dy, esc * a, **p.get("args", {}))


def esc_sello(cr, t, p):
    base = dict(p.get("base", {}))
    tipo = base.pop("tipo", "cifra")
    ESCENAS[tipo](cr, t + p.get("desfase", 2.0), base)
    a = clamp(t / 0.18)
    esc = 2.2 - 1.2 * ease_out_cubic(a)
    cr.save()
    cr.translate(W / 2, 820)
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
    x0, x1, y = 160, W - 160, 860
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
        dibujar_icono(cr, s["icono"], t, x, 820, 0.55 * a, **s.get("args", {}))
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



# ---------- ilustraciones adicionales ----------

def _circ(cr, x, y, r, color, alfa=1.0):
    cr.new_path()
    cr.arc(x, y, r, 0, 2 * math.pi)
    rellenar(cr, color, alfa)


def _persona(cr, x, y, s=1.0, color=(0.8, 0.85, 0.95), sombrero=False):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    _circ(cr, 0, -90, 55, color)
    rrect(cr, -85, -25, 170, 170, 70)
    rellenar(cr, color)
    if sombrero:
        rrect(cr, -95, -140, 190, 22, 8)
        rellenar(cr, (0.55, 0.42, 0.3))
        rrect(cr, -55, -195, 110, 65, 14)
        rellenar(cr, (0.55, 0.42, 0.3))
        cr.rectangle(-55, -150, 110, 12)
        rellenar(cr, DORADO)
    cr.restore()


def ic_torta(cr, t, **kw):
    a = ease_out_cubic(t / 0.8)
    cr.move_to(0, 0)
    cr.arc(0, 0, 220, -math.pi / 2 + 2 * math.pi * 0.1 * a, 3 * math.pi / 2)
    cr.close_path()
    rellenar(cr, (0.75, 0.78, 0.85))
    sep = 25 * ease_out_back((t - 0.6) / 0.4)
    cr.save()
    ang = -math.pi / 2 + math.pi * 0.1
    cr.translate(math.cos(ang) * sep, math.sin(ang) * sep)
    cr.move_to(0, 0)
    cr.arc(0, 0, 220, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 0.1 * a)
    cr.close_path()
    rellenar(cr, DORADO)
    cr.restore()
    texto(cr, kw.get("etiqueta", "10 %"), 0, 0, 80, OSCURO)


def ic_personas(cr, t, **kw):
    for i, x in enumerate((-230, 0, 230)):
        a = ease_out_back((t - i * 0.15) / 0.35)
        if a > 0:
            col = DORADO if i == kw.get("destacar", 2) else (0.75, 0.8, 0.9)
            _persona(cr, x, 40, 0.95 * a, col)


def ic_contrato(cr, t, **kw):
    cr.save()
    cr.rotate(-0.06)
    rrect(cr, -190, -250, 380, 500, 14)
    rellenar(cr, (0.96, 0.95, 0.9))
    for i in range(8):
        cr.rectangle(-140, -190 + i * 45, 280 if i % 3 else 200, 14)
        rellenar(cr, (0.75, 0.75, 0.78))
    # firma que se dibuja
    k = ease_in_out((t - 0.3) / 1.0)
    cr.set_line_width(7)
    cr.set_source_rgb(0.15, 0.3, 0.8)
    pasos = int(40 * k)
    for j in range(pasos):
        x = -120 + j * 6
        y = 190 + math.sin(j * 0.6) * 18
        cr.line_to(x, y) if j else cr.move_to(x, y)
    if pasos > 1:
        cr.stroke()
    cr.restore()


def ic_casa(cr, t, **kw):
    cr.move_to(-240, -20); cr.line_to(0, -230); cr.line_to(240, -20)
    rellenar(cr, (0.75, 0.25, 0.25))
    cr.rectangle(-190, -30, 380, 250)
    rellenar(cr, (0.9, 0.88, 0.82))
    cr.rectangle(-40, 90, 80, 130)
    rellenar(cr, (0.45, 0.3, 0.2))
    p = 1 + 0.12 * math.sin(t * 7)
    cr.save()
    cr.translate(170, -160)
    cr.scale(p, p)
    cr.move_to(0, -90); cr.line_to(85, 70); cr.line_to(-85, 70); cr.close_path()
    rellenar(cr, DORADO)
    texto(cr, "!", 0, 15, 110, OSCURO)
    cr.restore()


def ic_torre(cr, t, **kw):
    col = (0.62, 0.48, 0.33)
    cr.set_line_width(16)
    cr.set_source_rgb(*col)
    cr.move_to(-210, 260); cr.curve_to(-120, 80, -40, -60, -12, -300)
    cr.move_to(210, 260); cr.curve_to(120, 80, 40, -60, 12, -300)
    cr.stroke()
    for y, w in ((60, 200), (-110, 100)):
        cr.rectangle(-w / 2 - 20, y, w + 40, 20)
        rellenar(cr, col)
    cr.new_path()
    cr.arc(0, 260, 130, math.pi, 2 * math.pi)
    cr.set_line_width(14)
    cr.stroke()
    cr.move_to(0, -300); cr.line_to(0, -360)
    cr.set_line_width(8)
    cr.stroke()
    if kw.get("cartel"):
        a = ease_out_back((t - 0.3) / 0.35)
        if a > 0:
            cr.save()
            cr.translate(150, -40)
            cr.rotate(0.12 + math.sin(t * 3) * 0.05)
            cr.scale(a, a)
            rrect(cr, -150, -55, 300, 110, 12)
            rellenar(cr, ROJO)
            texto(cr, kw["cartel"], 0, 0, 50, BLANCO)
            cr.restore()


def ic_diario(cr, t, **kw):
    cr.save()
    cr.rotate(-0.08 + math.sin(t * 1.5) * 0.03)
    rrect(cr, -240, -280, 480, 560, 8)
    rellenar(cr, (0.93, 0.91, 0.85))
    rrect(cr, -200, -240, 400, 70, 4)
    rellenar(cr, (0.2, 0.2, 0.22))
    texto(cr, kw.get("cabecera", "DIARIO"), 0, -205, 44, (0.93, 0.91, 0.85))
    rrect(cr, -200, -150, 190, 160, 4)
    rellenar(cr, (0.6, 0.58, 0.55))
    for i in range(9):
        cr.rectangle(10 if i < 4 else -200, -150 + i * 42 if i < 4 else -150 + (i + 0.5) * 42, 190 if i < 4 else 400, 12)
        rellenar(cr, (0.6, 0.6, 0.62))
    cr.restore()


def ic_estafador(cr, t, **kw):
    _persona(cr, 0, 60, 1.6, (0.42, 0.45, 0.56), sombrero=True)
    cr.rectangle(-60, -75, 120, 22)
    rellenar(cr, OSCURO)
    _circ(cr, -30, -64, 10, DORADO)
    _circ(cr, 30, -64, 10, DORADO)


def ic_maletin(cr, t, **kw):
    a = ease_out_cubic(t / 0.5)
    rrect(cr, -230, -120, 460, 300, 20)
    rellenar(cr, (0.45, 0.28, 0.15))
    rrect(cr, -80, -180, 160, 70, 20)
    cr.set_line_width(18)
    cr.set_source_rgb(0.35, 0.2, 0.1)
    cr.stroke()
    for i in range(5):
        x = -150 + i * 75
        y = -150 - 140 * ease_out_cubic((t - 0.2 - i * 0.07) / 0.6)
        if y < -150:
            cr.save()
            cr.translate(x, y)
            cr.rotate(math.sin(i + t * 3) * 0.3)
            rrect(cr, -55, -28, 110, 56, 6)
            rellenar(cr, (0.25, 0.65, 0.4), a)
            texto(cr, "$", 0, 0, 36, (0.8, 1, 0.85))
            cr.restore()


def ic_sirena(cr, t, **kw):
    on = int(t * 4) % 2
    for lado, col in ((-1, ROJO), (1, AZUL)):
        cr.new_path()
        brillo = 1.0 if (on == (lado > 0)) else 0.35
        cr.arc(lado * 95, -20, 140, math.pi, 2 * math.pi)
        rellenar(cr, col, brillo)
        if brillo > 0.9:
            _circ(cr, lado * 95, -60, 260, col, 0.12)
    rrect(cr, -260, -20, 520, 90, 16)
    rellenar(cr, (0.3, 0.32, 0.4))


def ic_carcel(cr, t, **kw):
    rrect(cr, -230, -260, 460, 520, 20)
    rellenar(cr, (0.18, 0.2, 0.26))
    _persona(cr, 0, 90, 1.2, (0.5, 0.52, 0.6))
    k = ease_out_cubic(t / 0.5)
    for i in range(6):
        x = -195 + i * 78
        cr.rectangle(x - 9, -260, 18, 520 * k)
        rellenar(cr, (0.7, 0.72, 0.78))


def ic_candado(cr, t, **kw):
    cr.new_path()
    cr.arc(0, -60, 110, math.pi, 2 * math.pi)
    cr.set_line_width(36)
    cr.set_source_rgb(0.7, 0.72, 0.78)
    cr.stroke()
    cr.move_to(-110, -60); cr.line_to(-110, 0)
    cr.move_to(110, -60); cr.line_to(110, 0)
    cr.stroke()
    rrect(cr, -180, -10, 360, 260, 30)
    rellenar(cr, DORADO)
    _circ(cr, 0, 90, 30, OSCURO)
    cr.rectangle(-12, 90, 24, 70)
    rellenar(cr, OSCURO)


def ic_pincel(cr, t, **kw):
    """Pincelada genérica que se dibuja (no reproduce ningún logo)."""
    k = ease_in_out(t / 1.0)
    rrect(cr, -260, -220, 520, 440, 16)
    rellenar(cr, (0.96, 0.96, 0.94))
    pts = [(-200 + 400 * i / 60, 60 - 120 * math.sin(math.pi * i / 60 * 0.9) + 40 * (i / 60)) for i in range(61)]
    n = int(60 * k)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        cr.set_line_width(10 + 34 * math.sin(math.pi * i / 60))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgb(0.08, 0.08, 0.1)
        cr.move_to(x1, y1); cr.line_to(x2, y2)
        cr.stroke()


def ic_zapatilla(cr, t, color=None, **kw):
    c1 = tuple(color) if color else (0.92, 0.92, 0.95)
    c2 = (0.1, 0.1, 0.12) if color else (0.75, 0.75, 0.8)
    cr.save()
    cr.rotate(math.sin(t * 2) * 0.04)
    cr.move_to(-260, 90); cr.line_to(-250, -40); cr.curve_to(-220, -200, -60, -200, -40, -90)
    cr.curve_to(40, -40, 200, -20, 260, 40); cr.line_to(260, 90); cr.close_path()
    rellenar(cr, c1)
    rrect(cr, -275, 80, 550, 60, 20)
    rellenar(cr, (0.97, 0.97, 0.97))
    cr.move_to(-230, -40); cr.curve_to(-180, -140, -90, -150, -60, -80)
    cr.set_line_width(26)
    cr.set_source_rgb(*c2)
    cr.stroke()
    for i in range(4):
        cr.move_to(-150 + i * 30, -110 + i * 8); cr.line_to(-100 + i * 30, -90 + i * 8)
        cr.set_line_width(8)
        cr.set_source_rgb(*c2)
        cr.stroke()
    cr.restore()


def ic_duda(cr, t, **kw):
    _persona(cr, -60, 120, 1.3, (0.75, 0.8, 0.9))
    a = ease_out_back((t - 0.2) / 0.4)
    if a > 0:
        cr.save()
        cr.translate(150, -170)
        cr.scale(a, a)
        _circ(cr, 0, 0, 120, BLANCO)
        _circ(cr, -110, 110, 25, BLANCO)
        _circ(cr, -150, 160, 14, BLANCO)
        texto(cr, kw.get("texto", "MMM…"), 0, 0, 56, OSCURO)
        cr.restore()


def ic_anillo(cr, t, **kw):
    cr.new_path()
    cr.arc(0, 40, 170, 0, 2 * math.pi)
    cr.set_line_width(48)
    g = cairo.LinearGradient(-170, -130, 170, 210)
    g.add_color_stop_rgb(0, 1, 0.9, 0.5)
    g.add_color_stop_rgb(0.5, 0.85, 0.65, 0.2)
    g.add_color_stop_rgb(1, 1, 0.88, 0.45)
    cr.set_source(g)
    cr.stroke()
    cr.move_to(0, -250); cr.line_to(70, -180); cr.line_to(0, -110); cr.line_to(-70, -180); cr.close_path()
    rellenar(cr, (0.8, 0.95, 1))
    b = 0.5 + 0.5 * math.sin(t * 6)
    _circ(cr, 40, -210, 14 * b, BLANCO)


def ic_navegador(cr, t, **kw):
    rrect(cr, -280, -200, 560, 400, 24)
    rellenar(cr, (0.95, 0.96, 0.98))
    rrect(cr, -280, -200, 560, 70, 24)
    rellenar(cr, (0.82, 0.85, 0.9))
    for i, c in enumerate((ROJO, DORADO, VERDE)):
        _circ(cr, -240 + i * 40, -165, 12, c)
    rrect(cr, -230, -40, 460, 80, 40)
    rellenar(cr, BLANCO)
    cr.set_line_width(4)
    rrect(cr, -230, -40, 460, 80, 40)
    cr.set_source_rgb(0.7, 0.72, 0.78)
    cr.stroke()
    s = kw.get("texto", "google.com")
    n = int(len(s) * clamp(t / 0.8))
    texto(cr, s[:n] + ("|" if int(t * 3) % 2 else ""), -200, 0, 44, OSCURO, alinear="izq")


def ic_tarjeta(cr, t, **kw):
    cr.save()
    cr.rotate(-0.12 + math.sin(t * 2) * 0.03)
    g = cairo.LinearGradient(-260, -160, 260, 160)
    g.add_color_stop_rgb(0, 0.15, 0.35, 0.9)
    g.add_color_stop_rgb(1, 0.4, 0.15, 0.7)
    rrect(cr, -260, -160, 520, 320, 28)
    cr.set_source(g)
    cr.fill()
    rrect(cr, -200, -70, 90, 70, 10)
    rellenar(cr, DORADO)
    for i in range(4):
        rrect(cr, -200 + i * 105, 50, 85, 22, 8)
        rellenar(cr, (1, 1, 1), 0.7)
    cr.restore()


def ic_reloj(cr, t, **kw):
    _circ(cr, 0, 0, 230, BLANCO)
    _circ(cr, 0, 0, 205, (0.92, 0.93, 0.96))
    k = clamp(t / kw.get("seg", 3.0))
    cr.move_to(0, 0)
    cr.arc(0, 0, 190, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k)
    cr.close_path()
    rellenar(cr, DORADO, 0.5)
    for i in range(12):
        ang = i * math.pi / 6
        cr.move_to(math.cos(ang) * 170, math.sin(ang) * 170)
        cr.line_to(math.cos(ang) * 195, math.sin(ang) * 195)
        cr.set_line_width(8)
        cr.set_source_rgb(*OSCURO)
        cr.stroke()
    ang = -math.pi / 2 + 2 * math.pi * k
    cr.move_to(0, 0); cr.line_to(math.cos(ang) * 160, math.sin(ang) * 160)
    cr.set_line_width(12)
    cr.set_source_rgb(*ROJO)
    cr.stroke()
    _circ(cr, 0, 0, 18, OSCURO)


def ic_corazon(cr, t, **kw):
    p = 1 + 0.08 * math.sin(t * 6)
    cr.save()
    cr.scale(p, p)
    cr.move_to(0, 200)
    cr.curve_to(-320, -20, -170, -280, 0, -110)
    cr.curve_to(170, -280, 320, -20, 0, 200)
    rellenar(cr, ROJO)
    texto(cr, kw.get("texto", "x2"), 0, -10, 110, BLANCO)
    cr.restore()


def ic_lata(cr, t, **kw):
    """Lata genérica plateada y azul, sin marca."""
    cr.save()
    cr.rotate(math.sin(t * 2) * 0.05)
    g = cairo.LinearGradient(-110, 0, 110, 0)
    g.add_color_stop_rgb(0, 0.55, 0.6, 0.7)
    g.add_color_stop_rgb(0.45, 0.95, 0.96, 1)
    g.add_color_stop_rgb(1, 0.5, 0.55, 0.65)
    rrect(cr, -110, -260, 220, 520, 30)
    cr.set_source(g)
    cr.fill()
    cr.rectangle(-110, -120, 220, 220)
    rellenar(cr, (0.15, 0.3, 0.75))
    cr.rectangle(-110, -10, 110, 110)
    rellenar(cr, (0.75, 0.75, 0.82))
    rrect(cr, -90, -280, 180, 30, 10)
    rellenar(cr, (0.6, 0.62, 0.7))
    cr.restore()


def ic_tacho(cr, t, **kw):
    for i, (x, y, r) in enumerate([(-90, -250, -0.6), (40, -275, 0.4), (130, -230, 1.2), (-10, -215, -1.4)]):
        a = ease_out_back((t - i * 0.12) / 0.35)
        if a > 0:
            cr.save()
            cr.translate(x, y)
            cr.rotate(r)
            cr.scale(0.38 * a, 0.38 * a)
            ic_lata(cr, t)
            cr.restore()
    cr.move_to(-200, -170); cr.line_to(200, -170); cr.line_to(160, 230); cr.line_to(-160, 230); cr.close_path()
    rellenar(cr, (0.32, 0.35, 0.42))
    rrect(cr, -225, -200, 450, 45, 12)
    rellenar(cr, (0.42, 0.45, 0.52))
    for x in (-90, 0, 90):
        cr.move_to(x, -120); cr.line_to(x * 0.85, 190)
        cr.set_line_width(10)
        cr.set_source_rgb(0.25, 0.27, 0.33)
        cr.stroke()


def ic_pregunta(cr, t, **kw):
    p = 1 + 0.06 * math.sin(t * 4)
    cr.save()
    cr.scale(p, p)
    _circ(cr, 0, 0, 230, DORADO)
    texto(cr, "?", 0, 0, 300, OSCURO)
    cr.restore()


def ic_claqueta(cr, t, **kw):
    ang = -0.45 * (1 - ease_out_back((t - 0.2) / 0.3))
    rrect(cr, -250, -110, 500, 330, 16)
    rellenar(cr, (0.15, 0.15, 0.18))
    for i in range(3):
        cr.rectangle(-210, -40 + i * 80, 420, 14)
        rellenar(cr, (0.85, 0.85, 0.88))
    cr.save()
    cr.translate(-250, -110)
    cr.rotate(ang)
    cr.rectangle(0, -80, 500, 80)
    rellenar(cr, (0.95, 0.95, 0.97))
    for i in range(5):
        cr.move_to(20 + i * 100, -80); cr.line_to(70 + i * 100, -80); cr.line_to(30 + i * 100, 0); cr.line_to(-20 + i * 100, 0)
        rellenar(cr, (0.15, 0.15, 0.18))
    cr.restore()


def ic_caramelos(cr, t, colores=None, **kw):
    cols = [tuple(c) for c in colores] if colores else [ROJO, AZUL, VERDE, DORADO, (1, 0.55, 0.15), (0.55, 0.35, 0.2)]
    rnd = random.Random(3)
    for i in range(18):
        x, y = rnd.uniform(-240, 240), rnd.uniform(-180, 200)
        a = ease_out_back((t - i * 0.04) / 0.3)
        if a <= 0:
            continue
        cr.save()
        cr.translate(x, y + math.sin(t * 3 + i) * 6)
        cr.scale(a, a * 0.8)
        _circ(cr, 0, 0, 52, cols[i % len(cols)])
        _circ(cr, -15, -15, 14, BLANCO, 0.5)
        cr.restore()


def ic_luna(cr, t, **kw):
    rnd = random.Random(5)
    for _ in range(25):
        x, y = rnd.uniform(-300, 300), rnd.uniform(-280, 280)
        _circ(cr, x, y, rnd.uniform(3, 7), BLANCO, 0.4 + 0.4 * math.sin(t * 3 + x))
    _circ(cr, 0, 0, 220, (0.97, 0.95, 0.85))
    for x, y, r in ((-60, -50, 40), (70, 40, 30), (-20, 90, 22)):
        _circ(cr, x, y, r, (0.85, 0.83, 0.72))


def ic_cine(cr, t, **kw):
    rrect(cr, -290, -230, 580, 300, 10)
    rellenar(cr, (0.95, 0.95, 0.9), 0.85 + 0.15 * math.sin(t * 8))
    for fila in range(2):
        for i in range(7):
            x = -270 + i * 90 + (45 if fila else 0)
            _persona(cr, x, 210 + fila * 70, 0.45, (0.15, 0.17, 0.23))


def ic_parabrisas(cr, t, **kw):
    cr.move_to(-280, 180); cr.line_to(-220, -180); cr.line_to(220, -180); cr.line_to(280, 180); cr.close_path()
    rellenar(cr, (0.35, 0.55, 0.75))
    rnd = random.Random(9)
    for _ in range(26):
        x, y = rnd.uniform(-230, 230), rnd.uniform(-160, 160)
        _circ(cr, x, y, rnd.uniform(4, 9), (0.8, 0.9, 1), 0.8)
    ciclo = (t % 2.0) / 2.0
    ang = -math.pi + math.pi * (math.sin(ciclo * 2 * math.pi) * 0.5 + 0.5) if ciclo < 0.5 else -math.pi
    cr.save()
    cr.translate(0, 170)
    cr.rotate(ang)
    rrect(cr, 0, -9, 300, 18, 9)
    rellenar(cr, OSCURO)
    cr.restore()
    cr.rectangle(-320, 180, 640, 60)
    rellenar(cr, (0.2, 0.22, 0.28))


def ic_auto(cr, t, **kw):
    x = -30 + 60 * math.sin(t * 1.2)
    cr.save()
    cr.translate(x, 0)
    rrect(cr, -280, -20, 560, 140, 40)
    rellenar(cr, (0.75, 0.15, 0.18))
    cr.move_to(-170, -20); cr.line_to(-110, -140); cr.line_to(130, -140); cr.line_to(190, -20)
    rellenar(cr, (0.75, 0.15, 0.18))
    cr.move_to(-140, -30); cr.line_to(-95, -115); cr.line_to(110, -115); cr.line_to(155, -30)
    rellenar(cr, (0.55, 0.75, 0.95))
    for wx in (-170, 170):
        _circ(cr, wx, 125, 62, OSCURO)
        _circ(cr, wx, 125, 28, (0.6, 0.62, 0.7))
    cr.restore()


def ic_mazo(cr, t, **kw):
    golpe = clamp(t / 0.25)
    ang = -0.8 * (1 - ease_out_cubic(golpe))
    rrect(cr, -300, 100, 260, 70, 14)
    rellenar(cr, (0.45, 0.28, 0.15))
    cr.save()
    cr.translate(170, -40)
    cr.rotate(ang)
    rrect(cr, -320, -16, 330, 32, 12)
    rellenar(cr, (0.62, 0.42, 0.24))
    rrect(cr, -420, -80, 140, 160, 26)
    rellenar(cr, (0.52, 0.33, 0.18))
    rrect(cr, -420, -18, 140, 36, 6)
    rellenar(cr, DORADO)
    cr.restore()
    if golpe >= 1 and t < 0.7:
        for i in range(7):
            a2 = math.pi + i * math.pi / 6
            cr.move_to(-170 + math.cos(a2) * 80, 100 + math.sin(a2) * 40)
            cr.line_to(-170 + math.cos(a2) * 140, 100 + math.sin(a2) * 70)
            cr.set_line_width(9)
            cr.set_source_rgb(*DORADO)
            cr.stroke()


def ic_carrito(cr, t, **kw):
    items = [(VERDE, -110), (ROJO, -20), (AZUL, 70), (DORADO, 150), ((0.8, 0.5, 0.9), 30)]
    for i, (c, x) in enumerate(items):
        y = -260 + 230 * ease_out_cubic((t - i * 0.2) / 0.4)
        if t - i * 0.2 > 0:
            rrect(cr, x - 45, y - 45, 90, 90, 16)
            rellenar(cr, c)
    cr.move_to(-270, -150); cr.line_to(-200, -150); cr.line_to(-140, 120); cr.line_to(220, 120); cr.line_to(260, -60); cr.line_to(-180, -60)
    cr.set_line_width(20)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgb(*DORADO)
    cr.stroke()
    for x in (-110, 190):
        _circ(cr, x, 180, 32, DORADO)


def ic_laberinto(cr, t, **kw):
    pts = [(-240, 250), (-240, 100), (220, 100), (220, -20), (-220, -20), (-220, -140), (220, -140), (220, -260)]
    k = ease_in_out(t / 1.6) * (len(pts) - 1)
    cr.set_line_width(70)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(*pts[0])
    for q in pts[1:]:
        cr.line_to(*q)
    cr.set_source_rgba(*GRIS, 0.25)
    cr.stroke()
    i = int(k)
    f = k - i
    cr.move_to(*pts[0])
    for q in pts[1:i + 1]:
        cr.line_to(*q)
    if i < len(pts) - 1:
        x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
        y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
        cr.line_to(x, y)
    else:
        x, y = pts[-1]
    cr.set_line_width(20)
    cr.set_source_rgb(*DORADO)
    cr.stroke()
    _circ(cr, x, y, 30, BLANCO)


def ic_caja(cr, t, **kw):
    rrect(cr, -260, -40, 520, 260, 18)
    rellenar(cr, (0.35, 0.38, 0.46))
    rrect(cr, -150, -230, 300, 170, 14)
    rellenar(cr, (0.2, 0.22, 0.28))
    rrect(cr, -120, -200, 240, 90, 8)
    rellenar(cr, (0.24, 0.86, 0.52), 0.85)
    texto(cr, kw.get("precio", "$1"), 0, -155, 60, OSCURO)
    k = ease_out_cubic(t / 1.2)
    rrect(cr, 120, 20, 110, 30 + 300 * k, 6)
    rellenar(cr, (0.97, 0.97, 0.95))


def ic_lista(cr, t, **kw):
    rrect(cr, -200, -260, 400, 520, 18)
    rellenar(cr, (0.97, 0.96, 0.9))
    for i in range(5):
        y = -180 + i * 85
        rrect(cr, -150, y - 25, 50, 50, 8)
        cr.set_line_width(6)
        cr.set_source_rgb(0.4, 0.42, 0.5)
        cr.stroke()
        cr.rectangle(-70, y - 8, 200 if i % 2 else 160, 16)
        rellenar(cr, (0.65, 0.65, 0.7))
        if t > 0.3 + i * 0.25:
            cr.move_to(-140, y); cr.line_to(-125, y + 18); cr.line_to(-95, y - 20)
            cr.set_line_width(9)
            cr.set_source_rgb(*VERDE)
            cr.stroke()


def ic_pelota(cr, t, **kw):
    y = -220 * abs(math.sin(t * 3.2))
    cr.save()
    cr.translate(0, 80 + y)
    _circ(cr, 0, 0, 170, (0.95, 0.5, 0.15))
    cr.set_line_width(9)
    cr.set_source_rgb(0.25, 0.12, 0.05)
    cr.arc(0, 0, 170, 0, 2 * math.pi); cr.stroke()
    cr.move_to(-170, 0); cr.line_to(170, 0); cr.stroke()
    cr.move_to(0, -170); cr.line_to(0, 170); cr.stroke()
    cr.arc(-240, 0, 170, -0.75, 0.75); cr.stroke()
    cr.arc(240, 0, 170, math.pi - 0.75, math.pi + 0.75); cr.stroke()
    cr.restore()
    cr.save()
    cr.translate(0, 270)
    cr.scale(1, 0.2)
    _circ(cr, 0, 0, 150 * (1 + y / 600), OSCURO, 0.5)
    cr.restore()


def ic_regla(cr, t, **kw):
    rrect(cr, -60, -300, 120, 600, 12)
    rellenar(cr, DORADO)
    for i in range(13):
        y = -280 + i * 46
        cr.rectangle(-60, y, 50 if i % 2 else 80, 8)
        rellenar(cr, OSCURO)
    k = ease_out_back(t / 0.5)
    _persona(cr, -220, 100, 1.0 * k, (0.75, 0.8, 0.9))
    _persona(cr, 220, -20, 1.6 * k, (0.75, 0.8, 0.9))


ICONOS.update({"torta": ic_torta, "personas": ic_personas, "contrato": ic_contrato, "casa": ic_casa,
               "torre": ic_torre, "diario": ic_diario, "estafador": ic_estafador, "maletin": ic_maletin,
               "sirena": ic_sirena, "carcel": ic_carcel, "candado": ic_candado, "pincel": ic_pincel,
               "zapatilla": ic_zapatilla, "duda": ic_duda, "anillo": ic_anillo, "navegador": ic_navegador,
               "tarjeta": ic_tarjeta, "reloj": ic_reloj, "corazon": ic_corazon, "lata": ic_lata,
               "tacho": ic_tacho, "pregunta": ic_pregunta, "claqueta": ic_claqueta, "caramelos": ic_caramelos,
               "luna": ic_luna, "cine": ic_cine, "parabrisas": ic_parabrisas, "auto": ic_auto, "mazo": ic_mazo,
               "carrito": ic_carrito, "laberinto": ic_laberinto, "caja": ic_caja, "lista": ic_lista,
               "pelota": ic_pelota, "regla": ic_regla})


# ---------- escenas adicionales ----------

def esc_barras(cr, t, p):
    """Barras que crecen: comparación de valores reales (p. ej., meta contra resultado)."""
    titular(cr, p.get("titulo", ""), t)
    barras = p["barras"]
    vmax = max(b[1] for b in barras)
    base, alto_max = 1120, 520
    ancho = 260
    x0 = W / 2 - (len(barras) - 1) * 170
    for i, (etq, val, col) in enumerate(barras):
        k = ease_out_cubic((t - i * 0.5) / 1.0)
        h = max(8, alto_max * val / vmax * k)
        x = x0 + i * 340
        rrect(cr, x - ancho / 2, base - h, ancho, h, 16)
        rellenar(cr, tuple(col))
        v = val * k
        num = f"{p.get('prefijo', '')}{v:,.0f}".replace(",", ".") + p.get("sufijo", "")
        texto(cr, num, x, base - h - 60, 76, tuple(col))
        texto(cr, etq, x, base + 55, 48, BLANCO)


def esc_transformar(cr, t, p):
    """Un texto que se convierte letra por letra en otro (600613 → GOOGLE)."""
    titular(cr, p.get("titulo", ""), t)
    a, b = p["de"], p["a"]
    tam = 190
    paso = 0.25
    inicio = p.get("espera", 0.8)
    xs = W / 2 - (len(a) - 1) * 70
    for i, (ca, cb) in enumerate(zip(a, b)):
        ti = t - inicio - i * paso
        x = xs + i * 140
        if ti <= 0:
            texto(cr, ca, x, 760, tam, BLANCO)
        else:
            k = clamp(ti / 0.25)
            esc = abs(math.cos(k * math.pi))
            cr.save()
            cr.translate(x, 760)
            cr.scale(1, max(esc, 0.02))
            texto(cr, ca if k < 0.5 else cb, 0, 0, tam, BLANCO if k < 0.5 else DORADO)
            cr.restore()
    if p.get("pie"):
        texto(cr, p["pie"], W / 2, 980, 58, GRIS)


ESCENAS.update({"barras": esc_barras, "transformar": esc_transformar})



# ---------- escenas con personajes ----------

def globo(cr, s, x, y, t):
    """Globo de diálogo con la punta hacia abajo, en (x, y)."""
    a = ease_out_back(t / 0.3)
    if a <= 0.01:
        return
    lineas = s.split("\n")
    tam = 46
    ancho = max(ancho_texto(cr, l, tam) for l in lineas) + 60
    alto = tam * 1.3 * len(lineas) + 40
    x = min(max(x, ancho / 2 + 30), W - ancho / 2 - 30)
    cr.save()
    cr.translate(x, y)
    cr.scale(a, a)
    cr.new_path()
    rrect(cr, -ancho / 2, -alto, ancho, alto, 30)
    rellenar(cr, BLANCO)
    cr.new_path()
    cr.move_to(-25, -2); cr.line_to(0, 45); cr.line_to(25, -2)
    rellenar(cr, BLANCO)
    for i, l in enumerate(lineas):
        texto(cr, l, 0, -alto + 20 + tam * 1.3 * (i + 0.5), tam, OSCURO)
    cr.restore()


def _valor_en(v, t):
    """Número fijo o [desde, hasta, t_inicio, t_fin] con movimiento suave."""
    if isinstance(v, (int, float)):
        return v
    a, b, t0, t1 = v
    return a + (b - a) * ease_in_out((t - t0) / max(0.01, t1 - t0))


def esc_historia(cr, t, p):
    if V2:  # cámara: acercamiento lento con un leve paneo
        z = 1 + min(0.08, 0.012 * t)
        cr.save()
        cr.translate(W / 2 + math.sin(t * 0.4) * 8, personajes.PISO)
        cr.scale(z, z)
        cr.translate(-W / 2, -personajes.PISO)
    personajes.decorado(cr, p.get("decorado", "calle_paris"), t, W, H, dibujar_icono)
    for el in p.get("elementos", []):
        if V2:  # tarjeta de fondo para que el elemento no se mezcle con el escenario
            m = 290 * el.get("escala", 1.0)
            k = ease_out_back(t / 0.4)
            cr.new_path()
            rrect(cr, el["x"] - m * k, el["y"] - m * k, 2 * m * k, 2 * m * k, 40)
            rellenar(cr, FONDO1, 0.92)
            cr.new_path()
            rrect(cr, el["x"] - m * k, el["y"] - m * k, 2 * m * k, 2 * m * k, 40)
            cr.set_line_width(8)
            cr.set_source_rgb(*DORADO)
            cr.stroke()
        dibujar_icono(cr, el["icono"], t, el["x"], el["y"], el.get("escala", 1.0), **el.get("args", {}))
    for pj in p["personajes"]:
        te = t - pj.get("entra", 0)
        if te < 0 or t > pj.get("sale", 1e9):
            continue
        nombre_pose = pj.get("pose", "parado")
        for tp, ps in pj.get("poses", []):
            if t >= tp:
                nombre_pose = ps
        x = _valor_en(pj.get("x", W / 2), t)
        esc = pj.get("escala", 0.95)
        personajes.personaje(cr, pj["estilo"], x, personajes.PISO, esc, pj.get("mira", 1), nombre_pose, te,
                             pj.get("objeto"))
        g = pj.get("globo")
        if g and g[1] <= t <= g[2]:
            globo(cr, g[0], x + 40 * pj.get("mira", 1), personajes.PISO - 640 * esc, t - g[1])
    if p.get("rejas"):
        personajes.rejas(cr, t, W)
    if V2:
        cr.restore()
    titular(cr, p.get("titulo", ""), t)


ESCENAS["historia"] = esc_historia


# ---------- calidad v2: transiciones, viñeta y sonido ----------

def vineta(cr):
    g = cairo.RadialGradient(W / 2, H * 0.42, H * 0.3, W / 2, H * 0.42, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.4)
    cr.new_path()
    cr.rectangle(0, 0, W, H)
    cr.set_source(g)
    cr.fill()


def transicion(cr, d):
    """Barrido dorado que tapa el corte entre escenas (d = segundos respecto del corte)."""
    q = (d + 0.14) / 0.34
    if not 0 <= q <= 1:
        return
    a = -1.7 * W + 2.8 * W * q
    cr.new_path()
    cr.rectangle(a - 60, 0, 1.6 * W + 120, H)
    rellenar(cr, BLANCO)
    cr.new_path()
    cr.rectangle(a, 0, 1.6 * W, H)
    rellenar(cr, DORADO)


def eventos_sonido(cfg, inicios):
    ev = [("whoosh", c - 0.12) for c in inicios[1:]]
    for e, ini in zip(cfg["escenas"], inicios):
        base = e.get("base", e) if e["tipo"] == "sello" else e
        if e["tipo"] == "sello":
            ev.append(("golpe", ini + 0.16))
        if base["tipo"] == "cifra" or base.get("icono") == "dinero":
            ev.append(("caja", ini + 0.35))
        for pj in base.get("personajes", []):
            if pj.get("globo"):
                ev.append(("pop", ini + pj["globo"][1]))
            if pj.get("objeto") == "billetes":
                td = next((tp for tp, ps in pj.get("poses", []) if ps == "dar"), 0.3)
                ev.append(("caja", ini + td + 0.1))
    return ev


def pista_sonido(eventos, duracion, ruta):
    """Sintetiza los efectos con numpy y los guarda en un WAV mono de 48 kHz."""
    import wave
    import numpy as np
    sr = 48000
    pista = np.zeros(int((duracion + 1) * sr))
    rng = np.random.default_rng(3)

    def tono(f0, f1, dur, caida):
        t = np.arange(int(dur * sr)) / sr
        f = f0 + (f1 - f0) * t / dur
        return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * caida)

    def whoosh():
        n = int(0.34 * sr)
        r = rng.standard_normal(n)
        k = 60
        suave = np.convolve(r, np.ones(k) / k, mode="same") * 6
        return suave * np.hanning(n) * 0.35

    sonidos = {
        "whoosh": whoosh,
        "pop": lambda: tono(420, 980, 0.09, 30) * 0.3,
        "golpe": lambda: tono(110, 45, 0.3, 14) * 0.7 + np.pad(rng.standard_normal(600) * 0.15, (0, int(0.3 * sr) - 600)),
        "caja": lambda: (tono(1568, 1568, 0.5, 9) + np.pad(tono(2093, 2093, 0.42, 9), (int(0.08 * sr), 0))) * 0.16,
    }
    for nombre, t0 in eventos:
        if t0 < 0 or t0 > duracion:
            continue
        s = sonidos[nombre]()
        i = int(t0 * sr)
        pista[i:i + len(s)] += s[:len(pista) - i]
    datos = (np.clip(pista, -1, 1) * 32767).astype("<i2")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(datos.tobytes())

# ---------- armado del video ----------

def main(carpeta, archivo="motion.json"):
    global V2, FUENTE, PESO
    cfg = json.load(open(os.path.join(carpeta, archivo)))
    if cfg.get("paleta") == "roja":
        paleta_roja()
    if cfg.get("v2"):
        V2 = True
        personajes.DETALLE = True
        FUENTE, PESO = "Montserrat ExtraBold", cairo.FONT_WEIGHT_NORMAL
        destino = os.path.expanduser("~/.fonts")
        os.makedirs(destino, exist_ok=True)
        for f in os.listdir(DIR_FUENTES_V2):
            if f.endswith(".ttf"):
                shutil.copy(os.path.join(DIR_FUENTES_V2, f), destino)
        subprocess.run(["fc-cache", "-f"], check=False)
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
            if V2:
                vineta(cr)
                for c in inicios[1:]:
                    transicion(cr, tg - c)
            sup.flush()
            ff.stdin.write(bytes(sup.get_data()))
        ff.stdin.close()
        ff.wait()

        subs = render.aplicar_reemplazos(palabras, cfg.get("reemplazos", {}))
        ass = os.path.join(tmp, "subs.ass")
        if V2:
            render.generar_ass(subs, [], duracion, ass, y_sub=1350, fuente=FUENTE, tam_base=98)
        else:
            render.generar_ass(subs, [], duracion, ass, y_sub=1350)
        salida = os.path.join(carpeta, cfg.get("salida", "video-motion.mp4"))
        if V2:
            wav = os.path.join(tmp, "efectos.wav")
            pista_sonido(eventos_sonido(cfg, inicios), duracion, wav)
            audio_args = ["-i", wav, "-filter_complex",
                          f"[0:v]ass={ass}:fontsdir={DIR_FUENTES_V2}[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad[voz];"
                          "[2:a]aresample=48000,apad[fx];"
                          "[voz][fx]amix=inputs=2:normalize=0:duration=longest[a]", "-map", "[v]", "-map", "[a]"]
        else:
            audio_args = ["-vf", f"ass={ass}:fontsdir={render.DIR_FUENTES}", "-af",
                          "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a"]
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", fondo_mp4, "-ss", f"{inicio_audio:.3f}", "-i", audio,
            *audio_args, "-t", f"{duracion:.2f}", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", salida], check=True)
        print(f"Listo: {salida} ({duracion:.1f} s, {len(inicios)} escenas)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "motion.json")
