# -*- coding: utf-8 -*-
"""Arte propio del Short 013 (Adidas dejó ir a Michael Jordan).

Aporta estilos de personaje y tres decorados: «dos_puertas» (gancho), «medidor» (pared con regla
de alturas) y «vitrina» (pedestal iluminado para la zapatilla). Las marcas van siempre como texto
en carteles claros (campo `placas` del JSON), nunca como logotipos.
"""
import math
import random


def registrar(m, pj):
    PISO = pj.PISO

    pj.ESTILOS["jordan"] = dict(pj.ESTILOS["jugador"])
    pj.ESTILOS["pivot1"] = {"ropa": (0.93, 0.93, 0.95), "pantalon": (0.93, 0.93, 0.95), "pelo": (0.22, 0.14, 0.08),
                            "peinado": "corto", "piel": (0.88, 0.70, 0.56)}
    pj.ESTILOS["pivot2"] = {"ropa": (0.14, 0.48, 0.34), "pantalon": (0.14, 0.48, 0.34), "pelo": (0.05, 0.04, 0.04),
                            "peinado": "rapado", "piel": (0.42, 0.28, 0.19)}
    pj.ESTILOS["adidas_ej"] = dict(pj.ESTILOS["ejecutivo"])
    pj.ESTILOS["nike_ej"] = dict(pj.ESTILOS["ejecutivo2"], corbata=(0.85, 0.15, 0.18))

    def rect(cr, x, y, w, h, c, a=1.0):
        cr.new_path()
        cr.rectangle(x, y, w, h)
        m.rellenar(cr, c, a)

    def dec_dos_puertas(cr, t, W, H, dibujar_icono):
        """Pared con dos puertas: la de la izquierda, apagada; la de la derecha, iluminada."""
        rect(cr, 0, 0, W, PISO, (0.87, 0.82, 0.76))
        rect(cr, 0, PISO - 60, W, 60, (0.62, 0.52, 0.46))
        for cx, abierta in ((270, False), (810, True)):
            rect(cr, cx - 150, 640, 300, PISO - 640, (0.45, 0.33, 0.27))          # marco
            if abierta:
                rect(cr, cx - 125, 665, 250, PISO - 665, (1.0, 0.86, 0.70))
                for i in range(5):                                                # rayos de luz
                    cr.new_path()
                    a = -0.5 + i * 0.25 + math.sin(t * 0.8 + i) * 0.03
                    cr.move_to(cx, PISO - 300)
                    cr.line_to(cx + math.sin(a) * 420 - 26, PISO - 300 - math.cos(a) * 420)
                    cr.line_to(cx + math.sin(a) * 420 + 26, PISO - 300 - math.cos(a) * 420)
                    cr.close_path()
                    m.rellenar(cr, (1, 1, 1), 0.10)
            else:
                rect(cr, cx - 125, 665, 250, PISO - 665, (0.30, 0.24, 0.26))
                rect(cr, cx - 125, 665, 250, PISO - 665, (0, 0, 0), 0.25)
                cr.new_path()
                cr.arc(cx + 95, PISO - 280, 12, 0, 2 * math.pi)                    # picaporte
                m.rellenar(cr, (0.75, 0.72, 0.70))
    pj.DECORADOS_EXTRA["dos_puertas"] = dec_dos_puertas

    def dec_medidor(cr, t, W, H, dibujar_icono):
        """Gimnasio con una regla de alturas pintada en la pared (sin números: es una caricatura)."""
        rect(cr, 0, 0, W, PISO, (0.83, 0.77, 0.69))
        rect(cr, 0, PISO - 70, W, 70, (0.72, 0.50, 0.30))
        for i in range(12):
            y = PISO - 70 - i * 62
            largo = W if i % 2 == 0 else W * 0.5
            rect(cr, 60, y, largo - 120, 4, (0.45, 0.36, 0.33), 0.35 if i % 2 else 0.6)
        rect(cr, 60, PISO - 760, 14, 760, (0.45, 0.36, 0.33))
    pj.DECORADOS_EXTRA["medidor"] = dec_medidor

    def dec_vitrina(cr, t, W, H, dibujar_icono):
        """Pedestal con un haz de luz, sobre el fondo del canal."""
        cr.new_path()
        cr.move_to(W / 2 - 70, 380)
        cr.line_to(W / 2 + 70, 380)
        cr.line_to(W / 2 + 430, 1000)
        cr.line_to(W / 2 - 430, 1000)
        cr.close_path()
        m.rellenar(cr, (1, 1, 1), 0.07 + 0.02 * math.sin(t * 2))
        cr.new_path()
        m.rrect(cr, W / 2 - 330, 985, 660, 46, 14)
        m.rellenar(cr, (0.93, 0.90, 0.88))
        rect(cr, W / 2 - 300, 1031, 600, PISO - 1031, (0.78, 0.74, 0.72), 0.0)
        rnd = random.Random(5)
        for _ in range(14):                                                        # destellos
            x, y = rnd.uniform(160, W - 160), rnd.uniform(470, 960)
            k = 0.5 + 0.5 * math.sin(t * 3 + x)
            cr.new_path()
            cr.arc(x, y, 5 * k, 0, 2 * math.pi)
            m.rellenar(cr, (1, 1, 1), 0.5 * k)
    pj.DECORADOS_EXTRA["vitrina"] = dec_vitrina
