# -*- coding: utf-8 -*-
"""Arte propio del Short 012 (el recorrido de IKEA).

Aporta: estilos (clienta, penn), íconos «carro» (carrito que se va llenando) y «mapa_mini»,
decorados «tienda_frente» y «pasillo», y el tipo de escena «i_mapa» (plano de la tienda visto
desde arriba, con el recorrido serpenteante, los atajos y sellos).
Sin azul con amarillo: la tienda se dibuja en tonos crema, madera y rojo, y la marca va como texto.
"""
import math
import random

CREMA = (0.95, 0.93, 0.89)
MADERA = (0.72, 0.55, 0.38)
TINTA = (0.16, 0.14, 0.20)
ROJO_T = (0.86, 0.10, 0.16)
VERDE_T = (0.14, 0.62, 0.38)


def registrar(m, pj):
    PISO = pj.PISO
    W = m.W

    pj.ESTILOS["clienta"] = {"ropa": (0.90, 0.36, 0.38), "pantalon": (0.24, 0.23, 0.30), "pelo": (0.32, 0.20, 0.12),
                             "peinado": "largo"}
    pj.ESTILOS["penn"] = dict(pj.ESTILOS["profesor"], ropa=(0.36, 0.32, 0.42))

    def rect(cr, x, y, w, h, c, a=1.0):
        cr.new_path()
        cr.rectangle(x, y, w, h)
        m.rellenar(cr, c, a)

    def circ(cr, x, y, r, c, a=1.0):
        cr.new_path()
        cr.arc(x, y, r, 0, 2 * math.pi)
        m.rellenar(cr, c, a)

    # ---------------------------------------------------------------- productos (centrados, ~90 px)
    def p_vela(cr):
        rect(cr, -24, -20, 48, 62, (0.97, 0.93, 0.84))
        rect(cr, -24, 30, 48, 12, (0.86, 0.80, 0.70))
        rect(cr, -2, -34, 4, 16, TINTA)
        cr.new_path()
        cr.move_to(0, -66)
        cr.curve_to(16, -46, 10, -32, 0, -32)
        cr.curve_to(-10, -32, -16, -46, 0, -66)
        m.rellenar(cr, (1.0, 0.55, 0.20))

    def p_vaso(cr):
        cr.new_path()
        cr.move_to(-30, -42)
        cr.line_to(30, -42)
        cr.line_to(22, 42)
        cr.line_to(-22, 42)
        cr.close_path()
        m.rellenar(cr, (0.88, 0.90, 0.95))
        rect(cr, -16, -30, 8, 56, (1, 1, 1), 0.8)

    def p_bolsa(cr):
        cr.new_path()
        m.rrect(cr, -40, -30, 80, 76, 8)
        m.rellenar(cr, ROJO_T)
        cr.new_path()
        cr.arc(0, -30, 22, math.pi, 2 * math.pi)
        cr.set_line_width(8)
        cr.set_source_rgb(0.98, 0.98, 0.98)
        cr.stroke()

    def p_peluche(cr):
        marron = (0.66, 0.46, 0.30)
        circ(cr, -24, -40, 14, marron)
        circ(cr, 24, -40, 14, marron)
        circ(cr, 0, 22, 32, marron)
        circ(cr, 0, -20, 30, marron)
        circ(cr, 0, -12, 13, (0.93, 0.84, 0.72))
        circ(cr, -11, -27, 4.5, TINTA)
        circ(cr, 11, -27, 4.5, TINTA)
        circ(cr, 0, -15, 4, TINTA)

    def p_lampara(cr):
        cr.new_path()
        cr.move_to(-18, -48)
        cr.line_to(18, -48)
        cr.line_to(36, 0)
        cr.line_to(-36, 0)
        cr.close_path()
        m.rellenar(cr, (1.0, 0.86, 0.66))
        rect(cr, -4, 0, 8, 36, TINTA)
        rect(cr, -24, 36, 48, 9, TINTA)

    def p_caja(cr):
        rect(cr, -42, -34, 84, 72, (0.80, 0.63, 0.45))
        rect(cr, -7, -34, 14, 72, (0.68, 0.52, 0.36))

    def p_planta(cr):
        for a in (-0.7, -0.25, 0.25, 0.7):
            cr.save()
            cr.translate(0, 2)
            cr.rotate(a)
            cr.new_path()
            cr.move_to(0, 0)
            cr.curve_to(-16, -30, -8, -58, 0, -66)
            cr.curve_to(8, -58, 16, -30, 0, 0)
            m.rellenar(cr, VERDE_T)
            cr.restore()
        cr.new_path()
        cr.move_to(-26, 2)
        cr.line_to(26, 2)
        cr.line_to(19, 44)
        cr.line_to(-19, 44)
        cr.close_path()
        m.rellenar(cr, (0.80, 0.42, 0.30))

    def p_cojin(cr):
        cr.new_path()
        m.rrect(cr, -38, -30, 76, 64, 18)
        m.rellenar(cr, (0.62, 0.42, 0.78))
        circ(cr, 0, 2, 6, (0.50, 0.32, 0.66))

    PRODUCTOS = {"vela": p_vela, "vaso": p_vaso, "bolsa": p_bolsa, "peluche": p_peluche, "lampara": p_lampara,
                 "caja": p_caja, "planta": p_planta, "cojin": p_cojin}

    HUECOS = [(-88, 52), (4, 56), (96, 52), (-44, -22), (52, -22), (-96, -30), (4, -96), (104, -92), (-70, -104)]

    def ic_carro(cr, t, items=None, **kw):
        """Carrito de compras de costado. `items` = [[producto, segundo en que cae], ...]."""
        if items is None:
            items = [[n, 0.05 + 0.13 * i] for i, n in enumerate(
                ["caja", "lampara", "vela", "planta", "bolsa", "peluche", "vaso", "cojin", "vela"])]
        gris = (0.86, 0.85, 0.88)
        # estructura
        cr.set_line_cap(1)
        for (xa, ya, xb, yb, g) in ((-150, 118, -128, 176, 12), (158, 118, 150, 176, 12), (-128, 176, 150, 176, 12),
                                    (-178, -62, -232, -128, 14)):
            cr.new_path()
            cr.move_to(xa, ya)
            cr.line_to(xb, yb)
            cr.set_line_width(g)
            cr.set_source_rgb(*gris)
            cr.stroke()
        cr.new_path()
        cr.move_to(-262, -128)
        cr.line_to(-206, -128)
        cr.set_line_width(20)
        cr.set_source_rgb(*ROJO_T)
        cr.stroke()
        for xr in (-104, 132):
            circ(cr, xr, 200, 26, TINTA)
            circ(cr, xr, 200, 10, gris)
        # canasto (fondo translúcido), productos y rejilla por delante
        def canasto():
            cr.new_path()
            cr.move_to(-178, -62)
            cr.line_to(196, -62)
            cr.line_to(158, 118)
            cr.line_to(-150, 118)
            cr.close_path()
        canasto()
        m.rellenar(cr, (1, 1, 1), 0.16)
        for i, (nombre, entra) in enumerate(items):
            te = t - entra
            if te < 0:
                continue
            hx, hy = HUECOS[i % len(HUECOS)]
            cae = 1 - m.ease_out_back(min(1.0, te / 0.35))
            cr.save()
            cr.translate(hx, hy - 330 * max(0.0, cae))
            cr.rotate(0.12 * math.sin(i * 2.1))
            cr.scale(1.05, 1.05)
            PRODUCTOS[nombre](cr)
            cr.restore()
        canasto()
        cr.set_line_width(10)
        cr.set_source_rgb(*gris)
        cr.stroke()
        for k in range(1, 8):
            f = k / 8
            cr.new_path()
            cr.move_to(-178 + 374 * f, -62)
            cr.line_to(-150 + 308 * f, 118)
            cr.set_line_width(4)
            cr.set_source_rgba(*gris, 0.75)
            cr.stroke()
        for yy in (-2, 58):
            f = (yy + 62) / 180
            cr.new_path()
            cr.move_to(-178 + 28 * f, yy)
            cr.line_to(196 - 38 * f, yy)
            cr.set_line_width(4)
            cr.set_source_rgba(*gris, 0.75)
            cr.stroke()
    m.ICONOS["carro"] = ic_carro

    # ---------------------------------------------------------------- plano de la tienda
    def recorrido(x0, y0, w, h):
        ys = [y0 + 120 + i * (h - 200) / 4 for i in range(5)]
        xl, xr = x0 + 110, x0 + w - 110
        pts = []
        for i, y in enumerate(ys):
            pts += [(xl, y), (xr, y)] if i % 2 == 0 else [(xr, y), (xl, y)]
        return pts, ys, xl, xr

    def largo_de(pts):
        return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))

    def tramo(pts, s):
        """Puntos del recorrido hasta la distancia s, y dirección en la punta."""
        out = [pts[0]]
        d = (1, 0)
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            d = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
            if s >= L:
                out.append(b)
                s -= L
            else:
                out.append((a[0] + d[0] * s, a[1] + d[1] * s))
                break
        return out, d

    def trazo(cr, pts, ancho, color, a=1.0):
        cr.new_path()
        cr.move_to(*pts[0])
        for q in pts[1:]:
            cr.line_to(*q)
        cr.set_line_width(ancho)
        cr.set_line_join(1)
        cr.set_line_cap(1)
        cr.set_source_rgba(*color, a)
        cr.stroke()

    SECCIONES = ["SALAS", "COCINAS", "DORMITORIOS", "BAÑOS", "DECORACIÓN"]

    def plano(cr, t, x0, y0, w, h, s_rel, atajo=-1.0, chico=False, cuenta=None):
        """Dibuja el plano. s_rel = avance del recorrido (0 a 1); atajo = avance del atajo (0 a 1, o -1)."""
        cr.new_path()
        m.rrect(cr, x0 + 8, y0 + 10, w, h, 34)
        m.rellenar(cr, (0, 0, 0), 0.30)
        cr.new_path()
        m.rrect(cr, x0, y0, w, h, 34)
        m.rellenar(cr, CREMA)
        pts, ys, xl, xr = recorrido(x0, y0, w, h)
        L = largo_de(pts)
        trazo(cr, pts, 54 if not chico else 30, (0.84, 0.81, 0.84))
        if not chico:
            for i, y in enumerate(ys):                       # nombres de las secciones
                pasada = s_rel * L >= (i + 0.5) * (L / 5)
                m.texto(cr, SECCIONES[i], x0 + w / 2, y - 66, 36, ROJO_T if pasada else (0.50, 0.47, 0.52))
            n_fl = 26
            for k in range(n_fl):                            # flechas del piso
                seg, d = tramo(pts, L * (k + 0.5) / n_fl)
                px, py = seg[-1]
                cr.save()
                cr.translate(px, py)
                cr.rotate(math.atan2(d[1], d[0]))
                cr.new_path()
                cr.move_to(-9, -12)
                cr.line_to(9, 0)
                cr.line_to(-9, 12)
                cr.set_line_width(6)
                cr.set_line_cap(1)
                cr.set_source_rgba(1, 1, 1, 0.9)
                cr.stroke()
                cr.restore()
        if s_rel > 0:
            hecho, d = tramo(pts, L * min(1.0, s_rel))
            if len(hecho) > 1:
                trazo(cr, hecho, 26 if not chico else 14, ROJO_T)
            px, py = hecho[-1]
            if not chico:
                circ(cr, px, py, 30 + 3 * math.sin(t * 8), (1, 1, 1))
                circ(cr, px, py, 21, ROJO_T)
        if not chico:
            m.placa(cr, "ENTRADA", xl - 10, y0 + 40, 30, 1.0, TINTA, (1, 1, 1))
            m.placa(cr, "CAJA", xr - 10, y0 + h - 38, 34, 1.0, ROJO_T, (1, 1, 1))
            if cuenta is not None:
                m.placa(cr, f"EN EL CARRITO: {cuenta}", x0 + w - 185, y0 + 40, 27, 1.0, (1, 1, 1), TINTA)
        if atajo >= 0:
            xa = x0 + w * 0.21
            ya, yb = ys[0], ys[0] + (ys[-1] - ys[0]) * min(1.0, atajo)
            cr.new_path()
            cr.move_to(xa, ya)
            cr.line_to(xa, yb)
            cr.set_line_width(16)
            cr.set_dash([26, 18])
            cr.set_line_cap(0)
            cr.set_source_rgb(*VERDE_T)
            cr.stroke()
            cr.set_dash([])
            cr.new_path()
            cr.move_to(xa - 26, yb - 6)
            cr.line_to(xa, yb + 26)
            cr.line_to(xa + 26, yb - 6)
            cr.close_path()
            m.rellenar(cr, VERDE_T)
            if atajo >= 0.5:
                m.placa(cr, "ATAJO", xa, (ys[1] + ys[2]) / 2, 44, m.ease_out_back((atajo - 0.5) / 0.3),
                        VERDE_T, (1, 1, 1))

    def ic_mapa_mini(cr, t, **kw):
        plano(cr, t, -190, -180, 380, 360, min(1.0, t / 2.5), chico=True)
    m.ICONOS["mapa_mini"] = ic_mapa_mini

    def titulo_de(cr, p, t):
        if p.get("titulos"):
            ti, txt = max((x for x in p["titulos"] if x[0] <= t), key=lambda x: x[0], default=p["titulos"][0])
            m.titular(cr, txt, max(0.0, t - ti))
        else:
            m.titular(cr, p.get("titulo", ""), t)

    def esc_mapa(cr, t, p):
        """Plano con el recorrido. Campos: avance [t0, t1] o completo, atajos {entra}, sellos, elementos, titulos."""
        if p.get("completo"):
            s = 1.0
        else:
            t0, t1 = p.get("avance", [0.3, 5.0])
            s = m.ease_in_out(m.clamp((t - t0) / max(0.1, t1 - t0)))
        at = -1.0
        if p.get("atajos") and t >= p["atajos"].get("entra", 0):
            at = m.clamp((t - p["atajos"]["entra"]) / 0.9)
        k = m.ease_out_back(min(1.0, t / 0.4)) if not p.get("sin_entrada") else 1.0
        cr.save()
        cr.translate(W / 2, 840)
        cr.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
        cr.translate(-W / 2, -840)
        plano(cr, t, 80, 470, 920, 740, s, at, cuenta=int(round(s * p["cuenta"])) if p.get("cuenta") else None)
        cr.restore()
        for el in p.get("elementos", []):
            te = t - el.get("entra", 0)
            if te < 0 or t > el.get("sale", 1e9):
                continue
            ke = m.ease_out_back(te / 0.4)
            mm = 290 * el.get("escala", 1.0)
            cr.new_path()
            m.rrect(cr, el["x"] - mm * ke, el["y"] - mm * ke, 2 * mm * ke, 2 * mm * ke, 40)
            m.rellenar(cr, m.FONDO1, 0.94)
            cr.new_path()
            m.rrect(cr, el["x"] - mm * ke, el["y"] - mm * ke, 2 * mm * ke, 2 * mm * ke, 40)
            cr.set_line_width(8)
            cr.set_source_rgb(*m.DORADO)
            cr.stroke()
            m.dibujar_icono(cr, el["icono"], te, el["x"], el["y"], el.get("escala", 1.0) * ke, **el.get("args", {}))
        for se in p.get("sellos", []):
            if t <= se.get("sale", 1e9):
                m.sello_en(cr, se["texto"], se.get("x", W / 2), se.get("y", 840), t - se.get("entra", 0),
                           se.get("tam", 110), tuple(se["color"]) if se.get("color") else None)
        titulo_de(cr, p, t)
    m.ESCENAS["i_mapa"] = esc_mapa

    # ---------------------------------------------------------------- decorados
    def dec_tienda_frente(cr, t, W_, H, dibujar_icono):
        """Frente de la tienda al atardecer: galpón claro con franja roja y puertas de vidrio."""
        import cairo
        g = cairo.LinearGradient(0, 0, 0, PISO)
        g.add_color_stop_rgb(0, 0.36, 0.20, 0.42)
        g.add_color_stop_rgb(1, 0.98, 0.66, 0.50)
        cr.new_path()
        cr.rectangle(0, 0, W_, PISO)
        cr.set_source(g)
        cr.fill()
        rect(cr, 110, 470, 1080, PISO - 470, (0.93, 0.91, 0.88))            # galpón
        rect(cr, 110, 470, 1080, 30, (0.80, 0.77, 0.75))
        rect(cr, 110, 700, 1080, 34, ROJO_T)
        rect(cr, 560, 800, 380, PISO - 800, (0.30, 0.26, 0.34))            # puertas
        rect(cr, 574, 814, 170, PISO - 814, (0.52, 0.48, 0.60))
        rect(cr, 756, 814, 170, PISO - 814, (0.52, 0.48, 0.60))
        rect(cr, 590, 830, 30, 200, (1, 1, 1), 0.18)
        rect(cr, 772, 830, 30, 200, (1, 1, 1), 0.18)
        rect(cr, 0, PISO - 46, W_, 46, (0.46, 0.42, 0.46))                  # vereda
    pj.DECORADOS_EXTRA["tienda_frente"] = dec_tienda_frente

    def dec_pasillo(cr, t, W_, H, dibujar_icono):
        """Pasillo de la tienda: estanterías de madera con productos y flechas en el piso."""
        rect(cr, 0, 0, W_, PISO, (0.94, 0.91, 0.86))
        rnd = random.Random(12)
        colores = [(0.86, 0.30, 0.32), (0.20, 0.58, 0.42), (0.93, 0.88, 0.80), (0.60, 0.42, 0.76), (0.95, 0.60, 0.45),
                   (0.80, 0.63, 0.45)]
        for ex in (40, 400, 760):                                          # tres estanterías
            rect(cr, ex, 470, 300, 560, MADERA)
            for fila in range(4):
                y = 490 + fila * 135
                rect(cr, ex + 14, y, 272, 112, (0.86, 0.72, 0.56))
                x = ex + 26
                while x < ex + 250:
                    w = rnd.choice([44, 58, 70])
                    h = rnd.choice([58, 76, 92])
                    cr.new_path()
                    m.rrect(cr, x, y + 112 - h, w, h, 6)
                    m.rellenar(cr, rnd.choice(colores))
                    x += w + 10
        rect(cr, 0, 1030, W_, PISO - 1030, (0.82, 0.78, 0.74))              # piso
        for i in range(5):                                                 # flechas que avanzan
            x = (i * 260 + t * 60) % (W_ + 260) - 130
            cr.new_path()
            cr.move_to(x - 60, 1130)
            cr.line_to(x + 20, 1130)
            cr.line_to(x + 20, 1104)
            cr.line_to(x + 70, 1146)
            cr.line_to(x + 20, 1188)
            cr.line_to(x + 20, 1162)
            cr.line_to(x - 60, 1162)
            cr.close_path()
            m.rellenar(cr, (1, 1, 1), 0.85)
    pj.DECORADOS_EXTRA["pasillo"] = dec_pasillo
