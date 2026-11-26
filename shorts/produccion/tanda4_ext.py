# -*- coding: utf-8 -*-
"""Arte de la tanda 4 (Shorts 027 a 032). Incluye todo lo de la tanda 3 y suma:
íconos celular (tipo: clasico | tactil), ladrillo, ladrillos, tablero, gota, oro, cupon, revista;
decorado desierto; y estilos de personaje. Sin azul con amarillo; marcas solo como texto."""
import importlib.util
import math
import os
import random

TINTA = (0.14, 0.12, 0.18)
ROJO_T = (0.86, 0.10, 0.16)
CREMA = (0.95, 0.92, 0.86)
ORO = (0.98, 0.74, 0.26)


def registrar(m, pj):
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tanda3_ext.py")
    spec = importlib.util.spec_from_file_location("tanda3_ext", ruta)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    base.registrar(m, pj)
    PISO = pj.PISO

    def rect(cr, x, y, w, h, c, a=1.0):
        cr.new_path()
        cr.rectangle(x, y, w, h)
        m.rellenar(cr, c, a)

    def rr(cr, x, y, w, h, r, c, a=1.0):
        cr.new_path()
        m.rrect(cr, x, y, w, h, r)
        m.rellenar(cr, c, a)

    def circ(cr, x, y, r, c, a=1.0):
        cr.new_path()
        cr.arc(x, y, r, 0, 2 * math.pi)
        m.rellenar(cr, c, a)

    def ic_celular(cr, t, tipo="clasico", **kw):
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.03)
        if tipo == "clasico":
            rr(cr, -100, -200, 200, 400, 46, (0.24, 0.24, 0.30))
            rr(cr, -74, -160, 148, 120, 12, (0.70, 0.82, 0.62))
            for k in range(3):
                rect(cr, -56, -140 + k * 26, 80 + 14 * (k % 2), 10, (0.30, 0.40, 0.28))
            rr(cr, -40, -14, 80, 34, 14, (0.86, 0.86, 0.90))
            for fy in range(4):
                for fx in range(3):
                    rr(cr, -74 + fx * 52, 40 + fy * 36, 44, 26, 10, (0.86, 0.86, 0.90))
            rect(cr, 50, -236, 16, 40, (0.24, 0.24, 0.30))
        else:
            rr(cr, -110, -210, 220, 420, 36, (0.10, 0.10, 0.13))
            rr(cr, -94, -180, 188, 340, 14, (0.16, 0.16, 0.22))
            cols = [(0.90, 0.30, 0.34), (0.24, 0.70, 0.46), (0.62, 0.42, 0.80), (0.98, 0.60, 0.30)]
            for fy in range(4):
                for fx in range(3):
                    k = m.ease_out_back((t - (fy * 3 + fx) * 0.05) / 0.3)
                    if k > 0.01:
                        rr(cr, -78 + fx * 56 + 22 * (1 - k), -160 + fy * 62 + 22 * (1 - k), 44 * k, 44 * k, 12,
                           cols[(fx + fy) % 4])
            circ(cr, 0, 184, 14, (0.30, 0.30, 0.36))
        cr.restore()

    def un_ladrillo(cr, x, y, w, c, pernos):
        rr(cr, x, y, w, 80, 8, c)
        rect(cr, x, y + 60, w, 20, (0, 0, 0), 0.14)
        paso = w / pernos
        for k in range(pernos):
            rr(cr, x + paso * k + paso * 0.2, y - 22, paso * 0.6, 26, 6, c)
        rect(cr, x + 8, y + 8, w - 16, 10, (1, 1, 1), 0.18)

    def ic_ladrillo(cr, t, color=None, **kw):
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.03)
        cr.scale(1.5, 1.5)
        un_ladrillo(cr, -130, -30, 260, tuple(color) if color else ROJO_T, 4)
        cr.restore()

    def ic_ladrillos(cr, t, **kw):
        piezas = [(-190, 110, 180, ROJO_T, 3), (0, 110, 190, (0.24, 0.66, 0.44), 3), (-110, 30, 220, (0.96, 0.96, 0.94), 4),
                  (-150, -50, 130, (0.62, 0.40, 0.80), 2), (0, -50, 130, (0.98, 0.58, 0.30), 2), (-70, -130, 140, ROJO_T, 2)]
        for i, (x, y, w, c, p) in enumerate(piezas):
            k = m.ease_out_back((t - i * 0.12) / 0.35)
            if k > 0.01:
                un_ladrillo(cr, x, y - 300 * (1 - min(1.0, k)), w, c, p)

    def ic_tablero(cr, t, **kw):
        cr.save()
        cr.rotate(math.sin(t * 1.5) * 0.03)
        rr(cr, -200, -200, 400, 400, 16, (0.82, 0.92, 0.84))
        cols = [(0.90, 0.30, 0.34), (0.98, 0.58, 0.30), (0.24, 0.66, 0.44), (0.62, 0.40, 0.80)]
        for k in range(8):
            c = cols[k // 2 % 4]
            rect(cr, -200 + k * 50, -200, 48, 56, CREMA)
            rect(cr, -200 + k * 50, -200, 48, 16, c)
            rect(cr, -200 + k * 50, 144, 48, 56, CREMA)
            rect(cr, -200 + k * 50, 184, 48, 16, cols[(k // 2 + 2) % 4])
            rect(cr, -200, -200 + k * 50, 56, 48, CREMA)
            rect(cr, 144, -200 + k * 50, 56, 48, CREMA)
        rr(cr, -70, -40, 140, 80, 10, ROJO_T)                              # carta central
        rr(cr, 60, 30, 50, 44, 6, (0.24, 0.50, 0.36))                      # casita
        cr.new_path()
        cr.move_to(52, 30)
        cr.line_to(85, 2)
        cr.line_to(118, 30)
        cr.close_path()
        m.rellenar(cr, (0.18, 0.40, 0.30))
        rr(cr, -110, 40, 46, 46, 8, (0.97, 0.97, 0.97))                    # dado
        for (dx, dy) in ((-98, 52), (-76, 74), (-87, 63)):
            circ(cr, dx, dy, 5, TINTA)
        cr.restore()

    def ic_gota(cr, t, **kw):
        late = 1 + 0.05 * math.sin(t * 5)
        cr.save()
        cr.scale(late, late)
        cr.new_path()
        cr.move_to(0, -200)
        cr.curve_to(60, -90, 130, -10, 130, 70)
        cr.curve_to(130, 150, 70, 200, 0, 200)
        cr.curve_to(-70, 200, -130, 150, -130, 70)
        cr.curve_to(-130, -10, -60, -90, 0, -200)
        m.rellenar(cr, (0.82, 0.08, 0.14))
        cr.new_path()
        cr.arc(-10, 80, 86, math.pi * 0.62, math.pi * 0.98)
        cr.set_line_width(18)
        cr.set_line_cap(1)
        cr.set_source_rgba(1, 1, 1, 0.5)
        cr.stroke()
        cr.restore()

    def ic_oro(cr, t, **kw):
        osc = (0.80, 0.54, 0.12)
        pos = [(-150, 120), (-50, 120), (50, 120), (150, 120), (-100, 40), (0, 40), (100, 40), (-50, -40), (50, -40),
               (0, -120)]
        for i, (x, y) in enumerate(pos):
            k = m.ease_out_back((t - i * 0.06) / 0.3)
            if k <= 0.01:
                continue
            cr.save()
            cr.translate(x, y)
            cr.scale(k, k)
            cr.new_path()
            cr.move_to(-56, 34)
            cr.line_to(-40, -30)
            cr.line_to(40, -30)
            cr.line_to(56, 34)
            cr.close_path()
            m.rellenar(cr, ORO)
            rect(cr, -56, 22, 112, 12, osc)
            rect(cr, -30, -22, 22, 8, (1, 1, 1), 0.5)
            cr.restore()
        for k in range(3):
            a = t * 3 + k * 2.1
            circ(cr, 140 * math.cos(a), -60 + 110 * math.sin(a * 0.7), 6, (1, 1, 1), 0.6 * abs(math.sin(a)))

    def ic_cupon(cr, t, **kw):
        cr.save()
        cr.rotate(-0.08 + math.sin(t * 2) * 0.03)
        rr(cr, -200, -120, 400, 240, 14, CREMA)
        cr.new_path()
        m.rrect(cr, -184, -104, 368, 208, 8)
        cr.set_line_width(6)
        cr.set_dash([14, 10])
        cr.set_source_rgb(0.60, 0.44, 0.30)
        cr.stroke()
        cr.set_dash([])
        circ(cr, 110, 0, 58, ROJO_T, 0.85)
        circ(cr, 110, 0, 40, CREMA)
        for k in range(4):
            rect(cr, -160, -70 + k * 36, 170 - k * 20, 12, (0.60, 0.44, 0.30))
        cr.restore()

    def ic_revista(cr, t, texto="", **kw):
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.03)
        rr(cr, -150, -200, 300, 400, 10, (0.97, 0.96, 0.94))
        rect(cr, -150, -200, 300, 74, ROJO_T)
        m.texto(cr, "REVISTA", 0, -162, 40, (1, 1, 1))
        circ(cr, 0, -20, 62, (0.96, 0.80, 0.68))                           # retrato
        cr.new_path()
        cr.arc(0, -30, 66, math.pi, 2 * math.pi)
        cr.close_path()
        m.rellenar(cr, (0.90, 0.80, 0.46))
        rr(cr, -70, 44, 140, 90, 30, TINTA)
        if texto:
            m.texto(cr, texto, 0, 166, m.ajustar_tam(cr, texto, 30, 270), TINTA)
        cr.restore()

    m.ICONOS.update({"celular": ic_celular, "ladrillo": ic_ladrillo, "ladrillos": ic_ladrillos, "tablero": ic_tablero,
                     "gota": ic_gota, "oro": ic_oro, "cupon": ic_cupon, "revista": ic_revista})

    def dec_desierto(cr, t, W, H, dibujar_icono):
        import cairo
        g = cairo.LinearGradient(0, 0, 0, PISO)
        g.add_color_stop_rgb(0, 0.98, 0.62, 0.40)
        g.add_color_stop_rgb(1, 0.99, 0.86, 0.66)
        cr.new_path()
        cr.rectangle(0, 0, W, PISO)
        cr.set_source(g)
        cr.fill()
        circ(cr, 800, 560, 90, (1.0, 0.95, 0.84))
        for (cx, cy, r, c) in ((220, 1500, 640, (0.90, 0.66, 0.42)), (860, 1560, 700, (0.84, 0.58, 0.36)),
                               (520, 1700, 720, (0.78, 0.52, 0.32))):
            circ(cr, cx, cy, r, c)
        for k in range(4):                                                  # caravana a lo lejos
            x = (220 + k * 110 + t * 14) % (W + 200) - 100
            y = 905
            rr(cr, x - 26, y - 22, 52, 26, 10, (0.36, 0.22, 0.16))
            circ(cr, x + 4, y - 30, 12, (0.36, 0.22, 0.16))
            rect(cr, x + 22, y - 44, 8, 30, (0.36, 0.22, 0.16))
            circ(cr, x + 30, y - 46, 9, (0.36, 0.22, 0.16))
            for dx in (-18, 14):
                rect(cr, x + dx, y, 6, 26, (0.36, 0.22, 0.16))
    pj.DECORADOS_EXTRA["desierto"] = dec_desierto

    E = pj.ESTILOS
    E["magie"] = {"ropa": (0.34, 0.26, 0.46), "pantalon": (0.34, 0.26, 0.46), "pelo": (0.30, 0.18, 0.10),
                  "peinado": "largo", "falda": True}
    E["darrow"] = {"ropa": (0.52, 0.40, 0.30), "pantalon": (0.30, 0.24, 0.20), "pelo": (0.22, 0.15, 0.10),
                   "peinado": "corto", "bigote": True, "anteojos": True}
    E["holmes"] = {"ropa": (0.10, 0.10, 0.12), "pantalon": (0.10, 0.10, 0.12), "pelo": (0.90, 0.80, 0.46),
                   "peinado": "largo"}
    E["ponzi"] = {"ropa": (0.30, 0.30, 0.36), "pantalon": (0.22, 0.22, 0.27), "pelo": (0.12, 0.09, 0.07),
                  "peinado": "corto", "sombrero": "fedora", "corbata": ROJO_T}
    E["musa"] = {"ropa": (0.96, 0.94, 0.88), "pantalon": (0.96, 0.94, 0.88), "pelo": (0.05, 0.04, 0.04),
                 "peinado": "rapado", "piel": (0.42, 0.28, 0.19), "barba": "corta", "corbata": ORO}
    E["director"] = {"ropa": (0.30, 0.34, 0.40), "pantalon": (0.20, 0.22, 0.28), "pelo": (0.50, 0.36, 0.20),
                     "peinado": "corto", "anteojos": True, "barba": "corta"}
    E["periodista"] = {"ropa": (0.56, 0.48, 0.38), "pantalon": (0.26, 0.24, 0.26), "pelo": (0.30, 0.20, 0.12),
                       "peinado": "corto", "anteojos": True}
