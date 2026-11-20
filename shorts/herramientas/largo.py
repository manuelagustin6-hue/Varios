#!/usr/bin/env python3
"""Videos largos horizontales (1920x1080) hechos con código: explicaciones e historias animadas.

Uso:
  python3 herramientas/largo.py largos/L01-tir            # video guía (texto para leer y grabar la voz)
  python3 herramientas/largo.py largos/L01-tir limpio     # video limpio, sin el texto de lectura
  python3 herramientas/largo.py largos/L01-tir limpio voz.mp3   # video final con la voz grabada

La carpeta debe contener `largo.json`: una lista de escenas. Cada escena tiene sus `frases`
(lo que dice la voz) y los elementos visuales, que aparecen cuando empieza una frase (`en`).
La duración de cada frase se calcula por cantidad de palabras, a ritmo de lectura natural.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import cairo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motion  # noqa: E402
import personajes  # noqa: E402
from motion import (AZUL, BLANCO, DORADO, FONDO1, GRIS, OSCURO, ROJO, VERDE, ancho_texto, clamp,  # noqa: E402
                    ease_in_out, ease_out_back, ease_out_cubic, rellenar, rrect, texto)

W, H, FPS = 1920, 1080, 30
PALABRAS_POR_SEG = 2.5   # ritmo de lectura (unas 150 palabras por minuto)
PAUSA = 0.45             # respiro entre frases
CUENTA_REGRESIVA = 3.0   # solo en el video guía
PISO = 880

personajes.ESTILOS["presentador"] = {"ropa": (0.13, 0.2, 0.38), "pantalon": (0.1, 0.12, 0.2),
                                     "pelo": (0.2, 0.13, 0.08), "peinado": "corto", "corbata": DORADO}


def preparar():
    motion.W, motion.H = W, H
    motion.V2 = True
    personajes.DETALLE = True
    motion.FUENTE, motion.PESO = "Montserrat ExtraBold", cairo.FONT_WEIGHT_NORMAL
    destino = os.path.expanduser("~/.fonts")
    os.makedirs(destino, exist_ok=True)
    for f in os.listdir(motion.DIR_FUENTES_V2):
        if f.endswith(".ttf"):
            shutil.copy(os.path.join(motion.DIR_FUENTES_V2, f), destino)
    subprocess.run(["fc-cache", "-f"], check=False)


def duracion_frase(f):
    return max(1.2, len(f.split()) / PALABRAS_POR_SEG) + PAUSA


def tiempos(escenas):
    """Agrega a cada escena su inicio, su duración y el inicio de cada frase (relativo a la escena)."""
    t = 0.0
    for e in escenas:
        e["_ini"] = t
        e["_fr"] = []
        d = 0.0
        for f in e["frases"]:
            e["_fr"].append(d)
            d += duracion_frase(f)
        e["_dur"] = d
        t += d
    return t


def desde(e, i, t):
    """Segundos transcurridos desde que empezó la frase i de la escena (negativo si todavía no)."""
    return t - e["_fr"][min(i, len(e["_fr"]) - 1)]


def ajustar(cr, s, tam, ancho):
    while ancho_texto(cr, s, tam) > ancho and tam > 24:
        tam -= 2
    return tam


def partir(cr, s, tam, ancho):
    lineas, actual = [], ""
    for p in s.split():
        prueba = (actual + " " + p).strip()
        if ancho_texto(cr, prueba, tam) > ancho and actual:
            lineas.append(actual)
            actual = p
        else:
            actual = prueba
    return lineas + [actual]


def tarjeta(cr, x, y, w, h, borde=None, alfa=0.9):
    cr.new_path()
    rrect(cr, x, y, w, h, 30)
    rellenar(cr, (0.09, 0.13, 0.21), alfa)
    cr.new_path()
    rrect(cr, x, y, w, h, 30)
    cr.set_line_width(5)
    cr.set_source_rgba(*(borde or GRIS), 1 if borde else 0.35)
    cr.stroke()


def encabezado(cr, e, t):
    s = e.get("titulo")
    if s:
        k = ease_out_back(t / 0.4)
        tam = 46
        w = ancho_texto(cr, s, tam) + 60
        cr.save()
        cr.translate(80, 95)
        cr.scale(k, k)
        cr.new_path()
        rrect(cr, 0, -42, w, 84, 16)
        rellenar(cr, DORADO)
        texto(cr, s, 30, 0, tam, OSCURO, alinear="izq")
        cr.restore()
    texto(cr, "@datomillonario", W - 80, 95, 30, GRIS, alinear="derecha", alfa=0.8)


def presentador(cr, e, t, x=330, escala=0.82):
    pose = e.get("pose", "hablar")
    for i, ps in sorted((int(k), v) for k, v in e.get("poses", {}).items()):
        if desde(e, i, t) >= 0:
            pose = ps
    # piso
    cr.new_path()
    cr.rectangle(0, PISO, W, 6)
    rellenar(cr, GRIS, 0.25)
    personajes.personaje(cr, e.get("personaje", "presentador"), x, PISO, escala, 1, pose, t)


# ---------- contenidos ----------

def c_puntos(cr, e, t, x0=700, ancho=1100):
    items = e["puntos"]
    paso = min(130, 560 / max(1, len(items)))
    y0 = 500 - paso * (len(items) - 1) / 2
    for i, it in enumerate(items):
        d = desde(e, it.get("en", 0), t)
        if d < 0:
            continue
        k = ease_out_cubic(d / 0.4)
        y = y0 + i * paso
        col = tuple(it.get("color", BLANCO))
        cr.new_path()
        cr.arc(x0 + 20 - 60 * (1 - k), y, 16, 0, 2 * math.pi)
        rellenar(cr, DORADO, k)
        tam = ajustar(cr, it["t"], it.get("tam", 54), ancho - 70)
        texto(cr, it["t"], x0 + 70 + 60 * (1 - k), y, tam, col, alinear="izq", alfa=k)


def c_grande(cr, e, t, cx=1230):
    lineas = e["lineas"]
    alto = sum(l.get("tam", 80) * 1.35 for l in lineas)
    y = 510 - alto / 2
    for l in lineas:
        tam = l.get("tam", 80)
        y += tam * 1.35 / 2
        d = desde(e, l.get("en", 0), t)
        if d >= 0:
            k = ease_out_back(d / 0.4)
            tam2 = ajustar(cr, l["t"], tam, 1150)
            cr.save()
            cr.translate(cx, y)
            cr.scale(0.7 + 0.3 * k, 0.7 + 0.3 * k)
            texto(cr, l["t"], 0, 0, tam2, tuple(l.get("color", BLANCO)), alfa=clamp(d / 0.2))
            cr.restore()
        y += tam * 1.35 / 2


def c_icono(cr, e, t, cx=1230):
    for ic in e["iconos"]:
        d = desde(e, ic.get("en", 0), t)
        if d < 0:
            continue
        motion.dibujar_icono(cr, ic["icono"], d, ic.get("x", cx), ic.get("y", 480),
                             ic.get("escala", 0.8) * ease_out_back(d / 0.4), **ic.get("args", {}))
        if ic.get("pie"):
            texto(cr, ic["pie"], ic.get("x", cx), ic.get("y", 480) + 330 * ic.get("escala", 0.8), 44,
                  tuple(ic.get("color", BLANCO)), alfa=clamp(d / 0.3))


def esc_presentador(cr, e, t):
    presentador(cr, e, t)
    if "puntos" in e:
        c_puntos(cr, e, t)
    if "lineas" in e:
        c_grande(cr, e, t)
    if "iconos" in e:
        c_icono(cr, e, t)


def esc_comparar(cr, e, t):
    cols = e["columnas"]
    w = 800
    for j, c in enumerate(cols):
        d0 = desde(e, c.get("en", 0), t)
        if d0 < 0:
            continue
        k = ease_out_cubic(d0 / 0.45)
        x = 130 + j * (w + 60)
        baja = 70 if e.get("pie") else 0
        y = 190 + baja + 60 * (1 - k)
        col = tuple(c.get("color", DORADO))
        tarjeta(cr, x, y, w, 660 - baja, borde=col, alfa=0.9 * k)
        texto(cr, c["titulo"], x + w / 2, y + 75, ajustar(cr, c["titulo"], 58, w - 80), col, alfa=k)
        cr.new_path()
        cr.rectangle(x + 50, y + 135, w - 100, 4)
        rellenar(cr, col, 0.5 * k)
        filas = c["filas"]
        paso = min(120, (470 - baja) / max(1, len(filas)))
        for i, f in enumerate(filas):
            d = desde(e, f.get("en", 0), t)
            if d < 0:
                continue
            a = ease_out_cubic(d / 0.35)
            yy = y + 210 + i * paso
            tam = ajustar(cr, f["t"], f.get("tam", 50), w - 100)
            texto(cr, f["t"], x + w / 2, yy + 20 * (1 - a), tam, tuple(f.get("color", BLANCO)), alfa=a)
    if e.get("pie"):
        d = desde(e, e["pie"].get("en", 0), t)
        if d >= 0:
            texto(cr, e["pie"]["t"], W / 2, 195, ajustar(cr, e["pie"]["t"], 50, W - 240), tuple(e["pie"].get("color", BLANCO)), alfa=clamp(d / 0.3))


def esc_flujos(cr, e, t):
    barras = e["barras"]
    vmax = max(abs(b["v"]) for b in barras)
    base, alto = 520, 250
    x0, x1 = 330, W - 330
    paso = (x1 - x0) / (len(barras) - 1)
    cr.new_path()
    cr.rectangle(x0 - 160, base - 3, x1 - x0 + 320, 6)
    rellenar(cr, GRIS, 0.6)
    for i, b in enumerate(barras):
        x = x0 + i * paso
        texto(cr, b["etq"], x, base + (60 if b["v"] > 0 else -60), 40, GRIS)
        d = desde(e, b.get("en", 0), t)
        if d < 0:
            continue
        k = ease_out_cubic(d / 0.6)
        h = alto * abs(b["v"]) / vmax * k
        col = VERDE if b["v"] > 0 else ROJO
        cr.new_path()
        if b["v"] > 0:
            rrect(cr, x - 85, base - 3 - h, 170, h, 14)
        else:
            rrect(cr, x - 85, base + 3, 170, h, 14)
        rellenar(cr, col)
        num = ("+" if b["v"] > 0 else "−") + "$" + f"{abs(b['v']) * k:,.0f}".replace(",", ".")
        texto(cr, num, x, base - h - 50 if b["v"] > 0 else base + h + 55, 56, col)
    for n in e.get("notas", []):
        d = desde(e, n.get("en", 0), t)
        if d >= 0:
            texto(cr, n["t"], W / 2, n.get("y", 200), n.get("tam", 54), tuple(n.get("color", BLANCO)),
                  alfa=clamp(d / 0.3))


def van(flujos, r):
    return sum(f / (1 + r) ** i for i, f in enumerate(flujos))


def esc_curva(cr, e, t):
    fl = e["flujos"]
    r0, r1 = 0.0, e.get("r_max", 0.16)
    x0, x1, y0, y1 = 330, W - 250, 780, 230
    v_max, v_min = van(fl, r0) * 1.15, van(fl, r1) * 1.25
    px = lambda r: x0 + (x1 - x0) * (r - r0) / (r1 - r0)  # noqa: E731
    py = lambda v: y0 + (y1 - y0) * (v - v_min) / (v_max - v_min)  # noqa: E731
    # ejes
    cr.new_path()
    cr.rectangle(x0, y1 - 20, 5, y0 - y1 + 40)
    rellenar(cr, GRIS, 0.7)
    cr.new_path()
    cr.rectangle(x0, py(0) - 3, x1 - x0 + 40, 6)
    rellenar(cr, GRIS, 0.9)
    texto(cr, "Valor de los cobros − inversión", x0 + 20, y1 - 60, 34, GRIS, alinear="izq")
    texto(cr, "0", x0 - 40, py(0), 40, GRIS)
    texto(cr, "Tasa", x1 + 100, py(0) - 45, 36, GRIS)
    for r in (0.05, 0.10, 0.15):
        texto(cr, f"{r * 100:.0f} %", px(r), py(0) + 50, 36, GRIS)
    # curva
    d = desde(e, e.get("en_curva", 0), t)
    if d >= 0:
        k = ease_in_out(d / 2.0)
        n = 80
        cr.new_path()
        for i in range(int(n * k) + 1):
            r = r0 + (r1 - r0) * i / n
            (cr.line_to if i else cr.move_to)(px(r), py(van(fl, r)))
        cr.set_line_width(10)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.set_source_rgb(*AZUL)
        cr.stroke()
    for m in e.get("marcas", []):
        d = desde(e, m.get("en", 0), t)
        if d < 0:
            continue
        v = van(fl, m["r"])
        col = VERDE if v > 0 else ROJO
        k = ease_out_back(d / 0.4)
        cr.new_path()
        cr.arc(px(m["r"]), py(v), 22 * k, 0, 2 * math.pi)
        rellenar(cr, col)
        signo = "+" if v > 0 else "−"
        s1, s2 = (-60, -115) if v > 0 else (115, 60)
        dx, al = (30, "izq") if v > 0 else (-30, "derecha")
        texto(cr, f"{signo}${abs(v):,.0f}".replace(",", "."), px(m["r"]) + dx, py(v) + s1, 52, col,
              alinear=al, alfa=clamp(d / 0.3))
        texto(cr, m["t"], px(m["r"]) + dx, py(v) + s2, 36, BLANCO, alinear=al, alfa=clamp(d / 0.3))
    if "tir" in e:
        d = desde(e, e["tir"].get("en", 0), t)
        if d >= 0:
            r = e["tir"]["r"]
            k = ease_out_back(d / 0.5)
            pulso = 1 + 0.15 * math.sin(d * 5)
            cr.new_path()
            cr.arc(px(r), py(0), 30 * k * pulso, 0, 2 * math.pi)
            rellenar(cr, DORADO)
            cr.save()
            cr.translate(px(r) + 300, py(0) - 120)
            cr.scale(k, k)
            cr.new_path()
            rrect(cr, -250, -60, 500, 120, 20)
            rellenar(cr, DORADO)
            texto(cr, e["tir"]["t"], 0, 0, 58, OSCURO)
            cr.restore()


def esc_planilla(cr, e, t):
    filas = e["filas"]
    x, y, wc, hc = 420, 200, 380, 92
    tarjeta(cr, x - 40, y - 40, wc * 2 + 180, hc * (len(filas) + 2) + 80, alfa=0.95)
    for j, letra in enumerate(("A", "B")):
        texto(cr, letra, x + 100 + wc * j + wc / 2, y + 20, 36, GRIS)
    for i, (a, b, en) in enumerate(filas + [["TIR", "", e.get("en_formula", 0)]]):
        yy = y + 60 + i * hc
        texto(cr, str(i + 1), x + 40, yy + hc / 2, 36, GRIS)
        for j in range(2):
            cr.new_path()
            cr.rectangle(x + 100 + wc * j, yy, wc, hc)
            cr.set_line_width(3)
            cr.set_source_rgba(*GRIS, 0.6)
            cr.stroke()
        d = desde(e, en, t)
        if d < 0:
            continue
        texto(cr, a, x + 130, yy + hc / 2, 44, BLANCO, alinear="izq", alfa=clamp(d / 0.3))
        if i < len(filas):
            col = ROJO if b.startswith("-") or b.startswith("−") else VERDE
            texto(cr, b, x + 100 + wc * 2 - 30, yy + hc / 2, 46, col, alinear="derecha", alfa=clamp(d / 0.3))
        else:
            f = e["formula"]
            dr = desde(e, e.get("en_resultado", 0), t)
            if dr >= 0:
                cr.new_path()
                cr.rectangle(x + 100 + wc, yy, wc, hc)
                rellenar(cr, DORADO, clamp(dr / 0.2))
                texto(cr, e["resultado"], x + 100 + wc * 2 - 30, yy + hc / 2, 52, OSCURO, alinear="derecha")
            else:
                n = int(len(f) * clamp(d / 1.5))
                texto(cr, f[:n] + ("|" if int(d * 3) % 2 else ""), x + 120 + wc, yy + hc / 2, 40, DORADO,
                      alinear="izq")
    for n in e.get("notas", []):
        d = desde(e, n.get("en", 0), t)
        if d >= 0:
            texto(cr, n["t"], 1560, n.get("y", 400), n.get("tam", 40), tuple(n.get("color", GRIS)),
                  alfa=clamp(d / 0.3))


def esc_precio(cr, e, t):
    """Gráfico de precio que se dibuja por tramos: `puntos` [[fecha, valor]], `inicio` (índice ya
    dibujado al empezar), `tramos` [{hasta, en, dur}] y `marcas` [{i, t, en, v, color, lado}]."""
    pts = e["puntos"]
    n = len(pts)
    v_max = e.get("v_max", max(p[1] for p in pts) * 1.1)
    x0, x1, y0, y1 = 260, W - 330, 800, 250
    px = lambda i: x0 + (x1 - x0) * i / (n - 1)  # noqa: E731
    py = lambda v: y0 + (y1 - y0) * v / v_max  # noqa: E731
    paso = e.get("paso_eje", 100)
    v = 0
    while v <= v_max:
        cr.new_path()
        cr.rectangle(x0, py(v) - 1, x1 - x0, 2)
        rellenar(cr, GRIS, 0.22)
        texto(cr, f"${v:.0f}", x0 - 30, py(v), 32, GRIS, alinear="derecha")
        v += paso
    for i in range(0, n, max(1, e.get("cada", 4))):
        texto(cr, pts[i][0], px(i), y0 + 45, 28, GRIS)
    if e.get("nota"):
        texto(cr, e["nota"], x0, 200, ajustar(cr, e["nota"], 30, x1 - x0), GRIS, alinear="izq")
    # hasta dónde está dibujada la línea
    pos = float(e.get("inicio", 0))
    for tr in e.get("tramos", []):
        d = desde(e, tr.get("en", 0), t)
        if d >= 0:
            pos = pos + (tr["hasta"] - pos) * ease_in_out(d / tr.get("dur", 2.5))
    val = lambda q: pts[int(q)][1] + (pts[min(n - 1, int(q) + 1)][1] - pts[int(q)][1]) * (q - int(q))  # noqa: E731
    if pos > 0:
        cr.new_path()
        cr.move_to(px(0), py(pts[0][1]))
        for i in range(1, int(pos) + 1):
            cr.line_to(px(i), py(pts[i][1]))
        cr.line_to(px(pos), py(val(pos)))
        camino = cr.copy_path()
        cr.line_to(px(pos), y0)
        cr.line_to(px(0), y0)
        cr.close_path()
        sube = val(pos) >= pts[0][1]
        col = VERDE if e.get("color", "auto") == "auto" and sube else ROJO if e.get("color", "auto") == "auto" else tuple(e["color"])
        rellenar(cr, col, 0.16)
        cr.new_path()
        cr.append_path(camino)
        cr.set_line_width(9)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgb(*col)
        cr.stroke()
    # punto actual con su precio
    cr.new_path()
    cr.arc(px(pos), py(val(pos)), 16, 0, 2 * math.pi)
    rellenar(cr, BLANCO)
    cr.save()
    cr.translate(min(px(pos) + 150, W - 170), max(py(val(pos)) - 10, y1))
    cr.new_path()
    rrect(cr, -110, -42, 220, 84, 16)
    rellenar(cr, DORADO)
    texto(cr, f"${val(pos):.0f}", 0, 0, 50, OSCURO)
    cr.restore()
    for m in e.get("marcas", []):
        d = desde(e, m.get("en", 0), t)
        if d < 0:
            continue
        k = ease_out_back(d / 0.4)
        mv = m.get("v", pts[m["i"]][1])
        col = tuple(m.get("color", BLANCO))
        cr.new_path()
        cr.arc(px(m["i"]), py(mv), 14 * k, 0, 2 * math.pi)
        rellenar(cr, col)
        lado = m.get("lado", "izq")
        dx = -30 if lado == "izq" else 30
        texto(cr, m["t"], px(m["i"]) + dx + m.get("dx", 0), py(mv) + m.get("dy", -10), m.get("tam", 36), col,
              alinear="derecha" if lado == "izq" else "izq", alfa=clamp(d / 0.3))


ESCENAS = {"presentador": esc_presentador, "comparar": esc_comparar, "flujos": esc_flujos,
           "curva": esc_curva, "planilla": esc_planilla, "precio": esc_precio}


# ---------- guía de lectura ----------

def banda_lectura(cr, e, t, n_esc, total_esc):
    i = max(k for k, s in enumerate(e["_fr"]) if s <= t + 1e-6)
    frase = e["frases"][i]
    dur = duracion_frase(frase) - PAUSA
    prog = clamp((t - e["_fr"][i]) / dur)
    cr.new_path()
    cr.rectangle(0, 900, W, 180)
    rellenar(cr, (0.02, 0.03, 0.06), 0.94)
    tam = 40
    lineas = partir(cr, frase, tam, 1740)
    if len(lineas) > 3:
        tam = 34
        lineas = partir(cr, frase, tam, 1740)
    palabras = frase.split()
    leidas = int(len(palabras) * prog + 0.5)
    y = 990 - (len(lineas) - 1) * tam * 0.65
    n = 0
    for l in lineas:
        ws = l.split()
        cr.select_font_face(motion.FUENTE, cairo.FONT_SLANT_NORMAL, motion.PESO)
        cr.set_font_size(tam)
        x = W / 2 - (sum(cr.text_extents(w_).x_advance for w_ in ws) + tam * 0.3 * (len(ws) - 1)) / 2
        for w_ in ws:
            # línea de base fija: todas las palabras del renglón quedan alineadas
            cr.select_font_face(motion.FUENTE, cairo.FONT_SLANT_NORMAL, motion.PESO)
            cr.set_font_size(tam)
            cr.set_source_rgb(*(DORADO if n < leidas else BLANCO))
            cr.move_to(x, y + tam * 0.35)
            cr.show_text(w_)
            cr.new_path()
            x += cr.text_extents(w_).x_advance + tam * 0.3
            n += 1
        y += tam * 1.3
    cr.new_path()
    cr.rectangle(0, 900, W * prog, 6)
    rellenar(cr, DORADO)
    texto(cr, f"Escena {n_esc}/{total_esc}", 110, 925, 22, GRIS)


def cuenta(cr, t):
    cr.new_path()
    cr.rectangle(0, 0, W, H)
    rellenar(cr, FONDO1)
    texto(cr, "Video guía para grabar la voz", W / 2, 330, 60, BLANCO)
    texto(cr, "Lee el texto de abajo al ritmo en que se pinta de dorado", W / 2, 420, 38, GRIS)
    texto(cr, str(max(1, math.ceil(CUENTA_REGRESIVA - t))), W / 2, 640, 260, DORADO)


def main(carpeta, modo="guia", voz=None):
    preparar()
    cfg = json.load(open(os.path.join(carpeta, "largo.json")))
    escenas = cfg["escenas"]
    total = tiempos(escenas)
    guia = modo == "guia"
    pre = CUENTA_REGRESIVA if guia else 0.0
    tmp = tempfile.mkdtemp(prefix="largo_")
    try:
        mudo = os.path.join(tmp, "mudo.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset",
                               "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
        sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cortes = [e["_ini"] for e in escenas[1:]]
        for f in range(int(math.ceil((total + pre) * FPS))):
            tg = f / FPS - pre
            cr = cairo.Context(sup)
            if tg < 0:
                cuenta(cr, tg + pre)
            else:
                k = max(i for i, e in enumerate(escenas) if e["_ini"] <= tg + 1e-6)
                e = escenas[k]
                motion.fondo(cr, tg)
                ESCENAS[e["tipo"]](cr, e, tg - e["_ini"])
                encabezado(cr, e, tg - e["_ini"])
                motion.vineta(cr)
                for c in cortes:
                    motion.transicion(cr, tg - c)
                if guia:
                    banda_lectura(cr, e, tg - e["_ini"], k + 1, len(escenas))
            sup.flush()
            ff.stdin.write(bytes(sup.get_data()))
        ff.stdin.close()
        ff.wait()
        salida = os.path.join(carpeta, {"guia": "video-guia.mp4", "limpio": "video.mp4"}[modo])
        if voz:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mudo, "-i", voz, "-map", "0:v",
                            "-map", "1:a", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a",
                            "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida], check=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mudo, "-c", "copy", "-movflags",
                            "+faststart", salida], check=True)
        print(f"Listo: {salida} ({(total + pre) / 60:.1f} min, {len(escenas)} escenas)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "guia", sys.argv[3] if len(sys.argv) > 3 else None)
