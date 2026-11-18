"""Personajes animados y escenarios para contar historias (se usa desde motion.py).

Cada personaje es un muñeco articulado dibujado con código: cabeza, cara con expresiones,
torso, brazos y piernas de dos segmentos. Las poses definen los ángulos de cada articulación
y se animan con el tiempo (caminar, correr, hablar, sorprenderse, etc.).
"""
import math
import random

import cairo

# ---------- estilos de personaje ----------

PIEL = (0.96, 0.8, 0.68)
ESTILOS = {
    "lustig":     {"ropa": (0.28, 0.3, 0.38), "pantalon": (0.2, 0.21, 0.27), "pelo": (0.18, 0.12, 0.08),
                   "peinado": "corto", "bigote": True, "sombrero": "fedora", "corbata": (0.85, 0.15, 0.18)},
    "poisson":    {"ropa": (0.5, 0.35, 0.22), "pantalon": (0.35, 0.25, 0.16), "pelo": (0.7, 0.7, 0.72),
                   "peinado": "calvo", "bigote": True, "anteojos": True, "corbata": (0.2, 0.4, 0.3)},
    "comerciante": {"ropa": (0.2, 0.42, 0.32), "pantalon": (0.15, 0.25, 0.2), "pelo": (0.45, 0.28, 0.15),
                    "peinado": "corto", "corbata": (0.9, 0.75, 0.2)},
    "comerciante2": {"ropa": (0.22, 0.32, 0.6), "pantalon": (0.16, 0.2, 0.35), "pelo": (0.9, 0.78, 0.45),
                     "peinado": "corto", "bigote": True},
    "canillita":  {"ropa": (0.5, 0.7, 0.85), "pantalon": (0.35, 0.3, 0.25), "pelo": (0.4, 0.25, 0.12),
                   "peinado": "corto", "sombrero": "gorra"},
    "policia":    {"ropa": (0.14, 0.22, 0.48), "pantalon": (0.1, 0.15, 0.32), "pelo": (0.2, 0.15, 0.1),
                   "peinado": "corto", "sombrero": "policia", "bigote": True},
    "mujer":      {"ropa": (0.85, 0.3, 0.35), "pantalon": (0.85, 0.3, 0.35), "pelo": (0.35, 0.2, 0.1),
                   "peinado": "largo", "falda": True},
}


def _sombra(c, f=0.75):
    return tuple(x * f for x in c)


# ---------- poses ----------
# Ángulos en grados desde "hacia abajo"; positivos = hacia donde mira el personaje.
# brazo = (hombro, codo); pierna = (cadera, rodilla). D = adelante, T = atrás.

def pose(nombre, t):
    p = {"brazoD": (6, 12), "brazoT": (-6, 12), "piernaD": (4, -2), "piernaT": (-4, -2),
         "cabeza": 0, "torso": 0, "salto": 0, "boca": "neutra", "cejas": 0, "rubor": False, "temblor": 0}
    resp = math.sin(t * 2.5) * 2
    p["torso"] = resp * 0.5
    if nombre == "caminar":
        f = t * 7
        s = math.sin(f)
        p.update(piernaD=(28 * s, -25 * max(0, -s)), piernaT=(-28 * s, -25 * max(0, s)),
                 brazoD=(-25 * s, 15), brazoT=(25 * s, 15), salto=abs(math.cos(f)) * 8, boca="sonrisa")
    elif nombre == "correr":
        f = t * 12
        s = math.sin(f)
        p.update(piernaD=(45 * s, -60 * max(0, -s) - 15), piernaT=(-45 * s, -60 * max(0, s) - 15),
                 brazoD=(-50 * s, 80), brazoT=(50 * s, 80), salto=abs(math.cos(f)) * 22, torso=12,
                 boca="o", cejas=1)
    elif nombre == "hablar":
        p.update(brazoD=(55 + 18 * math.sin(t * 5), 55), boca="hablar", cejas=0.3)
    elif nombre == "señalar":
        p.update(brazoD=(95, 0), boca="hablar", cejas=0.3)
    elif nombre == "dar":
        p.update(brazoD=(75, 15), boca="sonrisa")
    elif nombre == "celebrar":
        p.update(brazoD=(165 + 10 * math.sin(t * 8), 10), brazoT=(-165 - 10 * math.sin(t * 8), -10),
                 salto=abs(math.sin(t * 6)) * 25, boca="sonrisa", cejas=0.5)
    elif nombre == "sorpresa":
        p.update(brazoD=(140, 70), brazoT=(-140, -70), boca="o", cejas=1, cabeza=-4)
    elif nombre == "triste":
        p.update(brazoD=(2, 4), brazoT=(-2, 4), cabeza=14, torso=8, boca="triste", cejas=-1)
    elif nombre == "tapar_cara":
        p.update(brazoD=(150, 115), brazoT=(-150, -115), cabeza=14, torso=6, boca="triste", cejas=-1,
                 rubor=True, temblor=math.sin(t * 20) * 2)
    elif nombre == "pensar":
        p.update(brazoD=(35, 140), cabeza=-6, boca="neutra", cejas=0.6)
    elif nombre == "nervioso":
        p.update(brazoD=(20, 40), brazoT=(-20, 40), boca="triste", cejas=1, temblor=math.sin(t * 25) * 4)
    elif nombre == "escuchar":
        p.update(brazoD=(10, 30), boca="neutra", cabeza=-3)
    elif nombre == "sonreir":
        p.update(boca="sonrisa")
    return p


# ---------- dibujo del personaje ----------

def _segmento(cr, x1, y1, x2, y2, ancho, color):
    cr.new_path()
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_width(ancho)
    cr.set_source_rgb(*color)
    cr.move_to(x1, y1)
    cr.line_to(x2, y2)
    cr.stroke()


def _miembro(cr, x, y, ang1, ang2, l1, l2, ancho, color, fin=None, fin_r=0):
    a1 = math.radians(ang1)
    ex, ey = x + l1 * math.sin(a1), y + l1 * math.cos(a1)
    a2 = math.radians(ang1 + ang2)
    hx, hy = ex + l2 * math.sin(a2), ey + l2 * math.cos(a2)
    _segmento(cr, x, y, ex, ey, ancho, color)
    _segmento(cr, ex, ey, hx, hy, ancho * 0.92, color)
    if fin:
        cr.new_path()
        cr.arc(hx, hy, fin_r, 0, 2 * math.pi)
        cr.set_source_rgb(*fin)
        cr.fill()
    return hx, hy


def _objeto(cr, nombre, x, y):
    cr.new_path()
    if nombre == "maletin":
        cr.rectangle(x - 45, y, 90, 65)
        cr.set_source_rgb(0.45, 0.28, 0.15)
        cr.fill()
        cr.rectangle(x - 15, y - 14, 30, 16)
        cr.set_line_width(6)
        cr.stroke()
    elif nombre == "billetes":
        for i in range(3):
            cr.save()
            cr.translate(x + 10, y - 10 - i * 8)
            cr.rotate(-0.3 + i * 0.15)
            cr.rectangle(-40, -18, 80, 36)
            cr.set_source_rgb(0.25, 0.65, 0.4)
            cr.fill()
            cr.restore()
    elif nombre == "papel":
        cr.save()
        cr.translate(x + 15, y - 30)
        cr.rotate(0.1)
        cr.rectangle(-35, -45, 70, 90)
        cr.set_source_rgb(0.95, 0.93, 0.86)
        cr.fill()
        for i in range(4):
            cr.rectangle(-25, -30 + i * 18, 50, 6)
            cr.set_source_rgb(0.6, 0.6, 0.62)
            cr.fill()
        cr.restore()


def _cara(cr, est, p, t, hx, hy):
    # ojos (miran hacia adelante) con parpadeo
    parp = (t % 3.3) < 0.12
    for dx in (8, 40):
        cr.new_path()
        if parp:
            cr.rectangle(hx + dx - 8, hy - 8, 16, 4)
        else:
            cr.arc(hx + dx, hy - 8, 8, 0, 2 * math.pi)
        cr.set_source_rgb(0.1, 0.1, 0.12)
        cr.fill()
    # cejas
    c = p["cejas"]
    for dx, s in ((8, 1), (40, -1)):
        cr.new_path()
        cr.move_to(hx + dx - 12, hy - 28 - 6 * c + (s * 4 if c < 0 else 0))
        cr.line_to(hx + dx + 12, hy - 28 - 6 * c - (s * 4 if c < 0 else 0))
        cr.set_line_width(6)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgb(*_sombra(est["pelo"], 0.8))
        cr.stroke()
    if est.get("anteojos"):
        for dx in (8, 40):
            cr.new_path()
            cr.arc(hx + dx, hy - 8, 17, 0, 2 * math.pi)
            cr.set_line_width(5)
            cr.set_source_rgb(0.15, 0.15, 0.18)
            cr.stroke()
    if p["rubor"]:
        for dx in (0, 46):
            cr.new_path()
            cr.arc(hx + dx, hy + 14, 13, 0, 2 * math.pi)
            cr.set_source_rgba(1, 0.35, 0.35, 0.55)
            cr.fill()
    # bigote
    my = hy + 22
    if est.get("bigote"):
        cr.new_path()
        cr.move_to(hx + 4, my - 6)
        cr.curve_to(hx + 15, my - 16, hx + 35, my - 16, hx + 46, my - 6)
        cr.curve_to(hx + 35, my - 4, hx + 15, my - 4, hx + 4, my - 6)
        cr.set_source_rgb(*est["pelo"])
        cr.fill()
    # boca
    b = p["boca"]
    if b == "hablar":
        b = "o" if int(t * 9) % 2 else "neutra"
    cr.new_path()
    cr.set_source_rgb(0.35, 0.1, 0.1)
    cr.set_line_width(5)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    if b == "o":
        cr.arc(hx + 25, my + 6, 10, 0, 2 * math.pi)
        cr.fill()
    elif b == "sonrisa":
        cr.arc(hx + 25, my - 4, 16, 0.2 * math.pi, 0.8 * math.pi)
        cr.stroke()
    elif b == "triste":
        cr.arc(hx + 25, my + 16, 14, 1.2 * math.pi, 1.8 * math.pi)
        cr.stroke()
    else:
        cr.move_to(hx + 14, my + 4)
        cr.line_to(hx + 36, my + 4)
        cr.stroke()


def _peinado_y_sombrero(cr, est, hx, hy, r):
    pelo = est["pelo"]
    cr.new_path()
    if est["peinado"] == "corto":
        cr.arc(hx, hy, r + 2, math.pi * 1.05, math.pi * 1.95)
        cr.close_path()
        cr.set_source_rgb(*pelo)
        cr.fill()
    elif est["peinado"] == "largo":
        cr.arc(hx, hy, r + 6, math.pi * 1.0, math.pi * 1.95)
        cr.close_path()
        cr.set_source_rgb(*pelo)
        cr.fill()
        cr.new_path()
        cr.rectangle(hx - r - 12, hy - 30, 60, 150)
        cr.set_source_rgb(*pelo)
        cr.fill()
    elif est["peinado"] == "calvo":
        for dx in (-r + 6, r - 22):
            cr.new_path()
            cr.arc(hx + dx + 8, hy - 12, 16, 0, 2 * math.pi)
            cr.set_source_rgb(*pelo)
            cr.fill()
    s = est.get("sombrero")
    cr.new_path()
    if s == "fedora":
        cr.rectangle(hx - r - 22, hy - r + 4, 2 * r + 44, 16)
        cr.set_source_rgb(0.5, 0.38, 0.25)
        cr.fill()
        cr.new_path()
        cr.rectangle(hx - r + 8, hy - r - 48, 2 * r - 16, 56)
        cr.fill()
        cr.new_path()
        cr.rectangle(hx - r + 8, hy - r - 6, 2 * r - 16, 10)
        cr.set_source_rgb(1, 0.82, 0.29)
        cr.fill()
    elif s == "gorra":
        cr.arc(hx, hy - 8, r + 4, math.pi, 2 * math.pi)
        cr.set_source_rgb(0.8, 0.72, 0.55)
        cr.fill()
        cr.new_path()
        cr.rectangle(hx, hy - 16, r + 34, 12)
        cr.fill()
    elif s == "policia":
        cr.rectangle(hx - r - 4, hy - r - 36, 2 * r + 8, 46)
        cr.set_source_rgb(0.1, 0.14, 0.32)
        cr.fill()
        cr.new_path()
        cr.rectangle(hx - 10, hy - r + 4, r + 40, 12)
        cr.set_source_rgb(0.05, 0.05, 0.08)
        cr.fill()
        cr.new_path()
        cr.arc(hx + 10, hy - r - 14, 10, 0, 2 * math.pi)
        cr.set_source_rgb(1, 0.82, 0.29)
        cr.fill()


def personaje(cr, estilo, x, y, escala, mira, nombre_pose, t, objeto=None):
    """Dibuja un personaje con los pies en (x, y)."""
    est = ESTILOS[estilo]
    p = pose(nombre_pose, t)
    cr.save()
    cr.translate(x + p["temblor"], y - p["salto"] * escala)
    cr.scale(escala * mira, escala)
    ropa, pant = est["ropa"], est["pantalon"]
    cadera = (0, -230)
    hombro_y = -390
    # sombra en el piso
    cr.save()
    cr.scale(1, 0.18)
    cr.new_path()
    cr.arc(0, p["salto"] / 0.18, 90, 0, 2 * math.pi)
    cr.set_source_rgba(0, 0, 0, 0.25)
    cr.fill()
    cr.restore()
    # miembros de atrás
    _miembro(cr, -8, cadera[1], *p["piernaT"], 112, 112, 38, _sombra(pant), fin=(0.12, 0.1, 0.1), fin_r=22)
    cr.save()
    cr.rotate(math.radians(p["torso"]))
    _miembro(cr, -20, hombro_y + 12, *p["brazoT"], 98, 92, 30, _sombra(ropa), fin=_sombra(PIEL, 0.9), fin_r=17)
    cr.restore()
    _miembro(cr, 8, cadera[1], *p["piernaD"], 112, 112, 38, pant, fin=(0.12, 0.1, 0.1), fin_r=22)
    # torso
    cr.save()
    cr.rotate(math.radians(p["torso"]))
    cr.new_path()
    if est.get("falda"):
        cr.move_to(-60, hombro_y)
        cr.line_to(60, hombro_y)
        cr.line_to(95, cadera[1] + 40)
        cr.line_to(-95, cadera[1] + 40)
        cr.close_path()
    else:
        r = 40
        x0, y0, w, h = -68, hombro_y - 12, 136, cadera[1] - hombro_y + 30
        cr.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0)
        cr.line_to(x0 + w, y0 + h)
        cr.line_to(x0, y0 + h)
        cr.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2)
        cr.close_path()
    cr.set_source_rgb(*ropa)
    cr.fill()
    if est.get("corbata"):
        cr.new_path()
        cr.move_to(18, hombro_y - 8)
        cr.line_to(32, hombro_y + 70)
        cr.line_to(18, hombro_y + 90)
        cr.line_to(4, hombro_y + 70)
        cr.close_path()
        cr.set_source_rgb(*est["corbata"])
        cr.fill()
    # cabeza
    cr.save()
    cr.translate(0, hombro_y - 16)
    cr.rotate(math.radians(p["cabeza"]))
    hx, hy, r = 8, -62, 66
    cr.new_path()
    cr.arc(hx, hy, r, 0, 2 * math.pi)
    cr.set_source_rgb(*PIEL)
    cr.fill()
    cr.new_path()
    cr.arc(hx - r + 6, hy + 4, 14, 0, 2 * math.pi)
    cr.set_source_rgb(*_sombra(PIEL, 0.9))
    cr.fill()
    _peinado_y_sombrero(cr, est, hx, hy, r)
    _cara(cr, est, p, t, hx, hy)
    cr.restore()
    # brazo de adelante (y objeto en la mano)
    mano = _miembro(cr, 20, hombro_y + 12, *p["brazoD"], 98, 92, 30, ropa, fin=PIEL, fin_r=17)
    if objeto:
        _objeto(cr, objeto, *mano)
    cr.restore()
    cr.restore()


# ---------- escenarios ----------

PISO = 1240


def _edificios(cr, rnd, color, ventanas, base, alto_min, alto_max, W):
    x = -20
    while x < W:
        w = rnd.uniform(140, 230)
        h = rnd.uniform(alto_min, alto_max)
        cr.new_path()
        cr.rectangle(x, base - h, w, h)
        cr.set_source_rgb(*color)
        cr.fill()
        for yy in range(int(base - h + 40), base - 60, 70):
            for xx in range(int(x + 25), int(x + w - 40), 60):
                if rnd.random() < 0.7:
                    cr.new_path()
                    cr.rectangle(xx, yy, 28, 38)
                    cr.set_source_rgb(*ventanas)
                    cr.fill()
        x += w + rnd.uniform(4, 20)


def _farol(cr, x, prendido=True):
    cr.new_path()
    cr.rectangle(x - 8, PISO - 420, 16, 420)
    cr.set_source_rgb(0.12, 0.12, 0.15)
    cr.fill()
    cr.new_path()
    cr.rectangle(x - 30, PISO - 470, 60, 60)
    cr.fill()
    if prendido:
        cr.new_path()
        cr.rectangle(x - 22, PISO - 462, 44, 44)
        cr.set_source_rgb(1, 0.85, 0.45)
        cr.fill()
        g = cairo.RadialGradient(x, PISO - 440, 10, x, PISO - 440, 220)
        g.add_color_stop_rgba(0, 1, 0.85, 0.45, 0.35)
        g.add_color_stop_rgba(1, 1, 0.85, 0.45, 0)
        cr.new_path()
        cr.arc(x, PISO - 440, 220, 0, 2 * math.pi)
        cr.set_source(g)
        cr.fill()


def decorado(cr, nombre, t, W, H, dibujar_icono):
    rnd = random.Random(nombre)
    cr.new_path()
    if nombre in ("calle_paris", "calle", "calle_noche"):
        noche = nombre == "calle_noche"
        g = cairo.LinearGradient(0, 0, 0, PISO)
        if noche:
            g.add_color_stop_rgb(0, 0.04, 0.06, 0.15)
            g.add_color_stop_rgb(1, 0.12, 0.15, 0.3)
        else:
            g.add_color_stop_rgb(0, 0.28, 0.2, 0.45)
            g.add_color_stop_rgb(0.7, 0.95, 0.55, 0.4)
            g.add_color_stop_rgb(1, 1, 0.75, 0.5)
        cr.rectangle(0, 0, W, PISO)
        cr.set_source(g)
        cr.fill()
        if noche:
            cr.new_path()
            cr.arc(820, 520, 70, 0, 2 * math.pi)
            cr.set_source_rgb(0.97, 0.95, 0.85)
            cr.fill()
        elif nombre == "calle_paris":
            dibujar_icono(cr, "torre", t, 160, PISO - 330, 0.8)
        _edificios(cr, rnd, (0.1, 0.1, 0.18) if noche else (0.35, 0.25, 0.4),
                   (1, 0.85, 0.45) if noche else (0.55, 0.42, 0.55), PISO, 220, 420, W)
        _farol(cr, 900, prendido=True)
    elif nombre == "hotel":
        cr.rectangle(0, 0, W, PISO)
        cr.set_source_rgb(0.45, 0.12, 0.16)
        cr.fill()
        for x in range(0, W, 120):
            cr.new_path()
            cr.rectangle(x + 50, 0, 20, PISO)
            cr.set_source_rgb(0.5, 0.15, 0.2)
            cr.fill()
        cr.new_path()
        cr.rectangle(0, PISO - 260, W, 260)
        cr.set_source_rgb(0.38, 0.22, 0.12)
        cr.fill()
        cr.new_path()
        cr.rectangle(0, PISO - 270, W, 14)
        cr.set_source_rgb(0.85, 0.65, 0.3)
        cr.fill()
        # araña de cristal
        cr.new_path()
        cr.rectangle(W / 2 - 4, 0, 8, 470)
        cr.set_source_rgb(0.85, 0.65, 0.3)
        cr.fill()
        for i in range(7):
            ang = math.pi * i / 6
            x = W / 2 + math.cos(ang) * 120
            y = 520 + math.sin(ang) * 30
            cr.new_path()
            cr.arc(x, y, 14, 0, 2 * math.pi)
            cr.set_source_rgb(1, 0.9, 0.6)
            cr.fill()
        g = cairo.RadialGradient(W / 2, 520, 20, W / 2, 520, 420)
        g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.3)
        g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        cr.new_path()
        cr.arc(W / 2, 520, 420, 0, 2 * math.pi)
        cr.set_source(g)
        cr.fill()
    elif nombre == "carcel":
        cr.rectangle(0, 0, W, PISO)
        cr.set_source_rgb(0.32, 0.33, 0.37)
        cr.fill()
        for y in range(0, PISO, 70):
            off = 0 if (y // 70) % 2 else 70
            for x in range(-off, W, 140):
                cr.new_path()
                cr.rectangle(x + 4, y + 4, 132, 62)
                cr.set_source_rgb(0.36, 0.37, 0.41)
                cr.fill()
        cr.new_path()
        cr.rectangle(W / 2 - 110, 560, 220, 150)
        cr.set_source_rgb(0.15, 0.17, 0.25)
        cr.fill()
        for i in range(5):
            cr.new_path()
            cr.rectangle(W / 2 - 100 + i * 50, 560, 10, 150)
            cr.set_source_rgb(0.6, 0.62, 0.66)
            cr.fill()
    # piso (debajo van los subtítulos: oscuro para que se lean)
    cr.new_path()
    cr.rectangle(0, PISO, W, H - PISO)
    cr.set_source_rgb(0.06, 0.07, 0.1)
    cr.fill()
    cr.new_path()
    cr.rectangle(0, PISO, W, 10)
    cr.set_source_rgb(0.2, 0.2, 0.26)
    cr.fill()


def rejas(cr, t, W):
    """Barrotes en primer plano (se dibujan encima de los personajes)."""
    k = min(1.0, t / 0.5)
    for i in range(9):
        x = 60 + i * 120
        cr.new_path()
        cr.rectangle(x - 12, 0, 24, PISO * k)
        cr.set_source_rgb(0.55, 0.57, 0.62)
        cr.fill()
    cr.new_path()
    cr.rectangle(0, 620, W, 26)
    cr.set_source_rgb(0.5, 0.52, 0.57)
    cr.fill()
