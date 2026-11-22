# -*- coding: utf-8 -*-
"""Arte propio del Short 011 (Robert Kearns y el limpiaparabrisas intermitente).

Versión A, «historia con personajes»: cada escena es un tipo propio (`k_...`) con su coreografía
atada a la locución. Los textos que se ven en pantalla llegan desde el JSON (con un valor por
defecto acá), así se corrigen sin tocar el código.

Qué aporta este archivo:
  · estilos: kearns (joven), kearns_mayor (canoso), kearns_boda, novia, juez_k, ford1, ford2, abog1-3
  · peinados propios (kearns, kearns_mayor), moño y velo, enganchados sin tocar personajes.py
  · poses, objetos en la mano, decorados dibujados para esta historia y once tipos de escena
"""
import math
import random

import cairo

M = None    # módulo motion
PJ = None   # módulo personajes
E = {}      # posiciones de pantalla del último personaje dibujado (ojo, cabeza, mano, boca de la botella)
W, H, PISO = 1080, 1920, 1240

PIEL = (0.96, 0.80, 0.68)
CREMA = (0.93, 0.90, 0.84)
TINTA = (0.10, 0.09, 0.13)
ROJO_K = (0.84, 0.12, 0.18)        # corbata de Kearns y rojo de los carteles
VERDE_OSC = (0.08, 0.50, 0.29)
PELO_K = (0.17, 0.11, 0.08)
PELO_GRIS = (0.80, 0.80, 0.84)
MADERA = (0.55, 0.36, 0.22)
AUTO_KEARNS = (0.78, 0.15, 0.20)
AUTO_FORD = (0.93, 0.91, 0.94)
AUTO_CHRYSLER = (0.62, 0.63, 0.70)


# ------------------------------------------------------------------ utilidades de dibujo

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _sombra(c, f=0.75):
    return tuple(v * f for v in c)


def rect(cr, x, y, w, h, c, a=1.0):
    cr.new_path()
    cr.rectangle(x, y, w, h)
    cr.set_source_rgba(c[0], c[1], c[2], a)
    cr.fill()


def rr(cr, x, y, w, h, r, c, a=1.0):
    cr.new_path()
    M.rrect(cr, x, y, w, h, r)
    cr.set_source_rgba(c[0], c[1], c[2], a)
    cr.fill()


def circ(cr, x, y, r, c, a=1.0):
    if r <= 0.01:
        return
    cr.new_path()
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_source_rgba(c[0], c[1], c[2], a)
    cr.fill()


def poli(cr, pts, c, a=1.0):
    cr.new_path()
    cr.move_to(*pts[0])
    for q in pts[1:]:
        cr.line_to(*q)
    cr.close_path()
    cr.set_source_rgba(c[0], c[1], c[2], a)
    cr.fill()


def linea(cr, pts, ancho, c, a=1.0):
    cr.new_path()
    cr.set_line_width(ancho)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.move_to(*pts[0])
    for q in pts[1:]:
        cr.line_to(*q)
    cr.set_source_rgba(c[0], c[1], c[2], a)
    cr.stroke()


def degradado(cr, x, y, w, h, c0, c1):
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(1, *c1)
    cr.new_path()
    cr.rectangle(x, y, w, h)
    cr.set_source(g)
    cr.fill()


def halo(cr, x, y, r, c, a):
    g = cairo.RadialGradient(x, y, r * 0.05, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    cr.new_path()
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_source(g)
    cr.fill()


def texto_derecho(cr, s, x, y, tam, color, alfa=1.0):
    """Texto dentro de un objeto de personaje: lo endereza si el personaje está espejado."""
    cr.save()
    cr.translate(x, y)
    if cr.get_matrix().xx < 0:
        cr.scale(-1, 1)
    M.texto(cr, s, 0, 0, tam, color, alfa=alfa)
    cr.restore()


def aqui(cr, clave):
    """Posición capturada (en pantalla) convertida a las coordenadas actuales del dibujo."""
    return cr.device_to_user(*E[clave])


def camara(cr, t, zmax=0.05):
    """Acercamiento lento con un leve paneo, anclado en el piso (igual que las escenas «historia»)."""
    z = 1 + min(zmax, 0.012 * max(0.0, t))
    cr.translate(W / 2 + math.sin(t * 0.4) * 6, PISO)
    cr.scale(z, z)
    cr.translate(-W / 2, -PISO)


def banda(cr):
    """Franja oscura del subtítulo: tapa todo lo que quede por debajo del piso."""
    rect(cr, 0, PISO, W, H - PISO, (0.06, 0.07, 0.10))
    rect(cr, 0, PISO, W, 10, (0.20, 0.20, 0.26))


def titulo(cr, p, t, fijo=False):
    """Cartel de la marca. `titulo`: texto fijo; `titulos`: [[segundo, texto], ...] para cambiarlo."""
    lista = p.get("titulos") or [[0, p.get("titulo", "")]]
    s, t0 = "", 0.0
    for ti, txt in lista:
        if t >= ti:
            s, t0 = txt, ti
    if s:
        M.titular(cr, s, 1.0 if fijo else t - t0, y=325 if "\n" in s else 300)


def persona(cr, estilo, x, pose, t, mira=1, esc=0.95, objeto=None, y=None):
    PJ.personaje(cr, estilo, x, PISO if y is None else y, esc, mira, pose, t, objeto)


def sello(cr, s, x, y, t, color, tam=100, ang=-0.16):
    """Sello inclinado que cae de golpe, con fondo oscuro para que se lea sobre cualquier decorado."""
    if t < 0:
        return
    a = clamp(t / 0.18)
    esc = 2.2 - 1.2 * M.ease_out_cubic(a)
    lineas = s.split("\n")
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    w = max(M.ancho_texto(cr, l, tam) for l in lineas) + tam * 0.75
    h = tam * 1.12 * len(lineas) + tam * 0.5
    rr(cr, -w / 2, -h / 2, w, h, 18, (0.10, 0.04, 0.10), 0.86 * a)
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, 18)
    cr.set_line_width(tam * 0.13)
    cr.set_source_rgba(color[0], color[1], color[2], a)
    cr.stroke()
    for i, l in enumerate(lineas):
        M.texto(cr, l, 0, -h / 2 + tam * 0.25 + tam * 1.12 * (i + 0.5), tam, color, alfa=a)
    cr.restore()


def etiqueta(cr, s, x, y, t, tam=48, fondo=None, color=None, punta=0, punta_dx=0):
    """Cartelito redondeado centrado en (x, y). punta: 1 hacia abajo, -1 hacia arriba, 0 sin punta;
    punta_dx la corre hacia un costado."""
    k = M.ease_out_back(t / 0.3)
    if k <= 0.01:
        return
    fondo = fondo or M.BLANCO
    color = color or TINTA
    w = M.ancho_texto(cr, s, tam) + tam * 1.1
    h = tam * 1.55
    cr.save()
    cr.translate(x, y)
    cr.scale(k, k)
    rr(cr, -w / 2, -h / 2, w, h, h / 2, fondo)
    if punta:
        poli(cr, [(punta_dx - 18, punta * (h / 2 - 2)), (punta_dx + 18, punta * (h / 2 - 2)),
                  (punta_dx, punta * (h / 2 + 26))], fondo)
    M.texto(cr, s, 0, 0, tam, color)
    cr.restore()


def estrella(cr, x, y, r, color, n=9, giro=0.0, a=1.0, dentro=0.48):
    if r <= 0.5:
        return
    cr.new_path()
    for i in range(n * 2):
        ang = giro + i * math.pi / n
        rad = r if i % 2 == 0 else r * dentro
        px, py = x + math.cos(ang) * rad, y + math.sin(ang) * rad
        cr.line_to(px, py) if i else cr.move_to(px, py)
    cr.close_path()
    cr.set_source_rgba(color[0], color[1], color[2], a)
    cr.fill()


def billete(cr, x, y, ang, esc, a=1.0):
    if a <= 0.02:
        return
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    rr(cr, -46, -24, 92, 48, 7, (0.16, 0.56, 0.34), a)
    cr.new_path()
    M.rrect(cr, -38, -16, 76, 32, 5)
    cr.set_line_width(3)
    cr.set_source_rgba(0.70, 0.94, 0.76, a)
    cr.stroke()
    M.texto(cr, "$", 0, 0, 30, (0.82, 1.0, 0.86), alfa=a)
    cr.restore()


def lluvia_billetes(cr, tau, n, semilla, y0=440, y1=PISO + 30, x0=50, x1=W - 50, desde=None):
    """Billetes que caen. Sin `desde` es un ciclo continuo; con `desde`, una tanda que arranca ahí."""
    rnd = random.Random(semilla)
    alto = y1 - y0
    for i in range(n):
        x = rnd.uniform(x0, x1)
        f = rnd.uniform(0, 1)
        v = rnd.uniform(110, 190)
        giro = rnd.uniform(-1, 1)
        e = rnd.uniform(0.8, 1.1)
        if desde is None:
            y = y0 + (f * alto + tau * v) % alto
        else:
            d = tau - desde - f * 1.1
            if d < 0:
                continue
            y = y0 - 30 + d * v * 3.0
            if y > y1:
                continue
        a = clamp((y - y0) / 70) * clamp((y1 - y) / 50)
        billete(cr, x + 26 * math.sin(tau * 1.7 + i), y, giro * 0.5 + 0.45 * math.sin(tau * 2.2 + i * 1.3), e, a)


def lluvia(cr, t, n=80, a=0.30, semilla=5, y0=380):
    rnd = random.Random(semilla)
    cr.set_line_width(4)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        x0 = rnd.uniform(-60, W + 220)
        f = rnd.uniform(0, 900)
        v = rnd.uniform(900, 1300)
        l = rnd.uniform(26, 50)
        y = y0 + (f + t * v) % (PISO - y0 + 20)
        if y > PISO - 4:
            continue
        x = x0 - (y - y0) * 0.18
        cr.new_path()
        cr.move_to(x, y)
        cr.line_to(x + 0.18 * l, y - l)
        cr.set_source_rgba(1, 1, 1, a)
        cr.stroke()


# ------------------------------------------------------------------ personajes: pelo, moño y velo

def _pelo_extra(cr, est, hx, hy, r):
    """Se dibuja después del peinado original y antes de la cara. Además anota dónde quedaron el
    ojo y la cabeza en pantalla, para que la escena pueda apuntarles (corcho, estrella, globos)."""
    tipo = est.get("peinado")
    pelo = est["pelo"]
    if tipo == "kearns":
        # casquete alto (deja la frente libre), jopo hacia adelante y patilla
        cr.new_path()
        cr.move_to(hx - 68, hy - 4)
        cr.curve_to(hx - 82, hy - 60, hx - 42, hy - 94, hx + 4, hy - 88)
        cr.curve_to(hx + 42, hy - 96, hx + 72, hy - 74, hx + 60, hy - 46)
        cr.curve_to(hx + 42, hy - 60, hx + 8, hy - 58, hx - 22, hy - 42)
        cr.line_to(hx - 38, hy - 36)
        cr.line_to(hx - 40, hy + 4)
        cr.line_to(hx - 55, hy + 4)
        cr.close_path()
        cr.set_source_rgb(*pelo)
        cr.fill()
        cr.new_path()   # brillo del jopo
        cr.move_to(hx - 6, hy - 76)
        cr.curve_to(hx + 18, hy - 84, hx + 40, hy - 78, hx + 50, hy - 64)
        cr.set_line_width(5)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(1, 1, 1, 0.16)
        cr.stroke()
    elif tipo == "kearns_mayor":
        # mismo corte, pero canoso y con entradas
        cr.new_path()
        cr.move_to(hx - 68, hy - 4)
        cr.curve_to(hx - 82, hy - 58, hx - 46, hy - 86, hx - 6, hy - 80)
        cr.curve_to(hx + 14, hy - 82, hx + 32, hy - 74, hx + 36, hy - 62)
        cr.curve_to(hx + 14, hy - 64, hx - 8, hy - 56, hx - 22, hy - 40)
        cr.line_to(hx - 38, hy - 36)
        cr.line_to(hx - 40, hy + 4)
        cr.line_to(hx - 55, hy + 4)
        cr.close_path()
        cr.set_source_rgb(*pelo)
        cr.fill()
        for dy in (-42, -52):
            linea(cr, [(hx + 26, hy + dy), (hx + 52, hy + dy + 3)], 3, _sombra(est.get("piel", PIEL), 0.82), 0.8)
    if est.get("velo"):
        cr.new_path()
        cr.move_to(hx - 6, hy - r - 10)
        cr.curve_to(hx - r - 40, hy - r, hx - r - 70, hy + 90, hx - r - 62, hy + 190)
        cr.line_to(hx - r + 26, hy + 190)
        cr.curve_to(hx - r + 10, hy + 60, hx - 30, hy - 30, hx + 8, hy - r + 6)
        cr.close_path()
        cr.set_source_rgba(1, 1, 1, 0.80)
        cr.fill()
        rr(cr, hx - 34, hy - r - 10, 62, 14, 7, (1, 1, 1))
        for dx in (-22, -3, 16):
            circ(cr, hx + dx, hy - r - 12, 7, (1, 0.93, 0.95))
    if est.get("mono"):
        mx, my = hx + 12, hy + r + 20
        poli(cr, [(mx, my), (mx - 30, my - 17), (mx - 30, my + 17)], ROJO_K)
        poli(cr, [(mx, my), (mx + 30, my - 17), (mx + 30, my + 17)], ROJO_K)
        circ(cr, mx, my, 8, _sombra(ROJO_K, 0.75))
    E["ojo"] = cr.user_to_device(hx + 40, hy - 8)
    E["cabeza"] = cr.user_to_device(hx, hy)
    cr.new_path()


def _instalar_pelo():
    """Suma peinados sin modificar personajes.py: envuelve la función que dibuja pelo y sombrero."""
    if getattr(PJ, "_k_pelo_instalado", False):
        return
    original = PJ._peinado_y_sombrero

    def con_extras(cr, est, hx, hy, r):
        original(cr, est, hx, hy, r)
        _pelo_extra(cr, est, hx, hy, r)

    PJ._peinado_y_sombrero = con_extras
    PJ._k_pelo_instalado = True


def _estilos():
    kearns = {"ropa": CREMA, "pantalon": (0.24, 0.21, 0.28), "pelo": PELO_K, "peinado": "kearns",
              "anteojos": True, "corbata": ROJO_K}
    PJ.ESTILOS["kearns"] = kearns
    PJ.ESTILOS["kearns_mayor"] = dict(kearns, pelo=PELO_GRIS, peinado="kearns_mayor")
    PJ.ESTILOS["kearns_boda"] = dict(kearns, ropa=(0.11, 0.11, 0.15), pantalon=(0.09, 0.09, 0.12),
                                     corbata=(0.96, 0.96, 0.98), mono=True)
    PJ.ESTILOS["novia"] = {"ropa": (0.97, 0.96, 0.98), "pantalon": (0.93, 0.76, 0.64), "pelo": (0.50, 0.28, 0.14),
                           "peinado": "largo", "falda": True, "velo": True}
    PJ.ESTILOS["juez_k"] = {"ropa": (0.08, 0.08, 0.10), "pantalon": (0.08, 0.08, 0.10), "pelo": (0.93, 0.93, 0.95),
                            "peinado": "calvo", "falda": True, "bigote": True}
    PJ.ESTILOS["ford1"] = {"ropa": (0.15, 0.16, 0.21), "pantalon": (0.11, 0.12, 0.16), "pelo": (0.62, 0.62, 0.66),
                           "peinado": "corto", "corbata": (0.50, 0.52, 0.60)}
    PJ.ESTILOS["ford2"] = {"ropa": (0.34, 0.22, 0.25), "pantalon": (0.22, 0.15, 0.17), "pelo": (0.20, 0.13, 0.09),
                           "peinado": "calvo", "bigote": True, "corbata": (0.86, 0.83, 0.80)}
    PJ.ESTILOS["abog1"] = {"ropa": (0.22, 0.17, 0.30), "pantalon": (0.15, 0.12, 0.20), "pelo": (0.28, 0.17, 0.10),
                           "peinado": "corto", "corbata": (0.78, 0.78, 0.84)}
    PJ.ESTILOS["abog2"] = {"ropa": (0.14, 0.15, 0.20), "pantalon": (0.10, 0.11, 0.15), "pelo": (0.70, 0.70, 0.73),
                           "peinado": "calvo", "bigote": True, "corbata": (0.55, 0.20, 0.26)}
    PJ.ESTILOS["abog3"] = {"ropa": (0.30, 0.24, 0.22), "pantalon": (0.20, 0.16, 0.15), "pelo": (0.10, 0.08, 0.07),
                           "peinado": "corto", "corbata": (0.80, 0.80, 0.85), "piel": (0.80, 0.60, 0.45)}


def _poses():
    P = PJ.POSES_EXTRA
    P["k_clase"] = lambda t: {"brazoD": (116 + 4 * math.sin(t * 3), 8), "brazoT": (-8, 22), "boca": "hablar",
                              "cejas": 0.3, "cabeza": 2 * math.sin(t * 4)}
    P["k_botella"] = lambda t: {"brazoD": (62 + 4 * math.sin(t * 17), 38), "brazoT": (-10, 20), "boca": "sonrisa",
                                "cejas": 0.3, "temblor": math.sin(t * 34) * 2.2}
    P["k_botella_mira"] = lambda t: {"brazoD": (62, 38), "brazoT": (-10, 20), "boca": "o", "cejas": 1,
                                     "cabeza": -15}
    P["k_ojo"] = lambda t: {"brazoD": (152, 116), "brazoT": (-24, 36), "cabeza": 12, "torso": 7, "boca": "o",
                            "cejas": -1, "temblor": math.sin(t * 24) * 3}
    P["k_cruzar"] = lambda t: {"brazoD": (26, -112), "brazoT": (-18, 106), "boca": "triste", "cejas": -0.7,
                               "cabeza": -2}
    P["k_negar"] = lambda t: {"brazoD": (62, 62), "brazoT": (-8, 20), "boca": "triste", "cejas": -0.6,
                              "cabeza": 6 * math.sin(t * 13)}
    P["k_trabajar"] = lambda t: {"brazoD": (50 + 7 * math.sin(t * 11), 60 + 9 * math.sin(t * 11 + 1)),
                                 "brazoT": (-6, 30), "cabeza": 10, "torso": 5, "boca": "neutra", "cejas": 0.6}
    P["k_trofeo"] = lambda t: {"brazoD": (130, 40), "brazoT": (-130, -40), "boca": "sonrisa", "cejas": 0.5,
                               "salto": abs(math.sin(t * 5)) * 12}
    P["k_trofeo_salta"] = lambda t: {"brazoD": (130, 40), "brazoT": (-130, -40), "boca": "sonrisa", "cejas": 0.9,
                                     "salto": abs(math.sin(t * 7)) * 34}
    P["k_festejo"] = lambda t: {"brazoD": (125 + 8 * math.sin(t * 8), 50), "brazoT": (-125 - 8 * math.sin(t * 8), -50),
                                "boca": "sonrisa", "cejas": 0.6, "salto": abs(math.sin(t * 6)) * 24}
    P["k_patente"] = lambda t: {"brazoD": (125, 50), "brazoT": (-125, -50), "boca": "hablar", "cejas": -0.6,
                                "cabeza": -3}
    P["k_paraguas"] = lambda t: {"brazoD": (30, 120), "brazoT": (-8, 20), "boca": "neutra", "cejas": 0.2}
    P["k_paraguas_o"] = lambda t: {"brazoD": (30, 120), "brazoT": (-20, 40), "boca": "o", "cejas": 1,
                                   "cabeza": -6, "temblor": math.sin(t * 22) * 1.5}
    P["k_alegato"] = lambda t: {"brazoD": (104 + 14 * math.sin(t * 6), 34 + 10 * math.sin(t * 4)),
                                "brazoT": (-14, 30), "boca": "hablar", "cejas": 0.4,
                                "cabeza": -4 + 2 * math.sin(t * 4)}
    P["k_volante"] = lambda t: {"brazoD": (70, 40), "brazoT": (-10, 20), "boca": "neutra", "cejas": 0.2}
    P["k_volante_idea"] = lambda t: {"brazoD": (70, 40), "brazoT": (-10, 20), "boca": "o", "cejas": 1,
                                     "cabeza": -5}

    def mazo(t):
        # t < 0: mazo en alto; t >= 0: baja de golpe y rebota apenas
        if t < 0:
            k = 0.0
        else:
            k = M.ease_out_cubic(t / 0.10) - 0.10 * math.sin(clamp(t / 0.35) * math.pi)
        return {"brazoD": (150 - 82 * k, 14), "brazoT": (-8, 20), "boca": "neutra", "cejas": -0.5}
    P["k_mazo"] = mazo


def _objetos():
    O = PJ.OBJETOS_EXTRA

    def nada(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)

    def botella(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        cr.save()
        cr.translate(x, y + 26)
        cr.rotate(0.16)
        rr(cr, -22, -92, 44, 104, 10, (0.09, 0.30, 0.20))
        poli(cr, [(-22, -84), (22, -84), (9, -122), (-9, -122)], (0.09, 0.30, 0.20))
        rect(cr, -9, -150, 18, 30, (0.09, 0.30, 0.20))
        rect(cr, -10, -152, 20, 22, (0.96, 0.78, 0.56))
        rr(cr, -19, -62, 38, 40, 4, (0.97, 0.94, 0.88))
        rect(cr, -19, -50, 38, 8, ROJO_K)
        if E.get("corcho_puesto", True):
            rr(cr, -9, -168, 18, 20, 5, (0.80, 0.60, 0.40))
        E["boca_botella"] = cr.user_to_device(0, -160)
        cr.restore()

    def copa(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        linea(cr, [(x + 4, y - 4), (x + 4, y - 48)], 5, (0.95, 0.95, 1.0), 0.9)
        poli(cr, [(x - 18, y - 96), (x + 26, y - 96), (x + 12, y - 46), (x - 4, y - 46)], (0.98, 0.90, 0.72), 0.9)
        linea(cr, [(x - 18, y - 96), (x - 4, y - 46), (x + 12, y - 46), (x + 26, y - 96)], 4, (1, 1, 1), 0.9)

    def puntero(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        linea(cr, [(x - 12, y + 9), (x + 196, y - 140)], 8, (0.36, 0.22, 0.12))
        circ(cr, x + 196, y - 140, 8, (0.95, 0.95, 0.9))

    def destornillador(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        linea(cr, [(x - 6, y - 10), (x + 22, y + 20)], 16, ROJO_K)
        linea(cr, [(x + 22, y + 20), (x + 56, y + 54)], 6, (0.75, 0.76, 0.80))

    def paraguas(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        cr.save()
        cr.translate(x, y)
        cr.rotate(-0.14)
        linea(cr, [(0, 26), (0, -300)], 9, (0.20, 0.18, 0.22))
        cr.new_path()
        cr.arc(-12, 30, 12, 0, math.pi)
        cr.set_line_width(9)
        cr.set_source_rgb(0.20, 0.18, 0.22)
        cr.stroke()
        R = 215
        cr.new_path()
        cr.arc(0, -262, R, math.pi, 2 * math.pi)
        cr.close_path()
        cr.set_source_rgb(*ROJO_K)
        cr.fill()
        for i in range(4):   # ondas del borde
            circ(cr, -R + (i + 0.5) * (R / 2), -262, R / 4, _sombra(ROJO_K, 0.62))
        for i in (-1, 0, 1):
            linea(cr, [(0, -262 - R + 4), (i * R * 0.5, -262)], 3, _sombra(ROJO_K, 0.7))
        circ(cr, 0, -262 - R, 9, (0.20, 0.18, 0.22))
        cr.restore()

    def papeles(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        for i, g in enumerate((0.20, 0.06, -0.08)):
            cr.save()
            cr.translate(x + 10, y - 34)
            cr.rotate(g)
            rect(cr, -34, -46, 68, 92, (0.97, 0.95, 0.90) if i else (0.86, 0.84, 0.80))
            if i == 2:
                for j in range(5):
                    rect(cr, -24, -32 + j * 15, 48 if j % 2 else 38, 5, (0.55, 0.55, 0.60))
            cr.restore()

    def mazo(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        linea(cr, [(x - 14, y - 4), (x + 86, y + 6)], 13, (0.62, 0.42, 0.24))
        rr(cr, x + 72, y - 36, 44, 84, 10, (0.45, 0.28, 0.15))
        rect(cr, x + 72, y - 4, 44, 16, M.DORADO)
        E["mazo"] = cr.user_to_device(x + 94, y + 48)

    def escobilla(cr, x, y):
        # la escobilla del limpiaparabrisas, alzada como trofeo por encima de la cabeza
        E["mano"] = cr.user_to_device(x, y)
        linea(cr, [(x - 250, y - 36), (x + 28, y - 36)], 10, (0.72, 0.73, 0.78))
        linea(cr, [(x - 262, y - 52), (x + 40, y - 52)], 16, TINTA)
        for dx in (-206, -111, -16):
            linea(cr, [(x + dx, y - 36), (x + dx, y - 52)], 7, (0.72, 0.73, 0.78))
        circ(cr, x - 111, y - 32, 12, (0.55, 0.56, 0.62))

    def cheque(cr, x, y):
        E["mano"] = cr.user_to_device(x, y)
        cr.save()
        cr.translate(x + 30, y - 22)
        cr.rotate(-0.10)
        rr(cr, -52, -30, 104, 60, 6, (0.93, 0.98, 0.93))
        rect(cr, -40, -16, 46, 7, (0.55, 0.60, 0.58))
        rect(cr, -40, 4, 80, 9, VERDE_OSC)
        cr.restore()

    O.update({"nada": nada, "botella": botella, "copa": copa, "puntero": puntero,
              "destornillador": destornillador, "paraguas": paraguas, "papeles": papeles, "mazo": mazo,
              "escobilla": escobilla, "cheque": cheque})


# ------------------------------------------------------------------ el parabrisas y sus escobillas

AB, AT, HV = 260.0, 218.0, 230.0             # semiancho inferior, semiancho superior y alto del vidrio
PIVOTES = ((-70.0, -4.0), (130.0, -4.0))     # ejes de las dos escobillas
LARGO = 172.0
ANG0, ANG1 = 168.0, 62.0                     # ángulo en reposo y al final del barrido (grados)
_GOTAS = []


def barrido(t, pasadas):
    """Estado de las escobillas en el segundo t. `pasadas` = [(inicio, duración de la ida), ...].
    Devuelve u (0 = en reposo, 1 = barrido completo) y edad(f): segundos desde la última vez que la
    goma pasó por la fracción f del recorrido (para que las gotas vuelvan a aparecer de a poco)."""
    u = 0.0
    for T, s in pasadas:
        d = t - T
        if 0 <= d < s:
            u = 0.5 - 0.5 * math.cos(math.pi * d / s)
        elif s <= d < 2 * s:
            u = 0.5 - 0.5 * math.cos(math.pi * (2 * s - d) / s)

    def edad(f):
        x = math.acos(1 - 2 * clamp(f)) / math.pi
        mejor = 99.0
        for T, s in pasadas:
            for tp in (T + x * s, T + 2 * s - x * s):
                if tp <= t:
                    mejor = min(mejor, t - tp)
        return mejor
    return u, edad


def ciclo(periodo, s, desfase=0.0, n=40):
    """Pasadas periódicas: una cada `periodo` segundos (la ida dura s; la vuelta, otro tanto)."""
    return [(desfase + k * periodo, s) for k in range(-3, n)]


def _semiancho(y):
    return AB - (AB - AT) * (-y / HV)


def _gotas():
    if not _GOTAS:
        rnd = random.Random(11)
        while len(_GOTAS) < 64:
            x, y = rnd.uniform(-AB, AB), rnd.uniform(-HV + 14, -12)
            if abs(x) > _semiancho(y) - 16:
                continue
            fs = []
            for px, py in PIVOTES:
                dx, dy = x - px, -(y - py)
                d, ang = math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))
                if 20 <= d <= LARGO + 8 and ANG1 <= ang <= ANG0:
                    fs.append((ANG0 - ang) / (ANG0 - ANG1))
            _GOTAS.append((x, y, rnd.uniform(5.5, 10.5), fs, rnd.uniform(0, 1)))
    return _GOTAS


def vidrio_path(cr, r=26):
    cr.new_path()
    cr.move_to(-AB + r, 0)
    cr.line_to(AB - r, 0)
    cr.curve_to(AB, 0, AB, 0, AB - 5, -r)
    cr.line_to(AT + 5, -HV + r)
    cr.curve_to(AT, -HV, AT, -HV, AT - r, -HV)
    cr.line_to(-AT + r, -HV)
    cr.curve_to(-AT, -HV, -AT, -HV, -AT - 5, -HV + r)
    cr.line_to(-AB + 5, -r)
    cr.curve_to(-AB, 0, -AB, 0, -AB + r, 0)
    cr.close_path()


def parabrisas(cr, u, edad, gotas=True, conductor=None, crece=0.9, interior=True):
    """Vidrio con gotas y dos escobillas. Origen: centro del borde inferior; 520 px de ancho."""
    vidrio_path(cr)
    g = cairo.LinearGradient(0, -HV, 0, 0)
    g.add_color_stop_rgb(0, 0.77, 0.72, 0.81)
    g.add_color_stop_rgb(1, 0.56, 0.50, 0.63)
    cr.set_source(g)
    cr.fill()
    cr.save()
    vidrio_path(cr)
    cr.clip()
    if interior:   # respaldos de los asientos
        for sx in (-1, 1):
            rr(cr, sx * 120 - 78, -112, 156, 150, 30, (0.32, 0.25, 0.35), 0.75)
    if conductor:
        conductor(cr)
        vidrio_path(cr)
        cr.set_source_rgba(0.88, 0.82, 0.93, 0.16)
        cr.fill()
    poli(cr, [(-150, -HV), (-86, -HV), (-190, 0), (-254, 0)], (1, 1, 1), 0.11)
    poli(cr, [(-56, -HV), (-30, -HV), (-134, 0), (-160, 0)], (1, 1, 1), 0.08)
    if gotas:
        for x, y, rad, fs, az in _gotas():
            a = 1.0
            for f in fs:
                a = min(a, clamp((edad(f) - az * 0.25) / crece))
            if a > 0.03:
                circ(cr, x, y, rad * (0.55 + 0.45 * a), (1, 1, 1), 0.82 * a)
                circ(cr, x + rad * 0.25, y + rad * 0.3, rad * 0.4, (0.66, 0.60, 0.76), 0.5 * a)
    cr.restore()
    ang = math.radians(ANG0 + (ANG1 - ANG0) * u)
    for px, py in PIVOTES:
        ex, ey = px + LARGO * math.cos(ang), py - LARGO * math.sin(ang)
        bx, by = px + 30 * math.cos(ang), py - 30 * math.sin(ang)
        linea(cr, [(px, py), (ex, ey)], 7, (0.62, 0.63, 0.68))
        linea(cr, [(bx, by), (ex, ey)], 14, TINTA)
        circ(cr, px, py, 10, (0.32, 0.32, 0.37))


def auto_frente(cr, x, y, esc, u, edad, color, placa="", conductor=None, gotas=True, luces=0.5):
    """Auto visto de frente. (x, y) = centro del borde inferior del parabrisas."""
    if esc <= 0.001:
        return
    osc = _sombra(color, 0.78)
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    cr.save()
    cr.scale(1, 0.14)
    circ(cr, 0, 236 / 0.14, 360, (0, 0, 0), 0.30)
    cr.restore()
    for sx in (-1, 1):
        rr(cr, sx * 262 - 44, 150, 88, 86, 18, (0.07, 0.07, 0.09))
        rr(cr, sx * (AB + 52) - 28, -70, 56, 36, 10, osc)                       # espejos
    rr(cr, -AT - 20, -HV - 30, 2 * AT + 40, 70, 30, color)                      # techo
    poli(cr, [(-AB - 28, 10), (-AT - 24, -HV - 6), (AT + 24, -HV - 6), (AB + 28, 10)], color)   # parantes
    poli(cr, [(-AB - 28, 0), (AB + 28, 0), (AB + 64, 80), (-AB - 64, 80)], color)               # capó
    poli(cr, [(-AB - 28, 0), (AB + 28, 0), (AB + 36, 16), (-AB - 36, 16)], osc, 0.55)
    rr(cr, -AB - 68, 70, 2 * (AB + 68), 104, 26, color)                         # frente
    rr(cr, -176, 84, 352, 60, 12, (0.13, 0.13, 0.17))                           # parrilla
    for i in range(4):
        rect(cr, -166, 93 + i * 12, 332, 5, (0.72, 0.73, 0.79))
    for sx in (-1, 1):
        circ(cr, sx * 250, 116, 40, (0.76, 0.77, 0.82))
        circ(cr, sx * 250, 116, 31, (1.0, 0.98, 0.92))
        if luces > 0:
            halo(cr, sx * 250, 116, 170, (1.0, 0.97, 0.90), 0.55 * luces)
    rr(cr, -AB - 80, 164, 2 * (AB + 80), 32, 15, (0.82, 0.83, 0.88))            # paragolpes
    if placa:
        rr(cr, -104, 142, 208, 58, 9, (0.12, 0.12, 0.16))
        rr(cr, -98, 148, 196, 46, 6, (0.97, 0.97, 0.95))
        tam = 36
        while M.ancho_texto(cr, placa, tam) > 180:
            tam -= 2
        M.texto(cr, placa, 0, 171, tam, TINTA)
    parabrisas(cr, u, edad, gotas=gotas, conductor=conductor)
    cr.restore()


def prototipo(cr, x, y, esc, u, edad, luz=False):
    """El invento sobre el banco: un parabrisas de prueba con su motor y la caja de control."""
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    for sx in (-1, 1):
        rect(cr, sx * 190 - 9, -70, 18, 70, (0.50, 0.51, 0.57))
    rr(cr, -AB - 14, -84, 2 * AB + 28, 30, 8, (0.36, 0.37, 0.43))
    rr(cr, -60, -80, 150, 46, 10, (0.24, 0.25, 0.30))          # motor
    circ(cr, 62, -57, 12, M.VERDE if luz else (0.45, 0.20, 0.22))
    cr.translate(0, -84)
    vidrio_path(cr)
    cr.set_line_width(26)
    cr.set_source_rgb(0.36, 0.37, 0.43)
    cr.stroke()
    parabrisas(cr, u, edad, gotas=False, interior=False)
    cr.restore()


def ojo_panel(cr, x, y, esc, cierre, t, pelo=PELO_K):
    """Primer plano del ojo de Kearns detrás del lente. cierre: 0 abierto, 1 cerrado."""
    if esc <= 0.001:
        return
    w, h = 600, 300
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    rr(cr, -w / 2 - 12, -h / 2 - 12, w + 24, h + 24, 50, (1, 1, 1))
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, 40)
    cr.clip()
    rect(cr, -w / 2, -h / 2, w, h, PIEL)
    halo(cr, -260, 150, 300, _sombra(PIEL, 0.80), 0.55)
    # ceja
    cr.new_path()
    cr.move_to(-196, -96)
    cr.curve_to(-100, -138, 80, -138, 200, -104)
    cr.set_line_width(26)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_source_rgb(*_sombra(pelo, 0.9))
    cr.stroke()
    a, b, cy = 186.0, 80.0, 30.0

    def contorno():
        cr.new_path()
        cr.move_to(-a, cy)
        cr.curve_to(-a * 0.5, cy - b * 1.35, a * 0.5, cy - b * 1.35, a, cy)
        cr.curve_to(a * 0.5, cy + b * 1.15, -a * 0.5, cy + b * 1.15, -a, cy)
        cr.close_path()

    contorno()
    cr.set_source_rgb(1, 1, 1)
    cr.fill()
    cr.save()
    contorno()
    cr.clip()
    dx = 16 * math.sin(t * 1.1)
    circ(cr, dx, cy + 2, 76, (0.36, 0.23, 0.13))
    circ(cr, dx, cy + 2, 64, (0.50, 0.33, 0.18))
    circ(cr, dx, cy + 2, 34, TINTA)
    circ(cr, dx - 24, cy - 24, 15, (1, 1, 1))
    yc = (cy - b * 1.35) + clamp(cierre) * (b * 2.5)
    cr.new_path()
    cr.move_to(-a - 6, cy)
    cr.curve_to(-a * 0.5, yc, a * 0.5, yc, a + 6, cy)
    cr.line_to(a + 6, cy - 3 * b)
    cr.line_to(-a - 6, cy - 3 * b)
    cr.close_path()
    cr.set_source_rgb(*_sombra(PIEL, 0.90))
    cr.fill()
    cr.new_path()
    cr.move_to(-a, cy)
    cr.curve_to(-a * 0.5, yc, a * 0.5, yc, a, cy)
    cr.set_line_width(11)
    cr.set_source_rgb(*TINTA)
    cr.stroke()
    cr.restore()
    contorno()
    cr.set_line_width(7)
    cr.set_source_rgb(*TINTA)
    cr.stroke()
    # lente y patilla de los anteojos
    cr.save()
    cr.translate(0, 26)
    cr.scale(1, 0.50)
    cr.new_path()
    cr.arc(0, 0, 256, 0, 2 * math.pi)
    cr.restore()
    cr.set_line_width(20)
    cr.set_source_rgb(0.13, 0.13, 0.16)
    cr.stroke()
    linea(cr, [(-256, 26), (-320, 10)], 20, (0.13, 0.13, 0.16))
    linea(cr, [(256, 26), (320, 20)], 20, (0.13, 0.13, 0.16))
    poli(cr, [(-150, -70), (-110, -84), (-176, 50), (-206, 36)], (1, 1, 1), 0.16)
    cr.restore()


def edificio(cr, x, w, h, nombre, color, tam=44):
    """Edificio genérico de oficinas con el nombre de la empresa en un cartel (sin logotipos)."""
    y = PISO - h
    rect(cr, x, y, w, h, color)
    rect(cr, x, y, w, 16, _sombra(color, 1.25))
    rnd = random.Random(nombre)
    for yy in range(int(y + 118), PISO - 70, 62):
        for xx in range(int(x + 26), int(x + w - 44), 56):
            rect(cr, xx, yy, 32, 38, (1.0, 0.84, 0.70) if rnd.random() < 0.6 else _sombra(color, 0.7))
    rect(cr, x + w / 2 - 34, PISO - 76, 68, 76, _sombra(color, 0.55))
    wc = M.ancho_texto(cr, nombre, tam) + 44
    rr(cr, x + w / 2 - wc / 2, y - 46, wc, 86, 12, (0.97, 0.97, 0.95))
    rect(cr, x + w / 2 - wc / 2 + 30, y + 38, 12, 22, _sombra(color, 0.6))
    rect(cr, x + w / 2 + wc / 2 - 42, y + 38, 12, 22, _sombra(color, 0.6))
    M.texto(cr, nombre, x + w / 2, y - 3, tam, TINTA)


# ------------------------------------------------------------------ decorados

def dec_noche(cr, t, horizonte=880):
    g = cairo.LinearGradient(0, 380, 0, PISO)
    g.add_color_stop_rgb(0, 0.13, 0.05, 0.14)
    g.add_color_stop_rgb(1, 0.36, 0.15, 0.30)
    cr.new_path()
    cr.rectangle(0, 0, W, PISO)
    cr.set_source(g)
    cr.fill()
    rnd = random.Random(4)
    x = -30
    while x < W:
        w, h = rnd.uniform(110, 190), rnd.uniform(150, 330)
        rect(cr, x, horizonte - h, w, h, (0.17, 0.08, 0.18))
        for yy in range(int(horizonte - h + 26), horizonte - 30, 52):
            for xx in range(int(x + 18), int(x + w - 30), 44):
                if rnd.random() < 0.35:
                    rect(cr, xx, yy, 20, 28, (1.0, 0.76, 0.66), 0.55)
        x += w + rnd.uniform(0, 14)
    rect(cr, 0, horizonte, W, PISO - horizonte, (0.19, 0.10, 0.19))
    rect(cr, 0, horizonte, W, 8, (0.28, 0.16, 0.27))


def dec_aula(cr, t, p):
    rect(cr, 0, 0, W, PISO, (0.62, 0.41, 0.38))
    rect(cr, 0, 1050, W, PISO - 1050, (0.42, 0.26, 0.26))
    rect(cr, 0, 1042, W, 12, (0.80, 0.62, 0.54))
    # pizarrón
    rr(cr, 316, 458, 730, 500, 12, (0.46, 0.30, 0.18))
    rect(cr, 336, 478, 690, 446, (0.11, 0.25, 0.20))
    rect(cr, 336, 924, 690, 16, (0.58, 0.40, 0.24))
    rect(cr, 880, 912, 60, 12, (0.96, 0.96, 0.92))
    tiza = (0.96, 0.96, 0.90)
    s = p.get("pizarron", "INGENIERÍA")
    n = int(math.ceil(len(s) * clamp((t - 0.2) / 0.7)))
    if n:
        M.texto(cr, s[:n], 470, 548, 70, tiza, alinear="izq", alfa=0.95)
    linea(cr, [(470, 596), (470 + 430 * clamp((t - 0.8) / 0.3), 596)], 6, tiza, 0.8)
    # circuito de tiza (resistencia, condensador y pila)
    k = clamp((t - 0.5) / 1.2)
    if k > 0:
        pts = [(520, 690), (600, 690)] + [(600 + 16 * i, 690 + (22 if i % 2 else -22)) for i in range(1, 8)] + \
              [(728, 690), (870, 690), (870, 760)]
        m_ = max(2, int(len(pts) * k))
        linea(cr, pts[:m_], 6, tiza, 0.85)
    if k > 0.55:
        linea(cr, [(840, 760), (900, 760)], 6, tiza, 0.85)
        linea(cr, [(840, 782), (900, 782)], 6, tiza, 0.85)
        linea(cr, [(870, 782), (870, 850), (520, 850), (520, 800)], 6, tiza, 0.85)
        linea(cr, [(490, 800), (550, 800)], 6, tiza, 0.85)
        linea(cr, [(504, 778), (536, 778)], 6, tiza, 0.85)
        linea(cr, [(520, 778), (520, 690)], 6, tiza, 0.85)
    # banderín
    poli(cr, [(40, 470), (286, 524), (40, 578)], ROJO_K)
    rect(cr, 34, 462, 10, 124, (0.86, 0.80, 0.72))
    M.texto(cr, p.get("banderin", "DETROIT"), 128, 524, 34, (1, 1, 1))


def dec_boda(cr, t, vaiven=0.0, brillo=1.0, cartel="RECIÉN CASADOS"):
    rect(cr, 0, 0, W, PISO, (0.40, 0.11, 0.18))
    for x in range(0, W, 120):
        rect(cr, x + 46, 0, 26, PISO, (0.45, 0.14, 0.21))
    rect(cr, 0, 1010, W, PISO - 1010, (0.27, 0.13, 0.13))
    rect(cr, 0, 1000, W, 12, (0.93, 0.72, 0.54))
    # ventana con la noche y la luna
    rr(cr, 660, 470, 330, 400, 14, (0.95, 0.92, 0.86))
    rect(cr, 678, 488, 294, 364, (0.12, 0.05, 0.14))
    circ(cr, 900, 560, 40, (0.97, 0.95, 0.92))
    circ(cr, 884, 550, 34, (0.12, 0.05, 0.14))
    for sx, sy in ((720, 540), (790, 610), (850, 700), (735, 720), (930, 660)):
        circ(cr, sx, sy, 4, (1, 1, 1), 0.5 + 0.4 * math.sin(t * 3 + sx))
    rect(cr, 820, 488, 10, 364, (0.95, 0.92, 0.86))
    for sx in (1, -1):   # cortinas
        cx = 825 + sx * 185
        poli(cr, [(cx - 40, 450), (cx + 40, 450), (cx + 40 + sx * 12, 900), (cx - 40 + sx * 12, 900)],
             (0.93, 0.86, 0.80))
    # cartel con corazones
    rr(cr, 572, 420, 446, 84, 20, (0.98, 0.96, 0.94))
    M.texto(cr, cartel, 795, 462, 36, ROJO_K)
    for hx_ in (604, 986):
        cr.save()
        cr.translate(hx_, 462)
        cr.scale(0.075, 0.075)
        cr.new_path()
        cr.move_to(0, 200)
        cr.curve_to(-320, -20, -170, -280, 0, -110)
        cr.curve_to(170, -280, 320, -20, 0, 200)
        cr.set_source_rgb(*ROJO_K)
        cr.fill()
        cr.restore()
    # araña del techo (se sacude cuando el corcho le pega)
    cr.save()
    cr.translate(470, 360)
    cr.rotate(vaiven)
    rect(cr, -5, 0, 10, 190, (0.93, 0.72, 0.54))
    halo(cr, 0, 215, 340, (1.0, 0.92, 0.76), 0.30 * brillo)
    for i in range(5):
        ang = math.pi * (0.08 + 0.21 * i)
        bx, by = math.cos(ang) * 150, 205 + math.sin(ang) * 34
        linea(cr, [(0, 196), (bx, by)], 10, (0.93, 0.72, 0.54))
        rect(cr, bx - 7, by - 34, 14, 30, (0.98, 0.96, 0.92))
        circ(cr, bx, by - 42, 12, (1.0, 0.93, 0.74))
    rr(cr, -40, 180, 80, 44, 18, (0.93, 0.72, 0.54))
    circ(cr, 0, 236, 12, (0.93, 0.72, 0.54))
    cr.restore()
    # mesita con la hielera
    rr(cr, 520, 1040, 150, 18, 8, (0.98, 0.96, 0.94))
    poli(cr, [(530, 1058), (660, 1058), (676, PISO), (514, PISO)], (0.95, 0.92, 0.90))
    poli(cr, [(560, 968), (630, 968), (622, 1040), (568, 1040)], (0.78, 0.80, 0.86))
    rect(cr, 556, 962, 78, 10, (0.90, 0.91, 0.95))


def dec_taller(cr, t):
    rect(cr, 0, 0, W, PISO, (0.34, 0.29, 0.37))
    for y in range(440, PISO, 80):   # bloques de la pared del sótano
        rect(cr, 0, y, W, 4, (0.29, 0.24, 0.32))
    # tablero de herramientas
    rr(cr, 560, 480, 470, 280, 10, (0.60, 0.46, 0.36))
    for i in range(7):
        for j in range(4):
            circ(cr, 600 + i * 66, 520 + j * 66, 4, (0.44, 0.32, 0.25))
    hta = (0.22, 0.20, 0.25)
    linea(cr, [(630, 540), (630, 690)], 14, hta)                      # martillo
    rr(cr, 596, 520, 70, 34, 8, hta)
    linea(cr, [(740, 530), (740, 700)], 12, hta)                      # llave
    circ(cr, 740, 530, 22, hta)
    circ(cr, 740, 522, 9, (0.60, 0.46, 0.36))
    poli(cr, [(830, 530), (980, 560), (980, 590), (830, 620)], hta)   # serrucho
    rr(cr, 800, 540, 56, 70, 12, ROJO_K)
    # lámpara colgante
    rect(cr, 296, 0, 8, 470, (0.16, 0.14, 0.18))
    poli(cr, [(250, 520), (350, 520), (322, 462), (278, 462)], (0.16, 0.14, 0.18))
    circ(cr, 300, 524, 20, (1.0, 0.95, 0.82))
    cono = cairo.LinearGradient(0, 520, 0, PISO)
    cono.add_color_stop_rgba(0, 1.0, 0.90, 0.72, 0.30)
    cono.add_color_stop_rgba(1, 1.0, 0.90, 0.72, 0.0)
    cr.new_path()
    cr.move_to(262, 524)
    cr.line_to(338, 524)
    cr.line_to(640, PISO)
    cr.line_to(-40, PISO)
    cr.close_path()
    cr.set_source(cono)
    cr.fill()
    # banco de trabajo
    rect(cr, 430, 1010, 650, 30, MADERA)
    rect(cr, 430, 1040, 650, 12, _sombra(MADERA, 0.7))
    for x in (456, 1030):
        rect(cr, x, 1052, 26, PISO - 1052, _sombra(MADERA, 0.8))
    rect(cr, 482, 1150, 548, 18, _sombra(MADERA, 0.7))


def dec_oficina(cr, t, p):
    rect(cr, 0, 0, W, PISO, (0.36, 0.27, 0.32))
    for x in range(0, W, 180):
        rr(cr, x + 14, 430, 152, 560, 6, (0.40, 0.30, 0.36))
    rect(cr, 0, 1000, W, PISO - 1000, (0.27, 0.19, 0.24))
    rect(cr, 0, 994, W, 10, (0.52, 0.40, 0.44))
    # cartel de la empresa: solo el nombre, en letras de imprenta
    rr(cr, 600, 470, 400, 150, 16, (0.97, 0.97, 0.95))
    M.texto(cr, p.get("cartel", "FORD"), 800, 530, 92, TINTA)
    rect(cr, 660, 584, 280, 6, ROJO_K)
    # escritorio
    rect(cr, 500, 1010, 580, 30, (0.50, 0.32, 0.20))
    rect(cr, 524, 1040, 556, PISO - 1040, (0.38, 0.24, 0.15))
    rr(cr, 560, 1076, 480, 130, 8, (0.33, 0.20, 0.12))
    rr(cr, 940, 968, 96, 44, 8, (0.12, 0.12, 0.15))              # teléfono
    rr(cr, 930, 956, 116, 18, 9, (0.18, 0.18, 0.22))


def dec_tribunal(cr, t):
    rect(cr, 0, 0, W, PISO, (0.33, 0.20, 0.16))
    for x in range(0, W, 180):
        rr(cr, x + 16, 440, 148, 500, 6, (0.38, 0.24, 0.19))
    rect(cr, 0, 968, W, PISO - 968, (0.26, 0.15, 0.12))
    rect(cr, 0, 960, W, 12, (0.48, 0.31, 0.22))


def balanza(cr, x, y, esc, color):
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    linea(cr, [(0, -70), (0, 70)], 10, color)
    linea(cr, [(-90, -52), (90, -52)], 10, color)
    rr(cr, -44, 64, 88, 16, 8, color)
    for sx in (-1, 1):
        linea(cr, [(sx * 90, -52), (sx * 62, 16)], 4, color)
        linea(cr, [(sx * 90, -52), (sx * 118, 16)], 4, color)
        cr.new_path()
        cr.arc(sx * 90, 16, 30, 0, math.pi)
        cr.close_path()
        cr.set_source_rgb(*color)
        cr.fill()
    cr.restore()


def estrado(cr, x0, x1, y, emblema=True):
    """Estrado del juez: frente de madera con moldura. y = altura de la tapa."""
    rect(cr, x0, y + 24, x1 - x0, PISO - y - 24, (0.29, 0.17, 0.11))
    rr(cr, x0 + 26, y + 60, x1 - x0 - 52, PISO - y - 100, 10, (0.35, 0.21, 0.14))
    rect(cr, x0 - 16, y, x1 - x0 + 32, 26, (0.52, 0.33, 0.20))
    rect(cr, x0 - 16, y + 24, x1 - x0 + 32, 8, (0.22, 0.12, 0.08))
    if emblema:
        balanza(cr, (x0 + x1) / 2, y + 60 + (PISO - y - 100) / 2, 0.75, (0.93, 0.72, 0.54))


# ------------------------------------------------------------------ escenas

def esc_gancho(cr, t, p):
    """Gancho y cierre del bucle. `fase` desplaza el reloj: la última escena usa fase 0 y dura 0,8 s;
    la primera usa fase 0,8 y así arranca exactamente donde terminó la otra."""
    tau = t + p.get("fase", 0.0)
    v = p.get("fase_voz", 0.8)          # tau en el que empieza la locución
    g = cairo.RadialGradient(640, 860, 60, 640, 860, 1150)
    g.add_color_stop_rgb(0, 0.50, 0.15, 0.28)
    g.add_color_stop_rgb(1, 0.09, 0.03, 0.11)
    cr.new_path()
    cr.rectangle(0, 0, W, H)
    cr.set_source(g)
    cr.fill()
    cr.save()
    cr.rectangle(0, 0, W, PISO)
    cr.clip()
    for i in range(12):   # rayos que giran lento
        a0 = tau * 0.12 + i * math.pi / 6
        poli(cr, [(640, 880), (640 + math.cos(a0) * 1500, 880 + math.sin(a0) * 1500),
                  (640 + math.cos(a0 + 0.20) * 1500, 880 + math.sin(a0 + 0.20) * 1500)], (1, 1, 1), 0.035)
    lluvia_billetes(cr, tau, 7, 21, y0=640, x0=330, x1=1040)
    # el auto con el limpiaparabrisas intermitente
    pasadas = ciclo(2.2, 0.34, desfase=v + 4.82 - 2 * 2.2)
    u, edad = barrido(tau, pasadas)
    halo(cr, 730, 900, 420, (1.0, 0.80, 0.70), 0.16)
    auto_frente(cr, 735, 1017, 0.95, u, edad, AUTO_KEARNS, luces=0.35)
    dz = tau - (v + 4.82)
    if 0 <= dz < 1.2:   # destello cuando la voz dice «limpiaparabrisas»
        for i, (sx, sy) in enumerate(((560, 850), (905, 870), (735, 800))):
            k = math.sin(clamp((dz - i * 0.12) / 0.7) * math.pi)
            estrella(cr, sx, sy, 46 * k, (1, 1, 1), n=4, giro=dz * 2 + i, a=0.95)
    # Kearns con la escobilla en alto
    lluvia_billetes(cr, tau, 16, 33, y0=640, desde=v + 1.62)
    salta = tau >= v + 3.96 and tau < v + 5.4
    persona(cr, "kearns_mayor", 212, "k_trofeo_salta" if salta else "k_trofeo", tau, 1, 0.95, "escobilla")
    cr.restore()
    banda(cr)
    # cifra
    pulso = 1 + 0.10 * math.sin(clamp((tau - (v + 2.5)) / 0.4) * math.pi)
    M.texto(cr, p.get("antes", "UNOS"), 540, 492, 50, M.BLANCO)
    cr.save()
    cr.translate(540, 578)
    cr.scale(pulso, pulso)
    s = p.get("cifra", "$30 MILLONES")
    tam = 118
    while M.ancho_texto(cr, s, tam) > 940:
        tam -= 2
    M.texto(cr, s, 4, 5, tam, (0.04, 0.02, 0.06), alfa=0.6)
    M.texto(cr, s, 0, 0, tam, M.VERDE)
    cr.restore()
    titulo(cr, p, tau, fijo=True)


def esc_aula(cr, t, p):
    cr.save()
    camara(cr, t)
    dec_aula(cr, t, p)
    persona(cr, "kearns", 232, "k_clase", t, 1, 1.05, "puntero")
    for x, pelo, ropa in ((560, (0.30, 0.18, 0.10), (0.30, 0.34, 0.30)), (760, (0.80, 0.62, 0.36), ROJO_K),
                          (950, (0.12, 0.09, 0.08), (0.86, 0.84, 0.80))):
        yb = 1206 + 4 * math.sin(t * 2 + x)
        rr(cr, x - 96, yb + 40, 192, 90, 40, ropa)
        circ(cr, x, yb, 62, PIEL)
        cr.new_path()
        cr.arc(x, yb, 65, math.pi * 0.86, math.pi * 2.14)
        cr.close_path()
        cr.set_source_rgb(*pelo)
        cr.fill()
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def esc_boda(cr, t, p):
    tp, tl, to = p.get("t_corcho", 2.28), p.get("t_lampara", 2.68), p.get("t_ojo", 3.24)
    cr.save()
    camara(cr, t)
    vaiven = 0.0
    if t >= tl:
        vaiven = 0.20 * math.sin((t - tl) * 11) * math.exp(-(t - tl) * 2.2)
    dec_boda(cr, t, vaiven, cartel=p.get("cartel", "RECIÉN CASADOS"))
    lamp = (470, 600)
    persona(cr, "novia", 850, "sonreir" if t < tp + 0.12 else "sorpresa", t, -1, 1.0, "copa" if t < tp + 0.12 else None)
    E["corcho_puesto"] = t < tp
    if t < tp:
        persona(cr, "kearns_boda", 300, "k_botella", t, 1, 1.05, "botella")
    elif t < to:
        persona(cr, "kearns_boda", 300, "k_botella_mira", t, 1, 1.05, "botella")
    else:
        persona(cr, "kearns_boda", 300, "k_ojo", t - to, 1, 1.05)
    ojo = aqui(cr, "ojo")
    boca = aqui(cr, "boca_botella") if t < to else (0, 0)   # nada que dependa de cuadros anteriores
    if t >= to:   # la botella quedó en el piso
        cr.save()
        cr.translate(430, PISO - 20)
        cr.rotate(1.45)
        rr(cr, -22, -92, 44, 104, 10, (0.09, 0.30, 0.20))
        poli(cr, [(-22, -84), (22, -84), (9, -122), (-9, -122)], (0.09, 0.30, 0.20))
        rect(cr, -9, -150, 18, 30, (0.09, 0.30, 0.20))
        rr(cr, -19, -62, 38, 40, 4, (0.97, 0.94, 0.88))
        cr.restore()
        for i in range(5):
            circ(cr, 560 + i * 20, PISO - 12 - (i % 2) * 8, 12 - i, (1, 1, 1), 0.85)
    elif t >= tp:   # espuma que sale de la botella
        rnd = random.Random(8)
        for i in range(14):
            d = t - tp - rnd.uniform(0, 0.25)
            vx, vy = rnd.uniform(-60, 110), rnd.uniform(-380, -180)
            if d > 0:
                circ(cr, boca[0] + vx * d, boca[1] + vy * d + 520 * d * d, rnd.uniform(5, 11), (1, 1, 1),
                     0.9 * clamp(1.3 - d))
    # el corcho: de la botella a la araña y de ahí al ojo

    def pos(tt):
        if tt < tl:
            q = M.ease_out_cubic((tt - tp) / (tl - tp))
            return boca[0] + (lamp[0] - boca[0]) * q, boca[1] + (lamp[1] - boca[1]) * q
        q = clamp((tt - tl) / (to - tl)) ** 1.6
        return lamp[0] + (ojo[0] - lamp[0]) * q, lamp[1] + (ojo[1] - lamp[1]) * q

    if tp <= t < to:
        for i in range(7, 0, -1):
            tt = t - i * 0.022
            if tt >= tp:
                circ(cr, *pos(tt), 15 - i * 1.4, (1, 1, 1), 0.62 - i * 0.07)
        cx_, cy_ = pos(t)
        cr.save()
        cr.translate(cx_, cy_)
        cr.rotate(t * 22)
        rr(cr, -17, -22, 34, 44, 9, (0.84, 0.64, 0.42))
        rr(cr, -17, -22, 34, 14, 7, (0.66, 0.46, 0.28))
        cr.restore()
    elif t >= to and t - to < 0.7:   # rebota y cae
        d = t - to
        cr.save()
        cr.translate(ojo[0] + 130 * d, ojo[1] - 150 * d + 700 * d * d)
        cr.rotate(t * 16)
        rr(cr, -17, -22, 34, 44, 9, (0.84, 0.64, 0.42), clamp(1.6 - d * 2))
        cr.restore()
    if tp <= t < tp + 0.55:   # ¡POP!
        k = M.ease_out_back((t - tp) / 0.2)
        estrella(cr, boca[0] + 104, boca[1] + 56, 94 * k, (1, 1, 1), n=12, giro=0.2, dentro=0.74)
        if k > 0.3:
            M.texto(cr, p.get("pop", "¡POP!"), boca[0] + 104, boca[1] + 56, 38 * k, ROJO_K)
    if tl <= t < tl + 0.3:
        estrella(cr, lamp[0], lamp[1], 60 * math.sin((t - tl) / 0.3 * math.pi), (1.0, 0.95, 0.82), n=8)
    if t >= to:
        k = M.ease_out_back((t - to) / 0.22)
        fin = clamp(1.9 - (t - to) * 1.6)
        fin = clamp(1.25 - (t - to) * 2.6)
        estrella(cr, ojo[0] + 34, ojo[1] - 16, 78 * k, M.BLANCO, n=10, giro=0.3 + (t - to), a=fin)
        estrella(cr, ojo[0] + 34, ojo[1] - 16, 50 * k, M.ROJO, n=10, giro=0.6 - (t - to), a=fin)
        for i in range(3):   # rayitas de dolor que quedan titilando
            ang = -0.9 + i * 0.5 + 0.1 * math.sin(t * 20)
            r0 = 92 + 8 * math.sin(t * 18 + i)
            linea(cr, [(ojo[0] + math.cos(ang) * r0, ojo[1] + math.sin(ang) * r0),
                       (ojo[0] + math.cos(ang) * (r0 + 34), ojo[1] + math.sin(ang) * (r0 + 34))], 8, M.BLANCO, 1 - fin)
        M.globo(cr, p.get("globo", "¡MI OJO!"), 330, 606, t - to - 0.12)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def esc_ojo(cr, t, p):
    t1 = p.get("t_ojo", 1.54)
    parp = p.get("parpadeos", [1.94, 3.14])
    s = 0.30
    viejas = [(-0.22 + k * 0.68, 0.34) for k in range(3) if -0.22 + k * 0.68 + 0.68 <= parp[0] + 0.02]
    nuevas = [(T, s) for T in parp]
    u, edad = barrido(t, viejas + nuevas)
    cierre, _ = barrido(t, nuevas)
    cr.save()
    camara(cr, t, 0.04)
    dec_noche(cr, t, horizonte=940)
    circ(cr, 150, 520, 44, (0.96, 0.93, 0.96), 0.9)

    def conductor(c):
        PJ.personaje(c, "kearns", 96, 372, 1.05, -1, "k_volante" if t < 0.72 else "k_volante_idea", t)
        c.new_path()
        c.arc(40, 22, 96, math.pi, 2 * math.pi)
        c.set_line_width(15)
        c.set_source_rgb(0.12, 0.11, 0.15)
        c.stroke()

    auto_frente(cr, 540, 1048, 0.92, u, edad, AUTO_KEARNS, conductor=conductor, luces=0.6)
    lluvia(cr, t, 90, 0.30)
    if 0.72 <= t < t1 + 0.15:   # «notó algo»
        k = M.ease_out_back((t - 0.72) / 0.25)
        estrella(cr, 700, 700, 74 * k, M.BLANCO, n=10, giro=0.2)
        M.texto(cr, "!", 700, 700, 90 * k, ROJO_K)
    kp = M.ease_out_back((t - t1) / 0.35)
    if kp > 0.01:
        for i, (bx, by, br) in enumerate(((700, 800, 9), (676, 774, 13))):
            circ(cr, bx, by, br * clamp((t - t1) * 6 - i), (1, 1, 1))
        ojo_panel(cr, 540, 588, kp, cierre, t)
        en_pausa = cierre < 0.02
        puntos = "." * (1 + int((t * 3) % 3))
        if t > parp[0] - 0.05:
            if en_pausa:
                etiqueta(cr, p.get("pausa", "PAUSA") + puntos, 540, 782, 1.0, 44, M.BLANCO, TINTA)
            else:
                etiqueta(cr, p.get("parpadea", "PARPADEA = BARRE"), 540, 782, 1.0, 44, ROJO_K, M.BLANCO)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def esc_taller(cr, t, p):
    pasadas = [(0.72, 0.27), (1.72, 0.27)]
    u, edad = barrido(t, pasadas)
    tf = p.get("t_funciona", 1.68)
    cr.save()
    camara(cr, t)
    dec_taller(cr, t)
    prototipo(cr, 770, 1010, 0.86, u, edad, luz=u > 0.02)
    # caja de control con perilla y cables
    linea(cr, [(560, 990), (600, 1002), (700, 1000), (760, 960)], 6, ROJO_K)
    linea(cr, [(560, 978), (640, 950), (700, 940)], 6, (0.95, 0.95, 0.90))
    rr(cr, 462, 944, 110, 66, 10, (0.13, 0.13, 0.17))
    circ(cr, 500, 977, 17, (0.90, 0.90, 0.94))
    linea(cr, [(500, 977), (500 + 13 * math.cos(t * 2), 977 - 13 * abs(math.sin(t * 2)) - 2)], 5, ROJO_K)
    circ(cr, 546, 966, 8, M.VERDE if u > 0.02 else (0.40, 0.18, 0.20))
    if t < tf:
        persona(cr, "kearns", 262, "k_trabajar", t, 1, 1.08, "destornillador")
    else:
        persona(cr, "kearns", 262, "k_festejo", t - tf, 1, 1.08)
        M.globo(cr, p.get("globo", "¡FUNCIONA!"), 300, 604, t - tf - 0.05)
    if t > 0.6:
        if u > 0.02:
            etiqueta(cr, p.get("barre", "BARRE"), 770, 668, 1.0, 46, ROJO_K, M.BLANCO, punta=1)
        else:
            etiqueta(cr, p.get("pausa", "PAUSA") + "." * (1 + int((t * 4) % 3)), 770, 668, 1.0, 46, M.BLANCO,
                     TINTA, punta=1)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def esc_ford(cr, t, p):
    tn = p.get("t_no", 1.04)
    ts = p.get("t_sello", 1.40)
    u, edad = barrido(t, [(0.15, 0.24), (0.95, 0.24), (2.0, 0.24)])
    cr.save()
    camara(cr, t)
    dec_oficina(cr, t, p)
    persona(cr, "ford1", 770, "escuchar" if t < tn else "k_cruzar", t, -1, 0.95)
    persona(cr, "ford2", 950, "escuchar" if t < tn else "k_negar", t, -1, 0.95)
    rect(cr, 500, 1010, 580, 30, (0.50, 0.32, 0.20))            # la tapa del escritorio tapa las piernas
    rect(cr, 524, 1040, 556, PISO - 1040, (0.38, 0.24, 0.15))
    rr(cr, 560, 1076, 480, 130, 8, (0.33, 0.20, 0.12))
    prototipo(cr, 610, 1010, 0.36, u, edad, luz=u > 0.02)
    if t < ts + 0.1:
        persona(cr, "kearns", 236, "señalar", t, 1, 1.05)
    else:
        persona(cr, "kearns", 236, "triste", t, 1, 1.05)
    sello(cr, p.get("sello", "SIN ACUERDO"), 328, 598, t - ts, M.ROJO, tam=60, ang=-0.10)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def esc_autos(cr, t, p):
    t1, t2 = p.get("t_ford", 1.50), p.get("t_chrysler", 2.96)
    cr.save()
    camara(cr, t, 0.04)
    dec_noche(cr, t, horizonte=700)
    # calle en perspectiva
    poli(cr, [(700, 700), (900, 700), (1180, PISO), (250, PISO)], (0.14, 0.07, 0.15))
    for i in range(5):
        f0 = (i + (t * 0.5) % 1.0) / 5.0
        f1 = min(1.0, f0 + 0.09)
        x0, y0_ = 800 + (715 - 800) * f0 ** 2, 700 + (PISO - 700) * f0 ** 2
        x1, y1_ = 800 + (715 - 800) * f1 ** 2, 700 + (PISO - 700) * f1 ** 2
        linea(cr, [(x0, y0_), (x1, y1_)], 4 + 8 * f0, (0.80, 0.76, 0.82), 0.5)
    # segundo auto (aparece cuando la voz nombra a la otra empresa)
    k2 = M.ease_out_cubic((t - t2) / 0.5)
    if t >= t2:
        u2, e2 = barrido(t, ciclo(1.5, 0.26, desfase=t2 + 0.45))
        auto_frente(cr, 800 + 72 * k2, 690 + 40 * k2, 0.16 + 0.30 * k2, u2, e2, AUTO_CHRYSLER,
                    placa=p.get("placa2", "CHRYSLER"), luces=0.7)
    # primer auto: llega desde el fondo
    k1 = M.ease_out_cubic((t - 0.25) / 1.15)
    if t >= 0.25:
        u1, e1 = barrido(t, ciclo(1.5, 0.28, desfase=0.75))
        auto_frente(cr, 790 - 170 * k1, 700 + 334 * k1, 0.14 + 0.62 * k1, u1, e1, AUTO_FORD,
                    placa=p.get("placa1", "FORD"), luces=0.8)
    if t < t1 + 0.28:
        pose_k = "k_paraguas"
    else:
        pose_k = "k_paraguas_o"
    persona(cr, "kearns", 150, pose_k, t, 1, 0.86, "paraguas")
    lluvia(cr, t, 100, 0.28)
    etiqueta(cr, p.get("cartel1", "FORD · 1969"), 520, 730, t - t1, 50, M.BLANCO, TINTA, punta=1)
    etiqueta(cr, p.get("cartel2", "CHRYSLER TAMBIÉN"), 742, 520, t - t2 - 0.48, 40, M.BLANCO, TINTA, punta=1,
             punta_dx=128)
    if t1 + 0.3 <= t < t2 + 0.2:
        M.globo(cr, p.get("globo1", "¿¡QUÉ!?"), 200, 660, t - t1 - 0.3)
    elif t >= t2 + 0.75:
        M.globo(cr, p.get("globo2", "¿¡OTRO!?"), 200, 660, t - t2 - 0.75)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def documento_patente(cr, x, y, esc, p):
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    cr.rotate(-0.04)
    rr(cr, -128, -150, 256, 300, 10, (0.97, 0.94, 0.86))
    cr.new_path()
    M.rrect(cr, -112, -134, 224, 268, 6)
    cr.set_line_width(4)
    cr.set_source_rgb(0.62, 0.50, 0.36)
    cr.stroke()
    M.texto(cr, p.get("doc", "PATENTE"), 0, -96, 38, TINTA)
    M.texto(cr, p.get("doc_anio", "1967"), 0, -48, 36, ROJO_K)
    # dibujo técnico: el parabrisas con sus escobillas
    cr.save()
    cr.translate(0, 62)
    cr.scale(0.34, 0.34)
    vidrio_path(cr)
    cr.set_line_width(12)
    cr.set_source_rgb(*TINTA)
    cr.stroke()
    ang = math.radians(118)
    for px, py in PIVOTES:
        linea(cr, [(px, py), (px + LARGO * math.cos(ang), py - LARGO * math.sin(ang))], 12, TINTA)
        cr.new_path()
        cr.arc(px, py, LARGO, -math.radians(ANG0), -math.radians(ANG1))
        cr.set_line_width(5)
        cr.set_dash([14, 12])
        cr.set_source_rgb(0.45, 0.42, 0.42)
        cr.stroke()
        cr.set_dash([])
    cr.restore()
    for i in range(3):
        rect(cr, -90, 84 + i * 16, 180 - i * 40, 6, (0.66, 0.62, 0.56))
    circ(cr, 84, 112, 30, ROJO_K)
    estrella(cr, 84, 112, 22, (1.0, 0.86, 0.80), n=8)
    cr.restore()


def esc_patente(cr, t, p):
    td = p.get("t_demanda", 1.06)
    cr.save()
    camara(cr, t, 0.04)
    g = cairo.LinearGradient(0, 380, 0, PISO)
    g.add_color_stop_rgb(0, 0.20, 0.08, 0.24)
    g.add_color_stop_rgb(1, 0.52, 0.22, 0.30)
    cr.new_path()
    cr.rectangle(0, 0, W, PISO)
    cr.set_source(g)
    cr.fill()
    edificio(cr, 62, 300, 440, p.get("empresa1", "FORD"), (0.33, 0.24, 0.34), 50)
    edificio(cr, 716, 300, 440, p.get("empresa2", "CHRYSLER"), (0.36, 0.26, 0.33), 44)
    kx = 540
    persona(cr, "kearns", kx, "k_patente", t, 1, 1.0)
    documento_patente(cr, kx + 4, 574, 0.86 * M.ease_out_back((t + 0.2) / 0.4), p)
    # las demandas vuelan a cada edificio y quedan estampadas
    destinos = ((212, 990, td, p.get("demanda1", "DEMANDA\n1978")), (866, 990, td + 0.32, p.get("demanda2", "DEMANDA\n1982")))
    for dx, dy, t0, txt in destinos:
        q = (t - t0) / 0.42
        if 0 <= q < 1:
            e = M.ease_in_out(q)
            x = kx + (dx - kx) * e
            y = 700 + (dy - 700) * e - 150 * math.sin(e * math.pi)
            cr.save()
            cr.translate(x, y)
            cr.rotate(q * 9)
            rr(cr, -44, -30, 88, 60, 6, (0.98, 0.97, 0.94))
            linea(cr, [(-44, -30), (0, 6), (44, -30)], 4, (0.70, 0.66, 0.62))
            circ(cr, 0, 4, 11, ROJO_K)
            cr.restore()
        sello(cr, txt, dx, dy, t - t0 - 0.42, M.ROJO, tam=50, ang=-0.12 if dx < 540 else 0.10)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def cheque_grande(cr, x, y, k, p, t):
    if k <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.rotate(-0.04)
    cr.scale(k, k)
    rr(cr, -326, -146, 652, 292, 22, (0.05, 0.30, 0.18))
    rr(cr, -314, -134, 628, 268, 16, (0.94, 0.98, 0.94))
    M.texto(cr, p.get("paga", "FORD"), -284, -88, 56, TINTA, alinear="izq")
    M.texto(cr, p.get("anio", "ACUERDO · 1990"), 284, -88, 36, (0.40, 0.44, 0.42), alinear="derecha")
    rect(cr, -284, -50, 568, 5, (0.70, 0.78, 0.72))
    v = p.get("monto", 10.2) * M.ease_out_cubic((t - 0.1) / 0.7)
    s = "$" + f"{v:.1f}".replace(".", ",") + " " + p.get("unidad", "MILLONES")
    tam = 80
    while M.ancho_texto(cr, "$10,2 " + p.get("unidad", "MILLONES"), tam) > 560:
        tam -= 2
    M.texto(cr, s, 0, 12, tam, VERDE_OSC)
    M.texto(cr, p.get("para", "PARA: ROBERT KEARNS"), -284, 92, 32, (0.40, 0.44, 0.42), alinear="izq")
    cr.new_path()
    cr.set_line_width(5)
    cr.set_source_rgb(*TINTA)
    for j in range(22):
        px, py = 150 + j * 6, 96 + math.sin(j * 0.9) * 13
        cr.line_to(px, py) if j else cr.move_to(px, py)
    cr.stroke()
    cr.restore()


def esc_pleito(cr, t, p):
    """Doce años en tribunales: el calendario corre de 1978 a 1990 y Kearns encanece. Después, Ford paga."""
    t2 = p.get("t_ford", 1.86)
    a0, a1 = p.get("desde_anio", 1978), p.get("hasta_anio", 1990)
    cr.save()
    camara(cr, t, 0.04)
    dec_tribunal(cr, t)
    # mesa con los expedientes que se apilan
    rect(cr, 430, 1040, 280, 26, (0.52, 0.33, 0.20))
    rect(cr, 450, 1066, 240, PISO - 1066, (0.30, 0.18, 0.12))
    n = int(15 * clamp((t - 0.2) / 1.5))
    rnd = random.Random(2)
    for i in range(n):
        dx = rnd.uniform(-10, 10)
        rr(cr, 500 + dx, 1028 - i * 13, 140, 11, 3, ((0.97, 0.95, 0.90), (0.93, 0.72, 0.54), (0.86, 0.84, 0.80))[i % 3])
    # Kearns: encanece mientras pasan los años
    gris = clamp((t - 0.45) / 1.2)
    if t < t2:
        pose_k, tk, obj = "k_alegato", t, "papeles"
    elif t < t2 + 1.2:
        pose_k, tk, obj = "escuchar", t, "papeles"
    else:
        pose_k, tk, obj = "k_festejo", t - t2 - 1.2, None
    if gris < 1:
        persona(cr, "kearns", 205, pose_k, tk, 1, 1.05, obj)
    if gris > 0:
        cr.push_group()
        persona(cr, "kearns_mayor", 205, pose_k, tk, 1, 1.05, obj)
        cr.pop_group_to_source()
        cr.paint_with_alpha(gris)
    # abogado de la empresa: entra con el cheque
    if t >= t2 - 0.1:
        xa = 1180 - 330 * M.ease_in_out((t - t2 + 0.1) / 0.75)
        llego = t >= t2 + 0.65
        persona(cr, "ford1", xa, "dar" if llego else "caminar", t, -1, 0.98, "cheque" if t < t2 + 1.0 else None)
    # calendario
    kc = 1 - M.ease_in_out((t - t2 - 0.35) / 0.25)
    if kc > 0.01:
        anio = a0 + (a1 - a0) * M.ease_in_out((t - 0.25) / 1.5)
        cr.save()
        cr.translate(600, 590)
        cr.scale(kc, kc)
        rr(cr, -200, -128, 400, 256, 22, (0.97, 0.95, 0.92))
        rr(cr, -200, -128, 400, 70, 22, ROJO_K)
        rect(cr, -200, -86, 400, 28, ROJO_K)
        for ax in (-110, 110):
            rr(cr, ax - 9, -150, 18, 50, 9, (0.30, 0.28, 0.32))
        M.texto(cr, p.get("cal", "AÑO"), 0, -93, 38, (1, 1, 1))
        frac = anio - math.floor(anio)
        cr.save()
        cr.translate(0, 38)
        cr.scale(1, 1 - 0.30 * math.sin(frac * math.pi) if a0 < anio < a1 else 1)
        M.texto(cr, str(int(round(anio))), 0, 0, 130, TINTA)
        cr.restore()
        cr.restore()
    kq = M.ease_out_back((t - t2 - 0.55) / 0.4)
    cheque_grande(cr, 622, 566, 0.9 * kq, p, t - t2 - 0.55)
    cr.restore()
    banda(cr)
    titulo(cr, p, t)


def esc_juicio(cr, t, p):
    """Contra la segunda empresa: Kearns habla ante el juez; del otro lado, la mesa de la demandada."""
    tg = p.get("t_gano", 3.12)
    cr.save()
    camara(cr, t, 0.04)
    dec_tribunal(cr, t)
    # juez en el estrado
    persona(cr, "juez_k", 560, "escuchar" if t < tg else "señalar", t, -1, 0.86, y=1090)
    estrado(cr, 424, 700, 860)
    rr(cr, 440, 836, 80, 26, 8, (0.40, 0.25, 0.14))
    # mesa de la demandada
    gano = t >= tg
    for i, (x, est, pose_a, pose_b) in enumerate(((794, "abog1", "escuchar", "triste"),
                                                  (884, "abog2", "nervioso", "tapar_cara"),
                                                  (970, "abog3", "escuchar", "triste"))):
        persona(cr, est, x, pose_b if gano else pose_a, t + i * 0.7, -1, 0.82)
    rect(cr, 730, 1046, 350, 24, (0.52, 0.33, 0.20))
    rect(cr, 750, 1070, 330, PISO - 1070, (0.30, 0.18, 0.12))
    rr(cr, 757, 1096, 250, 64, 10, (0.97, 0.97, 0.95))
    M.texto(cr, p.get("mesa", "CHRYSLER"), 882, 1128, 40, TINTA)
    # Kearns, solo de su lado
    if gano:
        persona(cr, "kearns_mayor", 196, "k_festejo", t - tg, 1, 1.0)
    else:
        persona(cr, "kearns_mayor", 196, "k_alegato", t, 1, 1.0, "papeles")
        tb = p.get("t_globo", 1.0)
        if tb <= t < tg - 0.15:
            M.globo(cr, p.get("globo", "SU SEÑORÍA…"), 236, 640, t - tb)
    cr.restore()
    banda(cr)
    sello(cr, p.get("sello", "GANÓ"), 300, 572, t - tg, M.VERDE, tam=86, ang=-0.10)
    titulo(cr, p, t)


def esc_condena(cr, t, p):
    """La sentencia: mazazo del juez y la cifra que sube."""
    tg = p.get("t_mazo", 0.62)
    tc = p.get("t_cifra", 1.05)
    cuenta = p.get("cuenta", 1.45)
    tf = p.get("t_festejo", 2.55)
    cr.save()
    camara(cr, t, 0.04)
    dec_tribunal(cr, t)
    festeja = t >= tf
    if festeja:
        lluvia_billetes(cr, t, 18, 41, y0=700, desde=tf)
    persona(cr, "juez_k", 800, "k_mazo", t - tg, -1, 0.95, "mazo", y=1200)
    estrado(cr, 500, 1100, 990, emblema=False)
    balanza(cr, 800, 1120, 0.7, (0.93, 0.72, 0.54))
    rr(cr, 530, 962, 110, 30, 9, (0.40, 0.25, 0.14))
    if 0 <= t - tg < 0.5:
        d = t - tg
        for i in range(7):
            ang = math.pi + i * math.pi / 6
            r0, r1 = 50 + 60 * d, 90 + 150 * d
            linea(cr, [(585 + math.cos(ang) * r0, 962 + math.sin(ang) * r0 * 0.6),
                       (585 + math.cos(ang) * r1, 962 + math.sin(ang) * r1 * 0.6)], 9, (1, 1, 1), clamp(1 - d * 2))
    persona(cr, "kearns_mayor", 192, "k_festejo" if festeja else ("nervioso" if t < tg else "sorpresa"), t, 1, 1.05)
    cr.restore()
    banda(cr)
    # cifra
    k = M.ease_out_back((t - tc) / 0.35)
    if k > 0.01:
        v = p.get("monto", 18.7) * M.ease_in_out((t - tc) / cuenta)
        s = "$" + f"{v:.1f}".replace(".", ",")
        pulso = 1 + 0.08 * math.sin(clamp((t - tc - cuenta) / 0.3) * math.pi)
        cr.save()
        cr.translate(566, 548)
        cr.scale(k * pulso, k * pulso)
        M.texto(cr, s, 5, 6, 176, (0.04, 0.02, 0.06), alfa=0.55)
        M.texto(cr, s, 0, 0, 176, M.VERDE)
        cr.restore()
        M.texto(cr, p.get("unidad", "MILLONES"), 566, 660, 60, M.BLANCO, alfa=clamp((t - tc - 0.2) / 0.3))
    titulo(cr, p, t)


# ------------------------------------------------------------------ registro

def registrar(m, pj):
    global M, PJ
    M, PJ = m, pj
    _instalar_pelo()
    _estilos()
    _poses()
    _objetos()
    m.ESCENAS.update({
        "k_gancho": esc_gancho, "k_aula": esc_aula, "k_boda": esc_boda, "k_ojo": esc_ojo,
        "k_taller": esc_taller, "k_ford": esc_ford, "k_autos": esc_autos, "k_patente": esc_patente,
        "k_pleito": esc_pleito, "k_juicio": esc_juicio, "k_condena": esc_condena,
    })

    # También quedan disponibles para escenas «historia» comunes:
    def ic_parabrisas_k(cr, t, **kw):
        u, edad = barrido(t, ciclo(kw.get("periodo", 2.0), 0.3))
        cr.save()
        cr.translate(0, 120)
        parabrisas(cr, u, edad)
        cr.restore()
    m.ICONOS["parabrisas_k"] = ic_parabrisas_k
    pj.DECORADOS_EXTRA["tribunal_k"] = lambda cr, t, w, h, di: dec_tribunal(cr, t)
    pj.DECORADOS_EXTRA["taller_k"] = lambda cr, t, w, h, di: dec_taller(cr, t)
    pj.DECORADOS_EXTRA["noche_k"] = lambda cr, t, w, h, di: dec_noche(cr, t)
