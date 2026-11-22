# -*- coding: utf-8 -*-
"""Arte compartido de la tanda 3 (Shorts 020 a 026).

Cada JSON lo carga con `"extension": "../tanda3_ext.py"`. Aporta íconos, decorados, estilos de
personaje y un objeto de mano. Regla del canal: nunca azul con amarillo; las marcas van como texto
en carteles claros (campo `placas`), sin logotipos.

Íconos (centrados, tamaño base ~400 px): botella, tractor, deportivo, frasco, cacao, avellanas,
barra, aspiradora (tipo: bolsa | ciclon | prototipo), estufa, masa, lata_masa, disco_duro, bitcoin.
Decorados: pedestal, campo, pasteleria, pueblo_rio, cementerio, casa, pared, pared_limpia, basurero.
"""
import math
import random

TINTA = (0.14, 0.12, 0.18)
ROJO_T = (0.86, 0.10, 0.16)
CREMA = (0.95, 0.92, 0.86)
MADERA = (0.62, 0.44, 0.30)
CHOCO = (0.36, 0.20, 0.12)
VERDE_C = (0.36, 0.62, 0.40)


def registrar(m, pj):
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

    def linea(cr, x1, y1, x2, y2, g, c, a=1.0):
        cr.new_path()
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.set_line_width(g)
        cr.set_line_cap(1)
        cr.set_source_rgba(c[0], c[1], c[2], a)
        cr.stroke()

    # ================================================================ íconos
    def ic_botella(cr, t, etiqueta=None, texto="COLA", liquido=None, **kw):
        et = tuple(etiqueta) if etiqueta else ROJO_T
        liq = tuple(liquido) if liquido else (0.24, 0.11, 0.07)
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.03)

        def contorno():
            cr.new_path()
            cr.move_to(-24, -196)
            cr.line_to(24, -196)
            cr.curve_to(24, -120, 70, -110, 70, -40)
            cr.curve_to(70, 20, 56, 40, 60, 100)
            cr.curve_to(64, 150, 70, 170, 62, 200)
            cr.line_to(-62, 200)
            cr.curve_to(-70, 170, -64, 150, -60, 100)
            cr.curve_to(-56, 40, -70, 20, -70, -40)
            cr.curve_to(-70, -110, -24, -120, -24, -196)
            cr.close_path()
        contorno()
        m.rellenar(cr, liq)
        contorno()
        cr.save()
        cr.clip()
        rect(cr, -70, -200, 140, 70, (0.80, 0.84, 0.86), 0.55)      # cuello sin líquido
        rect(cr, -46, -190, 16, 380, (1, 1, 1), 0.22)                # brillo
        cr.restore()
        rr(cr, -30, -224, 60, 30, 8, _osc(et))
        rr(cr, -74, -28, 148, 96, 12, et)
        m.texto(cr, texto, 0, 20, 34 if len(texto) <= 5 else 26, (1, 1, 1))
        cr.restore()

    def _osc(c, f=0.75):
        return tuple(v * f for v in c)

    def ic_tractor(cr, t, color=None, **kw):
        col = tuple(color) if color else (0.92, 0.38, 0.16)
        cr.save()
        cr.translate(0, math.sin(t * 9) * 3)
        rect(cr, 96, -150, 18, 110, TINTA)                               # escape
        circ(cr, 105, -165 - (t * 40) % 60, 14, (0.8, 0.8, 0.84), 0.5)
        rr(cr, -30, -60, 250, 130, 18, col)                              # capó
        rr(cr, -170, -190, 170, 150, 16, _osc(col, 0.85))                # cabina
        rr(cr, -150, -170, 130, 86, 10, (0.86, 0.90, 0.94))
        rect(cr, 180, -30, 34, 60, (0.25, 0.24, 0.30))                   # parrilla
        cr.new_path()
        cr.arc(-80, 80, 150, math.pi, 2 * math.pi)                       # guardabarros
        cr.close_path()
        m.rellenar(cr, _osc(col, 0.7))
        for (x, y, r) in ((-80, 80, 124), (150, 130, 74)):
            circ(cr, x, y, r, TINTA)
            circ(cr, x, y, r * 0.55, (0.86, 0.84, 0.80))
            circ(cr, x, y, r * 0.2, col)
            for k in range(8):
                a = t * 3 + k * math.pi / 4
                linea(cr, x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62,
                      x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92, 10, (0.30, 0.28, 0.34))
        cr.restore()

    def ic_deportivo(cr, t, color=None, **kw):
        col = tuple(color) if color else ROJO_T
        cr.save()
        cr.translate(0, math.sin(t * 7) * 2)
        cr.new_path()
        cr.move_to(-270, 70)
        cr.line_to(-262, 6)
        cr.curve_to(-210, -10, -170, -60, -100, -66)
        cr.line_to(10, -66)
        cr.curve_to(70, -62, 120, -24, 170, -10)
        cr.curve_to(230, -6, 272, 6, 276, 40)
        cr.line_to(276, 70)
        cr.close_path()
        m.rellenar(cr, col)
        cr.new_path()                                                    # ventanas
        cr.move_to(-156, -14)
        cr.curve_to(-146, -40, -116, -50, -90, -52)
        cr.line_to(4, -52)
        cr.curve_to(46, -48, 80, -30, 104, -14)
        cr.close_path()
        m.rellenar(cr, (0.80, 0.84, 0.90))
        rect(cr, -36, -52, 10, 40, col)
        rect(cr, -270, 52, 546, 18, _osc(col, 0.7))
        circ(cr, 262, 22, 12, (1.0, 0.95, 0.85))
        for x in (-160, 160):
            circ(cr, x, 74, 58, TINTA)
            circ(cr, x, 74, 30, (0.86, 0.84, 0.80))
            for k in range(5):
                a = t * 5 + k * 2 * math.pi / 5
                linea(cr, x, 74, x + math.cos(a) * 28, 74 + math.sin(a) * 28, 7, (0.45, 0.44, 0.50))
        cr.restore()

    def ic_frasco(cr, t, etiqueta="", **kw):
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.025)
        rr(cr, -140, -130, 280, 330, 48, CHOCO)
        rr(cr, -140, -130, 280, 330, 48, (1, 1, 1), 0.06)
        rect(cr, -112, -110, 22, 280, (1, 1, 1), 0.16)
        rr(cr, -128, -206, 256, 86, 14, (0.97, 0.97, 0.97))
        for k in range(9):
            rect(cr, -116 + k * 28, -196, 6, 66, (0.82, 0.82, 0.84))
        rr(cr, -122, -34, 244, 150, 16, CREMA)
        if etiqueta:
            tam = 54
            while m.ancho_texto(cr, etiqueta, tam) > 216 and tam > 22:
                tam -= 2
            m.texto(cr, etiqueta, 0, 42, tam, ROJO_T)
        else:
            circ(cr, -50, 40, 34, (0.70, 0.48, 0.28))
            circ(cr, 30, 44, 40, (0.50, 0.30, 0.18))
        cr.restore()

    def ic_cacao(cr, t, **kw):
        cr.save()
        cr.rotate(-0.5 + math.sin(t * 2) * 0.04)
        cr.new_path()
        cr.move_to(-190, 0)
        cr.curve_to(-120, -130, 120, -130, 190, 0)
        cr.curve_to(120, 130, -120, 130, -190, 0)
        cr.close_path()
        m.rellenar(cr, (0.78, 0.42, 0.20))
        for dy in (-60, -20, 20, 60):
            cr.new_path()
            cr.move_to(-170, dy * 0.2)
            cr.curve_to(-80, dy * 1.4, 80, dy * 1.4, 170, dy * 0.2)
            cr.set_line_width(8)
            cr.set_source_rgb(0.56, 0.28, 0.14)
            cr.stroke()
        cr.restore()
        for (x, y, a) in ((120, 130, 0.4), (40, 170, -0.3)):               # granos
            cr.save()
            cr.translate(x, y)
            cr.rotate(a)
            cr.scale(1.5, 1)
            circ(cr, 0, 0, 26, CHOCO)
            cr.restore()

    def ic_avellanas(cr, t, **kw):
        pos = [(-110, 90), (0, 100), (110, 90), (-56, 0), (56, 0), (0, -88)]
        for i, (x, y) in enumerate(pos):
            k = m.ease_out_back((t - i * 0.08) / 0.35)
            if k <= 0.01:
                continue
            cr.save()
            cr.translate(x, y)
            cr.scale(k, k)
            circ(cr, 0, 6, 60, (0.70, 0.46, 0.26))
            cr.new_path()
            cr.arc(0, 6, 60, math.pi * 1.12, math.pi * 1.88)
            cr.close_path()
            m.rellenar(cr, (0.88, 0.74, 0.54))
            circ(cr, -20, -10, 10, (1, 1, 1), 0.25)
            cr.restore()

    def ic_barra(cr, t, **kw):
        rr(cr, -200, -76, 400, 160, 26, CHOCO)
        rr(cr, -200, -76, 190, 160, 26, CREMA)
        rect(cr, -40, -76, 30, 160, CREMA)
        for k in range(4):
            linea(cr, 20 + k * 44, -60, 20 + k * 44, 68, 6, (0.26, 0.14, 0.08))
        rect(cr, -180, -50, 12, 108, (1, 1, 1), 0.3)

    def ic_aspiradora(cr, t, tipo="bolsa", **kw):
        cr.save()
        if tipo == "bolsa":
            linea(cr, 30, -210, -10, 60, 16, (0.55, 0.56, 0.62))
            rr(cr, 2, -238, 70, 26, 10, TINTA)
            cr.save()
            cr.translate(-20, -40)
            cr.rotate(-0.15)
            infla = 1 + 0.04 * math.sin(t * 6)
            cr.scale(infla, 1)
            rr(cr, -62, -110, 124, 230, 56, (0.74, 0.44, 0.42))
            rr(cr, -40, -80, 26, 160, 12, (1, 1, 1), 0.15)
            cr.restore()
            rr(cr, -150, 110, 260, 70, 20, (0.42, 0.43, 0.50))
            rect(cr, -150, 170, 260, 12, TINTA)
        elif tipo == "ciclon":
            linea(cr, 60, -220, 10, 70, 18, (0.62, 0.63, 0.70))
            rr(cr, 30, -246, 76, 28, 10, (0.62, 0.30, 0.76))
            circ(cr, -10, -40, 96, (0.86, 0.84, 0.94), 0.9)
            for k in range(3):
                cr.new_path()
                cr.arc(-10, -40, 34 + k * 22, t * 7 + k * 2, t * 7 + k * 2 + 3.6)
                cr.set_line_width(9)
                cr.set_source_rgba(0.62, 0.30, 0.76, 0.85)
                cr.stroke()
            rr(cr, -58, -150, 96, 30, 10, (0.62, 0.30, 0.76))
            rr(cr, -150, 110, 260, 70, 24, (0.56, 0.57, 0.64))
            circ(cr, -110, 180, 22, ROJO_T)
            circ(cr, 70, 180, 22, ROJO_T)
        else:                                                            # prototipo de cartón
            carton = (0.80, 0.63, 0.45)
            cr.new_path()
            cr.move_to(-90, -160)
            cr.line_to(90, -160)
            cr.line_to(34, 80)
            cr.line_to(-34, 80)
            cr.close_path()
            m.rellenar(cr, carton)
            for yy in (-110, -30, 40):
                rect(cr, -80 + (yy + 160) * 0.22, yy, 160 - (yy + 160) * 0.44, 16, (0.90, 0.86, 0.80))
            rr(cr, -110, -196, 220, 44, 10, _osc(carton, 0.85))
            linea(cr, 110, -174, 190, -230, 14, (0.55, 0.56, 0.62))
            rr(cr, -130, 80, 260, 80, 16, (0.46, 0.47, 0.54))
            rect(cr, -130, 150, 260, 12, TINTA)
        cr.restore()

    def ic_estufa(cr, t, **kw):
        rect(cr, -30, -230, 60, 150, (0.20, 0.19, 0.24))                    # caño
        for k in range(3):                                                 # humo
            f = ((t * 0.5 + k / 3) % 1)
            circ(cr, 30 * math.sin(f * 6 + k), -250 - f * 150, 26 + 30 * f, (0.25, 0.23, 0.26), 0.5 * (1 - f))
        rr(cr, -130, -90, 260, 260, 26, (0.22, 0.21, 0.26))
        rr(cr, -84, -30, 168, 130, 14, (0.10, 0.09, 0.11))
        brillo = 0.75 + 0.25 * math.sin(t * 9)
        rr(cr, -70, -16, 140, 102, 10, (1.0, 0.50 * brillo, 0.12))
        for k in range(4):
            rect(cr, -58 + k * 36, -16, 8, 102, (0.10, 0.09, 0.11))
        rect(cr, -150, 170, 300, 24, (0.16, 0.15, 0.19))
        rect(cr, -110, 194, 22, 30, (0.16, 0.15, 0.19))
        rect(cr, 88, 194, 22, 30, (0.16, 0.15, 0.19))

    COLORES_MASA = [(0.90, 0.26, 0.30), (0.24, 0.66, 0.44), (0.62, 0.40, 0.80), (0.98, 0.58, 0.30)]

    def ic_masa(cr, t, colores=False, **kw):
        if colores:
            pos = [(-100, 40), (10, 70), (110, 30), (-40, -60)]
            for i, (x, y) in enumerate(pos):
                k = m.ease_out_back((t - i * 0.12) / 0.35)
                if k > 0.01:
                    circ(cr, x, y, 78 * k, COLORES_MASA[i])
                    circ(cr, x - 24 * k, y - 24 * k, 16 * k, (1, 1, 1), 0.25)
        else:
            col = (0.92, 0.89, 0.80)
            late = 1 + 0.03 * math.sin(t * 4)
            cr.save()
            cr.scale(late, 2 - late)
            for (x, y, r) in ((-80, 20, 90), (30, 30, 110), (110, 10, 70), (-10, -50, 84)):
                circ(cr, x, y, r, col)
            circ(cr, -50, -40, 22, (1, 1, 1), 0.5)
            cr.restore()

    def ic_lata_masa(cr, t, texto="MASA", **kw):
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.03)
        for (x, y, r, c) in ((-40, -150, 70, COLORES_MASA[2]), (40, -160, 60, COLORES_MASA[2]), (0, -200, 56, COLORES_MASA[2])):
            circ(cr, x, y, r, c)
        rr(cr, -130, -110, 260, 310, 26, (0.97, 0.96, 0.94))
        rect(cr, -130, -110, 260, 46, ROJO_T)
        rect(cr, -130, 150, 260, 50, ROJO_T)
        rect(cr, -106, -60, 20, 200, (0, 0, 0), 0.05)
        tam = 62
        while m.ancho_texto(cr, texto, tam) > 230 and tam > 24:
            tam -= 2
        m.texto(cr, texto, 0, 44, tam, ROJO_T)
        cr.restore()

    def ic_disco_duro(cr, t, **kw):
        cr.save()
        cr.rotate(math.sin(t * 2) * 0.03)
        rr(cr, -180, -130, 360, 260, 26, (0.56, 0.58, 0.66))
        rr(cr, -160, -110, 320, 220, 18, (0.70, 0.72, 0.79))
        circ(cr, -40, 0, 92, (0.86, 0.87, 0.92))
        circ(cr, -40, 0, 26, (0.56, 0.58, 0.66))
        cr.new_path()
        cr.arc(-40, 0, 62, t * 4, t * 4 + 1.2)
        cr.set_line_width(8)
        cr.set_source_rgba(1, 1, 1, 0.8)
        cr.stroke()
        linea(cr, 120, 80, 10, 20, 16, (0.40, 0.41, 0.48))
        circ(cr, 120, 80, 22, (0.40, 0.41, 0.48))
        circ(cr, 140, -86, 9, (0.24, 0.86, 0.52) if int(t * 3) % 2 else (0.14, 0.50, 0.30))
        cr.restore()

    def ic_bitcoin(cr, t, **kw):
        ancho = abs(math.cos(t * 1.6)) * 0.35 + 0.65
        cr.save()
        cr.scale(ancho, 1)
        circ(cr, 0, 0, 180, (0.80, 0.44, 0.06))
        circ(cr, 0, 0, 158, (0.97, 0.58, 0.10))
        m.texto(cr, "B", 4, 4, 230, (1, 1, 1))
        for x in (-22, 26):
            rect(cr, x - 7, -124, 14, 30, (1, 1, 1))
            rect(cr, x - 7, 96, 14, 30, (1, 1, 1))
        cr.restore()

    m.ICONOS.update({"botella": ic_botella, "tractor": ic_tractor, "deportivo": ic_deportivo, "frasco": ic_frasco,
                     "cacao": ic_cacao, "avellanas": ic_avellanas, "barra": ic_barra, "aspiradora": ic_aspiradora,
                     "estufa": ic_estufa, "masa": ic_masa, "lata_masa": ic_lata_masa, "disco_duro": ic_disco_duro,
                     "bitcoin": ic_bitcoin})

    # ================================================================ decorados
    def degradado(cr, W, c1, c2, y1=None):
        import cairo
        g = cairo.LinearGradient(0, 0, 0, y1 or PISO)
        g.add_color_stop_rgb(0, *c1)
        g.add_color_stop_rgb(1, *c2)
        cr.new_path()
        cr.rectangle(0, 0, W, PISO)
        cr.set_source(g)
        cr.fill()

    def dec_pedestal(cr, t, W, H, dibujar_icono):
        cr.new_path()
        cr.move_to(W / 2 - 70, 380)
        cr.line_to(W / 2 + 70, 380)
        cr.line_to(W / 2 + 440, 1010)
        cr.line_to(W / 2 - 440, 1010)
        cr.close_path()
        m.rellenar(cr, (1, 1, 1), 0.07 + 0.02 * math.sin(t * 2))
        rr(cr, W / 2 - 340, 1150, 680, 44, 14, (0.93, 0.90, 0.88))
        rect(cr, W / 2 - 300, 1194, 600, PISO - 1194, (0.72, 0.68, 0.70))
        rnd = random.Random(5)
        for _ in range(14):
            x, y = rnd.uniform(140, W - 140), rnd.uniform(470, 960)
            k = 0.5 + 0.5 * math.sin(t * 3 + x)
            circ(cr, x, y, 5 * k, (1, 1, 1), 0.5 * k)
    pj.DECORADOS_EXTRA["pedestal"] = dec_pedestal

    def dec_cochera(cr, t, W, H, dibujar_icono):
        """Taller sencillo: pared clara, tablero de herramientas y piso de cemento."""
        rect(cr, 0, 0, W, PISO, (0.84, 0.81, 0.80))
        for i in range(9):
            rect(cr, 0, 420 + i * 78, W, 4, (0.76, 0.73, 0.72))
        rr(cr, 380, 470, 320, 220, 10, (0.72, 0.56, 0.40))
        for (x, y, w, h) in ((410, 500, 14, 150), (450, 500, 60, 22), (530, 500, 14, 120), (570, 500, 46, 46),
                             (640, 500, 14, 160)):
            rr(cr, x, y, w, h, 5, (0.30, 0.29, 0.34))
        rect(cr, 0, 1090, W, PISO - 1090, (0.62, 0.60, 0.62))
        rect(cr, 0, 1076, W, 16, (0.70, 0.68, 0.70))
    pj.DECORADOS_EXTRA["cochera"] = dec_cochera

    def dec_campo(cr, t, W, H, dibujar_icono):
        degradado(cr, W, (0.98, 0.78, 0.60), (0.99, 0.92, 0.80))
        circ(cr, 860, 520, 70, (1.0, 0.96, 0.86))
        for (cx, cy, r, c) in ((200, 1000, 520, (0.42, 0.66, 0.44)), (860, 1040, 560, (0.34, 0.58, 0.38))):
            circ(cr, cx, cy + 80, r, c)
        rect(cr, 0, 960, W, PISO - 960, (0.50, 0.70, 0.42))
        for k in range(9):
            linea(cr, -100 + k * 160, PISO, 380 + k * 40, 960, 6, (0.40, 0.60, 0.36))
    pj.DECORADOS_EXTRA["campo"] = dec_campo

    def dec_pasteleria(cr, t, W, H, dibujar_icono):
        rect(cr, 0, 0, W, PISO, (0.96, 0.89, 0.80))
        for i in range(12):
            rect(cr, i * 96, 380, 48, 660, (0.93, 0.84, 0.74))
        for ey in (560, 760):
            rect(cr, 560, ey, 470, 16, MADERA)
            rnd = random.Random(ey)
            x = 580
            while x < 990:
                w = rnd.choice([50, 64, 76])
                h = rnd.choice([70, 96, 120])
                rr(cr, x, ey - h, w, h, 10, rnd.choice([CHOCO, (0.86, 0.60, 0.42), (0.93, 0.86, 0.74), (0.72, 0.36, 0.34)]))
                x += w + 16
        rect(cr, 0, 1040, W, PISO - 1040, MADERA)
        rect(cr, 0, 1040, W, 22, (0.74, 0.56, 0.40))
    pj.DECORADOS_EXTRA["pasteleria"] = dec_pasteleria

    def fabrica(cr, x, y, w, h, c, humo_t):
        rect(cr, x, y, w, h, c)
        rect(cr, x + w - 70, y - 150, 46, 150, _osc(c, 0.8))
        for k in range(3):
            f = ((humo_t * 0.4 + k / 3) % 1)
            circ(cr, x + w - 47 + 24 * f, y - 170 - f * 110, 22 + 26 * f, (1, 1, 1), 0.5 * (1 - f))
        for i in range(3):
            cr.new_path()
            cr.move_to(x + i * w / 3, y)
            cr.line_to(x + i * w / 3, y - 60)
            cr.line_to(x + (i + 1) * w / 3, y)
            cr.close_path()
            m.rellenar(cr, _osc(c, 0.9))
        for i in range(3):
            rect(cr, x + 30 + i * (w - 60) / 3, y + 50, 56, 70, (0.98, 0.90, 0.72))

    def dec_pueblo_rio(cr, t, W, H, dibujar_icono):
        degradado(cr, W, (0.62, 0.52, 0.72), (0.98, 0.80, 0.66))
        rect(cr, 0, 900, W, PISO - 900, (0.52, 0.66, 0.46))
        fabrica(cr, 40, 700, 340, 200, (0.74, 0.38, 0.32), t)
        fabrica(cr, 700, 700, 340, 200, (0.90, 0.86, 0.80), t + 1.3)
        cr.new_path()                                                       # río
        cr.move_to(470, 640)
        cr.curve_to(520, 800, 420, 980, 430, PISO)
        cr.line_to(650, PISO)
        cr.curve_to(640, 980, 600, 800, 560, 640)
        cr.close_path()
        m.rellenar(cr, (0.56, 0.62, 0.86))
        for k in range(5):
            y = 700 + ((t * 40 + k * 110) % 520)
            linea(cr, 500, y, 560, y + 6, 6, (1, 1, 1), 0.5)
    pj.DECORADOS_EXTRA["pueblo_rio"] = dec_pueblo_rio

    def lapida(cr, x, y):
        cr.new_path()
        cr.arc(x, y - 150, 74, math.pi, 2 * math.pi)
        cr.line_to(x + 74, y)
        cr.line_to(x - 74, y)
        cr.close_path()
        m.rellenar(cr, (0.74, 0.74, 0.80))
        rect(cr, x - 100, y - 12, 200, 24, (0.60, 0.60, 0.68))
        linea(cr, x - 34, y - 150, x + 34, y - 150, 8, (0.52, 0.52, 0.60))
        linea(cr, x - 34, y - 112, x + 34, y - 112, 8, (0.52, 0.52, 0.60))

    def dec_cementerio(cr, t, W, H, dibujar_icono):
        degradado(cr, W, (0.26, 0.18, 0.36), (0.80, 0.52, 0.56))
        circ(cr, 540, 560, 64, (1.0, 0.94, 0.86), 0.9)
        circ(cr, 540, 1560, 760, (0.26, 0.40, 0.32))
        rect(cr, 0, 1120, W, PISO - 1120, (0.26, 0.40, 0.32))
        rect(cr, 524, 760, 32, 300, (0.30, 0.22, 0.20))                    # árbol
        circ(cr, 540, 720, 120, (0.20, 0.34, 0.28))
        circ(cr, 470, 780, 80, (0.20, 0.34, 0.28))
        circ(cr, 610, 780, 80, (0.20, 0.34, 0.28))
        lapida(cr, 170, 1150)
        lapida(cr, 910, 1150)
        for k in range(12):
            x = 300 + k * 44
            rect(cr, x, 1130, 8, 50, (0.20, 0.18, 0.24))
        rect(cr, 296, 1146, 492, 8, (0.20, 0.18, 0.24))
    pj.DECORADOS_EXTRA["cementerio"] = dec_cementerio

    def dec_casa(cr, t, W, H, dibujar_icono):
        rect(cr, 0, 0, W, PISO, (0.92, 0.85, 0.77))
        rect(cr, 0, 1080, W, PISO - 1080, (0.66, 0.48, 0.34))
        rect(cr, 0, 1060, W, 22, (0.80, 0.72, 0.64))
        rr(cr, 620, 470, 360, 330, 10, (0.98, 0.97, 0.95))                 # ventana
        rect(cr, 640, 490, 320, 290, (0.98, 0.80, 0.66))
        rect(cr, 792, 490, 14, 290, (0.98, 0.97, 0.95))
        rect(cr, 640, 628, 320, 14, (0.98, 0.97, 0.95))
        for x in (600, 960):
            rect(cr, x, 450, 50, 380, (0.80, 0.36, 0.38))
        rr(cr, 110, 500, 200, 150, 8, MADERA)                              # cuadro
        rect(cr, 126, 516, 168, 118, (0.86, 0.92, 0.84))
        circ(cr, 250, 560, 22, (0.98, 0.80, 0.66))
    pj.DECORADOS_EXTRA["casa"] = dec_casa

    def pared(cr, t, W, hollin):
        rect(cr, 0, 0, W, PISO, (0.88, 0.82, 0.72))
        for fy in range(6):                                                # motivo del papel
            for fx in range(8):
                x = 70 + fx * 140 + (70 if fy % 2 else 0)
                y = 430 + fy * 120
                cr.new_path()
                cr.move_to(x, y - 26)
                cr.line_to(x + 20, y)
                cr.line_to(x, y + 26)
                cr.line_to(x - 20, y)
                cr.close_path()
                m.rellenar(cr, (0.76, 0.62, 0.52), 0.55)
        rect(cr, 0, 1090, W, PISO - 1090, (0.58, 0.42, 0.30))
        rect(cr, 0, 1070, W, 22, (0.72, 0.62, 0.52))
        if hollin > 0:
            rnd = random.Random(21)
            for _ in range(26):
                x, y, r = rnd.uniform(0, W), rnd.uniform(400, 1040), rnd.uniform(50, 130)
                circ(cr, x, y, r, (0.12, 0.10, 0.10), 0.20 * hollin)

    pj.DECORADOS_EXTRA["pared"] = lambda cr, t, W, H, d: pared(cr, t, W, m.clamp(0.25 + t / 3.5))
    pj.DECORADOS_EXTRA["pared_limpia"] = lambda cr, t, W, H, d: pared(cr, t, W, 0.0)

    def dec_basurero(cr, t, W, H, dibujar_icono):
        degradado(cr, W, (0.56, 0.52, 0.64), (0.86, 0.78, 0.76))
        rnd = random.Random(8)
        for (cx, cy, r, c) in ((180, 1240, 420, (0.46, 0.40, 0.36)), (760, 1280, 520, (0.54, 0.47, 0.40)),
                               (480, 1330, 420, (0.40, 0.35, 0.33))):
            circ(cr, cx, cy, r, c)
            for _ in range(46):
                a = rnd.uniform(math.pi * 1.1, math.pi * 1.9)
                d = rnd.uniform(0.35, 0.97) * r
                x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
                if y < PISO - 10:
                    rr(cr, x, y, rnd.uniform(16, 44), rnd.uniform(12, 30), 5,
                       rnd.choice([(0.86, 0.30, 0.32), (0.93, 0.90, 0.84), (0.30, 0.56, 0.42), (0.62, 0.42, 0.78),
                                   (0.20, 0.19, 0.24)]), 0.9)
        for k in range(4):                                                 # gaviotas
            x = (k * 300 + t * 50) % (W + 200) - 100
            y = 470 + 40 * math.sin(t * 2 + k)
            linea(cr, x - 22, y - 8, x, y + 6, 6, (0.2, 0.18, 0.24))
            linea(cr, x, y + 6, x + 22, y - 8, 6, (0.2, 0.18, 0.24))
    pj.DECORADOS_EXTRA["basurero"] = dec_basurero

    # ================================================================ personajes y objetos
    E = pj.ESTILOS
    E["ferruccio"] = {"ropa": (0.46, 0.34, 0.26), "pantalon": (0.30, 0.22, 0.18), "pelo": (0.16, 0.11, 0.08),
                      "peinado": "corto", "corbata": (0.92, 0.38, 0.16)}
    E["enzo"] = {"ropa": (0.12, 0.12, 0.16), "pantalon": (0.10, 0.10, 0.13), "pelo": (0.86, 0.86, 0.88),
                 "peinado": "corto", "anteojos": True, "corbata": ROJO_T}
    E["pietro"] = {"ropa": (0.97, 0.97, 0.97), "pantalon": (0.30, 0.28, 0.32), "pelo": (0.20, 0.14, 0.10),
                   "peinado": "corto", "bigote": True}
    E["michele"] = {"ropa": (0.26, 0.28, 0.40), "pantalon": (0.18, 0.19, 0.28), "pelo": (0.18, 0.12, 0.08),
                    "peinado": "corto", "corbata": ROJO_T}
    E["adi"] = {"ropa": (0.90, 0.88, 0.84), "pantalon": (0.26, 0.26, 0.32), "pelo": (0.60, 0.46, 0.30),
                "peinado": "corto"}
    E["rudolf"] = {"ropa": (0.20, 0.20, 0.26), "pantalon": (0.14, 0.14, 0.18), "pelo": (0.14, 0.10, 0.08),
                   "peinado": "corto", "bigote": True, "corbata": (0.50, 0.50, 0.56)}
    E["dyson"] = {"ropa": (0.22, 0.48, 0.46), "pantalon": (0.24, 0.24, 0.30), "pelo": (0.40, 0.28, 0.18),
                  "peinado": "corto", "anteojos": True}
    E["howells"] = {"ropa": (0.30, 0.32, 0.40), "pantalon": (0.18, 0.18, 0.24), "pelo": (0.22, 0.15, 0.10),
                    "peinado": "rapado", "barba": "corta"}
    E["maestra"] = {"ropa": (0.30, 0.60, 0.50), "pantalon": (0.30, 0.60, 0.50), "pelo": (0.30, 0.18, 0.10),
                    "peinado": "largo", "falda": True, "anteojos": True}
    E["nina"] = {"ropa": (0.90, 0.40, 0.50), "pantalon": (0.90, 0.40, 0.50), "pelo": (0.20, 0.13, 0.08),
                 "peinado": "largo", "falda": True}
    E["nino"] = {"ropa": (0.96, 0.60, 0.30), "pantalon": (0.26, 0.28, 0.40), "pelo": (0.50, 0.34, 0.18),
                 "peinado": "corto"}
    E["vecina"] = {"ropa": (0.70, 0.40, 0.56), "pantalon": (0.70, 0.40, 0.56), "pelo": (0.50, 0.30, 0.16),
                   "peinado": "largo", "falda": True}

    def obj_masa(cr, x, y):
        for (dx, dy, r) in ((-14, 0, 26), (12, -4, 30), (0, -22, 22)):
            circ(cr, x + dx, y + dy, r, (0.92, 0.89, 0.80))
    pj.OBJETOS_EXTRA["masa"] = obj_masa
