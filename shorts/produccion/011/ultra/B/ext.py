"""Arte propio del Short 011 (Robert Kearns) · versión B: gráfica de retención.

Todo lo que este video suma al motor vive acá: estilos de Kearns (joven y mayor), el auto de frente
con limpiaparabrisas que barren y despejan gotas, el ojo que parpadea, placas genéricas para las
marcas, sellos, año rodante, pilas de billetes y los tipos de escena del video.
Se carga con "extension": "ext.py" (ver herramientas/GUIA-ANIMACION.md).
"""
import math
import random

import cairo

M = None    # módulo motion
PJ = None   # módulo personajes

PIEL = (0.96, 0.8, 0.68)
PARPADO = (0.90, 0.71, 0.60)
ROJO_AUTO = (0.80, 0.14, 0.18)
CREMA_AUTO = (0.93, 0.90, 0.84)
NEGRO = (0.06, 0.02, 0.08)
SUBE, BAJA = 0.26, 0.30   # segundos que tarda la escobilla (y el párpado) en ir y en volver


# ---------- utilidades ----------

def lerp(a, b, k):
    return a + (b - a) * k


def mezcla(c1, c2, k):
    return tuple(lerp(a, b, k) for a, b in zip(c1, c2))


def golpe(x):
    """Pulso 0 → 1 → 0 mientras x va de 0 a 1."""
    return math.sin(math.pi * M.clamp(x))


def circ(cr, x, y, r, color, alfa=1.0):
    if r <= 0:
        return
    cr.new_path()
    cr.arc(x, y, r, 0, 2 * math.pi)
    M.rellenar(cr, color, alfa)


def linea(cr, x1, y1, x2, y2, ancho, color, alfa=1.0):
    cr.new_path()
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_width(ancho)
    cr.set_source_rgba(*color, alfa)
    cr.move_to(x1, y1)
    cr.line_to(x2, y2)
    cr.stroke()


def texto_s(cr, s, x, y, tam, color, d=6, alinear="centro", alfa=1.0):
    """Texto con sombra dura (para cifras y rótulos sobre el fondo)."""
    M.texto(cr, s, x + d * 0.5, y + d, tam, (0.03, 0.01, 0.05), alinear, 0.6 * alfa)
    return M.texto(cr, s, x, y, tam, color, alinear, alfa)


def cartel(cr, s, y, t, tam=58, max_w=900, x=None, color=None):
    """Cartel rojo del canal, más chico que el titular y a cualquier altura."""
    if t <= 0 or not s:
        return
    x = M.W / 2 if x is None else x
    while M.ancho_texto(cr, s, tam) > max_w - 60 and tam > 34:
        tam -= 2
    esc = 0.6 + 0.4 * M.ease_out_back(t / 0.3)
    w, h = M.ancho_texto(cr, s, tam) + 60, tam * 1.25 + 30
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, 16)
    M.rellenar(cr, color or M.TITULAR_FONDO or M.DORADO)
    M.texto(cr, s, 0, 0, tam, M.TITULAR_TEXTO or M.OSCURO)
    cr.restore()


def titulos(cr, t, lista):
    """Titular que cambia dentro de la escena: lista de (segundo, texto)."""
    actual = None
    for t0, s in lista:
        if t >= t0:
            actual = (t0, s)
    if actual:
        M.titular(cr, actual[1], t - actual[0])


def anio(cr, s, t, y=282, tam=190, color=None):
    """Año (o palabra) gigante en la zona del título."""
    a = M.ease_out_back(t / 0.35)
    if a <= 0.01:
        return
    while M.ancho_texto(cr, s, tam) > 900:
        tam -= 6
    cr.save()
    cr.translate(M.W / 2, y)
    cr.scale(a, a)
    texto_s(cr, s, 0, 0, tam, color or M.BLANCO, 9)
    cr.restore()


def ancho_placa(cr, s, tam):
    return M.ancho_texto(cr, s, tam) + tam * 0.95


def placa(cr, s, x, y, tam=66, esc=1.0, ang=0.0):
    """Placa blanca genérica con el nombre de la empresa en letras de molde (no es un logotipo)."""
    if esc <= 0.01:
        return 0
    w, h = ancho_placa(cr, s, tam), tam * 1.55
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -w / 2 + 6, -h / 2 + 9, w, h, 14)
    M.rellenar(cr, (0, 0, 0), 0.35)
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, 14)
    M.rellenar(cr, (0.98, 0.97, 0.94))
    cr.new_path()
    M.rrect(cr, -w / 2 + 8, -h / 2 + 8, w - 16, h - 16, 8)
    cr.set_line_width(max(3, tam * 0.07))
    cr.set_source_rgb(*M.OSCURO)
    cr.stroke()
    M.texto(cr, s, 0, 1, tam, M.OSCURO)
    cr.restore()
    return w


def sello(cr, s, x, y, t, color, tam=110, ang=-0.15, relleno=(0.99, 0.97, 0.94)):
    """Sello que cae de golpe, con fondo propio para leerse sobre cualquier escena."""
    if t <= 0:
        return
    a = M.clamp(t / 0.18)
    esc = 2.2 - 1.2 * M.ease_out_cubic(a)
    w, h = M.ancho_texto(cr, s, tam) + tam * 0.8, tam * 1.7
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -w / 2 + 8, -h / 2 + 12, w, h, 20)
    M.rellenar(cr, (0, 0, 0), 0.35 * a)
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, 20)
    M.rellenar(cr, relleno, 0.96 * a)
    cr.new_path()
    M.rrect(cr, -w / 2 + 10, -h / 2 + 10, w - 20, h - 20, 12)
    cr.set_line_width(tam * 0.11)
    cr.set_source_rgba(*color, a)
    cr.stroke()
    M.texto(cr, s, 0, 2, tam, color, alfa=a)
    cr.restore()


def flecha(cr, x1, y1, x2, y2, k, color, ancho=18):
    if k <= 0.03:
        return
    ex, ey = lerp(x1, x2, k), lerp(y1, y2, k)
    largo = math.hypot(ex - x1, ey - y1)
    cab = ancho * 1.5
    cr.save()
    cr.translate(x1, y1)
    cr.rotate(math.atan2(y2 - y1, x2 - x1))
    cr.new_path()
    cr.rectangle(0, -ancho / 2, max(0.0, largo - cab), ancho)
    M.rellenar(cr, color)
    cr.new_path()
    cr.move_to(largo, 0)
    cr.line_to(largo - cab * 1.15, -cab)
    cr.line_to(largo - cab * 1.15, cab)
    cr.close_path()
    M.rellenar(cr, color)
    cr.restore()


def estrella(cr, x, y, r, n, color, rot=0.0, interior=0.5, alfa=1.0):
    cr.new_path()
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * interior
        an = rot + i * math.pi / n
        px, py = x + rr * math.cos(an), y + rr * math.sin(an)
        if i:
            cr.line_to(px, py)
        else:
            cr.move_to(px, py)
    cr.close_path()
    M.rellenar(cr, color, alfa)


def piso(cr):
    """Franja oscura del subtítulo, igual a la de los decorados."""
    cr.new_path()
    cr.rectangle(0, PJ.PISO, M.W, M.H - PJ.PISO)
    M.rellenar(cr, (0.06, 0.07, 0.1))
    cr.new_path()
    cr.rectangle(0, PJ.PISO, M.W, 10)
    M.rellenar(cr, (0.2, 0.2, 0.26))


def camara(cr, t):
    """Acercamiento lento, como el de las escenas «historia» del motor."""
    z = 1 + min(0.06, 0.012 * t)
    cr.translate(M.W / 2 + math.sin(t * 0.4) * 6, PJ.PISO)
    cr.scale(z, z)
    cr.translate(-M.W / 2, -PJ.PISO)


def lluvia(cr, t, x0, y0, x1, y1, n, alfa):
    rnd = random.Random(21)
    alto = y1 - y0
    for _ in range(n):
        x, yb = rnd.uniform(x0, x1), rnd.uniform(0, 1)
        v, largo = rnd.uniform(560, 860), rnd.uniform(26, 50)
        y = y0 + ((yb + t * v / alto) % 1.0) * alto
        borde = min(1.0, (y - y0) / 70, (y1 - y) / 70)
        if borde <= 0:
            continue
        linea(cr, x, y, x - largo * 0.22, y + largo, 4, (0.85, 0.88, 0.95), alfa * borde)


# ---------- ritmo compartido: escobilla y párpado ----------

def ultimos(t, spec):
    """Los dos últimos disparos anteriores a t. spec = lista de segundos, o (primero, período)."""
    if isinstance(spec, tuple):
        t0, per = spec
        k = math.floor((t - t0) / per)
        return [t0 + (k - 1) * per, t0 + k * per]
    return [x for x in spec if x <= t][-2:]


def barrido(t, spec):
    """Posición de la escobilla: 0 en reposo, 1 arriba."""
    ts = ultimos(t, spec)
    if not ts:
        return 0.0
    tau = t - ts[-1]
    if tau < SUBE:
        return tau / SUBE
    if tau < SUBE + BAJA:
        return 1 - M.ease_in_out((tau - SUBE) / BAJA)
    return 0.0


def apertura(t, spec):
    """Apertura del ojo con el mismo ciclo que la escobilla: 1 abierto, 0 cerrado."""
    return 1 - barrido(t, spec)


def desde_paso(t, spec, fa):
    """Segundos desde que la escobilla pasó (subiendo) por la fracción fa del arco."""
    for t0 in reversed(ultimos(t, spec)):
        if t >= t0 + SUBE * fa:
            return t - (t0 + SUBE * fa)
    return None


def ritmo(t, lista):
    """(fracción de la pausa transcurrida, destello del disparo) para el anillo de ritmo."""
    antes = [x for x in lista if x <= t]
    despues = [x for x in lista if x > t]
    per = lista[1] - lista[0] if len(lista) > 1 else 1.0
    a = antes[-1] if antes else lista[0] - per
    b = despues[0] if despues else a + per
    return M.clamp((t - a) / (b - a)), (1 - M.clamp((t - a) / 0.3)) if antes else 0.0


def anillo(cr, x, y, r, frac, destello=0.0, simbolo=None):
    circ(cr, x, y, r * 1.3, NEGRO, 0.92)
    cr.new_path()
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_line_width(r * 0.3)
    cr.set_source_rgba(1, 1, 1, 0.2)
    cr.stroke()
    if frac > 0.01:
        cr.new_path()
        cr.arc(x, y, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * M.clamp(frac))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_width(r * 0.3)
        cr.set_source_rgb(*M.DORADO)
        cr.stroke()
    if destello > 0.01:
        cr.new_path()
        cr.arc(x, y, r * (1.35 + 0.7 * (1 - destello)), 0, 2 * math.pi)
        cr.set_line_width(r * 0.16)
        cr.set_source_rgba(1, 1, 1, 0.8 * destello)
        cr.stroke()
    if simbolo:
        M.texto(cr, simbolo, x, y, r * 1.05, M.BLANCO)


# ---------- parabrisas, auto y ojo ----------

def parabrisas(cr, t, spec, bw=238, tw=186, h=190, largo=150, piv=(-112, 66), n=46, semilla=9, marcar=0.0):
    """Vidrio con gotas y dos escobillas que las despejan. Origen: centro del borde inferior.
    `marcar` (0 a 1) dibuja el recorrido de cada escobilla con una flecha, para señalar el invento."""
    def camino():
        cr.new_path()
        cr.move_to(-bw, 0)
        cr.line_to(-tw, -h)
        cr.line_to(tw, -h)
        cr.line_to(bw, 0)
        cr.close_path()

    camino()
    g = cairo.LinearGradient(0, -h, 0, 0)
    g.add_color_stop_rgb(0, 0.91, 0.90, 0.94)
    g.add_color_stop_rgb(1, 0.73, 0.71, 0.80)
    cr.set_source(g)
    cr.fill()
    cr.save()
    camino()
    cr.clip()
    for dx in (-0.5, 0.2):
        cr.new_path()
        cr.move_to(bw * dx, 0)
        cr.line_to(bw * dx + h * 0.5, -h)
        cr.line_to(bw * dx + h * 0.5 + h * 0.24, -h)
        cr.line_to(bw * dx + h * 0.24, 0)
        cr.close_path()
        M.rellenar(cr, (1, 1, 1), 0.18)
    py = -h * 0.035
    r_in = largo * 0.26
    a0, a1 = math.radians(5), math.radians(118)
    ang = lerp(a0, a1, barrido(t, spec))
    ts = ultimos(t, spec)
    reciente = (t - ts[-1]) if ts else 99.0
    brillo = 0.42 * (1 - M.clamp((reciente - 0.35) / 0.9)) if ts else 0.0
    if brillo > 0.01:   # la zona recién barrida queda más clara
        tope = ang if reciente < SUBE else a1
        for px in piv:
            cr.new_path()
            cr.arc_negative(px, py, largo, -a0, -tope)
            cr.arc(px, py, r_in, -tope, -a0)
            cr.close_path()
            M.rellenar(cr, (1, 1, 1), brillo)
    rnd = random.Random(semilla)
    for _ in range(n):
        x, y, r = rnd.uniform(-bw, bw), rnd.uniform(-h + 10, -10), rnd.uniform(0.028, 0.052) * h
        if abs(x) > lerp(bw, tw, -y / h) - 10:
            continue
        al = 1.0
        for px in piv:
            dx, dy = x - px, py - y
            rr, an = math.hypot(dx, dy), math.atan2(dy, dx)
            if r_in <= rr <= largo and a0 <= an <= a1:
                s = desde_paso(t, spec, (an - a0) / (a1 - a0))
                if s is not None:
                    al = min(al, M.clamp((s - 0.25) / 1.0))
        if al > 0.03:
            circ(cr, x, y, r, (0.40, 0.38, 0.54), 0.85 * al)
            circ(cr, x - r * 0.3, y - r * 0.3, r * 0.36, (1, 1, 1), 0.85 * al)
    for px in piv:
        ex, ey = px + largo * math.cos(ang), py - largo * math.sin(ang)
        linea(cr, px, py, lerp(px, ex, 0.62), lerp(py, ey, 0.62), largo * 0.05, (0.28, 0.28, 0.33))
        linea(cr, lerp(px, ex, 0.2), lerp(py, ey, 0.2), ex, ey, largo * 0.085, (0.05, 0.05, 0.07))
        circ(cr, px, py, largo * 0.06, (0.2, 0.2, 0.24))
    if marcar > 0.01:
        b0, b1 = math.radians(14), math.radians(110)
        for px in piv:
            cr.new_path()
            cr.arc_negative(px, py, largo * 1.02, -b0, -b1)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_line_width(largo * 0.05)
            cr.set_source_rgba(*(M.TITULAR_FONDO or M.ROJO), marcar)
            cr.stroke()
            qx, qy = px + largo * 1.02 * math.cos(b1), py - largo * 1.02 * math.sin(b1)
            tx, ty, nx, ny = -math.sin(b1), -math.cos(b1), math.cos(b1), -math.sin(b1)
            c = largo * 0.11
            cr.new_path()
            cr.move_to(qx + tx * c * 1.5, qy + ty * c * 1.5)
            cr.line_to(qx + nx * c, qy + ny * c)
            cr.line_to(qx - nx * c, qy - ny * c)
            cr.close_path()
            M.rellenar(cr, M.TITULAR_FONDO or M.ROJO, marcar)
    cr.restore()
    camino()
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_width(h * 0.045)
    cr.set_source_rgb(0.10, 0.10, 0.14)
    cr.stroke()


def auto_frente(cr, t, x, y, esc, color, spec, marcar=0.0):
    """Auto genérico visto de frente, apoyado en (x, y), con los limpiaparabrisas funcionando."""
    if esc <= 0.01:
        return
    osc = mezcla(color, (0, 0, 0), 0.32)
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    cr.save()
    cr.scale(1, 0.1)
    circ(cr, 0, 0, 330, (0, 0, 0), 0.4)
    cr.restore()
    for sx in (-1, 1):
        cr.new_path()
        M.rrect(cr, sx * 232 - 46, -84, 92, 84, 16)
        M.rellenar(cr, (0.07, 0.07, 0.09))
        cr.new_path()
        M.rrect(cr, sx * 296 - 32, -296, 64, 42, 12)
        M.rellenar(cr, osc)
    cr.new_path()
    cr.move_to(-262, -214)
    cr.line_to(-200, -430)
    cr.line_to(200, -430)
    cr.line_to(262, -214)
    cr.close_path()
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_width(26)
    cr.set_source_rgb(*osc)
    cr.stroke_preserve()
    cr.fill()
    cr.new_path()
    M.rrect(cr, -296, -236, 592, 190, 40)
    M.rellenar(cr, color)
    cr.new_path()
    M.rrect(cr, -296, -118, 592, 72, 30)
    M.rellenar(cr, osc)
    cr.new_path()
    M.rrect(cr, -128, -200, 256, 80, 14)
    M.rellenar(cr, (0.10, 0.10, 0.13))
    for i in range(4):
        cr.new_path()
        cr.rectangle(-112, -188 + i * 18, 224, 6)
        M.rellenar(cr, (0.46, 0.47, 0.53))
    for sx in (-1, 1):
        circ(cr, sx * 216, -160, 39, (0.14, 0.14, 0.17))
        circ(cr, sx * 216, -160, 30, (1.0, 0.94, 0.84))
        circ(cr, sx * 216, -160, 62, (1.0, 0.94, 0.84), 0.16 + 0.05 * math.sin(t * 5))
    cr.new_path()
    M.rrect(cr, -308, -98, 616, 46, 20)
    M.rellenar(cr, (0.80, 0.81, 0.85))
    cr.new_path()
    M.rrect(cr, -64, -95, 128, 40, 6)
    M.rellenar(cr, (0.97, 0.97, 0.95))
    cr.translate(0, -226)
    parabrisas(cr, t, spec, marcar=marcar)
    cr.restore()


def ojo(cr, x, y, a, b, ap, iris=(0.36, 0.24, 0.13)):
    """Ojo almendrado centrado en (x, y): a y b son los semiejes; ap = 1 abierto, 0 cerrado."""
    ap = M.clamp(ap)
    top, bot = -b * 1.33, b * 1.12
    cy = lerp(bot, top, ap)

    def almendra():
        cr.new_path()
        cr.move_to(-a, 0)
        cr.curve_to(-a * 0.5, top, a * 0.5, top, a, 0)
        cr.curve_to(a * 0.5, bot, -a * 0.5, bot, -a, 0)
        cr.close_path()

    cr.save()
    cr.translate(x, y)
    almendra()
    M.rellenar(cr, (0.99, 0.98, 0.96))
    cr.save()
    almendra()
    cr.clip()
    ri, iy = b * 0.8, -b * 0.06
    circ(cr, 0, iy, ri, mezcla(iris, (0, 0, 0), 0.4))
    circ(cr, 0, iy, ri * 0.88, iris)
    circ(cr, 0, iy, ri * 0.62, mezcla(iris, (1, 0.7, 0.4), 0.25))
    circ(cr, 0, iy, ri * 0.44, (0.04, 0.03, 0.03))
    circ(cr, -ri * 0.34, iy - ri * 0.36, ri * 0.2, (1, 1, 1), 0.95)
    circ(cr, ri * 0.3, iy + ri * 0.3, ri * 0.09, (1, 1, 1), 0.7)
    cr.new_path()   # párpado superior: baja desde arriba hasta la curva actual
    cr.move_to(-a - 30, 0)
    cr.line_to(-a - 30, top - 80)
    cr.line_to(a + 30, top - 80)
    cr.line_to(a + 30, 0)
    cr.line_to(a, 0)
    cr.curve_to(a * 0.5, cy, -a * 0.5, cy, -a, 0)
    cr.close_path()
    M.rellenar(cr, PARPADO)
    cr.restore()
    cr.new_path()
    cr.move_to(-a, 0)
    cr.curve_to(-a * 0.5, bot, a * 0.5, bot, a, 0)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_width(b * 0.05)
    cr.set_source_rgba(0.5, 0.28, 0.22, 0.8)
    cr.stroke()
    cr.new_path()
    cr.move_to(-a, 0)
    cr.curve_to(-a * 0.5, cy, a * 0.5, cy, a, 0)
    cr.set_line_width(b * 0.12)
    cr.set_source_rgb(0.16, 0.09, 0.07)
    cr.stroke()
    sentido = lerp(-1.0, 1.0, M.clamp((ap - 0.12) / 0.4))   # pestañas: hacia arriba abierto, hacia abajo cerrado
    for i in range(8):
        u = 0.1 + i * 0.114
        v = 1 - u
        px = v ** 3 * -a + 3 * v * v * u * (-a * 0.5) + 3 * v * u * u * (a * 0.5) + u ** 3 * a
        py = 3 * v * v * u * cy + 3 * v * u * u * cy
        tx = 3 * v * v * (a * 0.5) + 6 * v * u * a + 3 * u * u * (a * 0.5)
        ty = 3 * v * v * cy - 3 * u * u * cy
        nrm = math.hypot(tx, ty) or 1.0
        nx, ny = ty / nrm + (u - 0.5) * 0.9, -tx / nrm
        largo = b * 0.26
        linea(cr, px, py, px + nx * largo * sentido, py + ny * largo * sentido, b * 0.07, (0.16, 0.09, 0.07))
    cr.restore()


def cara_ojo(cr, x, y, w, h, a, b, ap, ceja=0.0):
    """Primer plano de un ojo sobre una tarjeta de piel, con ceja."""
    cr.new_path()
    M.rrect(cr, x - w / 2, y - h / 2, w, h, 46)
    g = cairo.LinearGradient(0, y - h / 2, 0, y + h / 2)
    g.add_color_stop_rgb(0, 0.99, 0.84, 0.72)
    g.add_color_stop_rgb(1, 0.92, 0.74, 0.62)
    cr.set_source(g)
    cr.fill()
    oy = y + h * 0.11
    by = oy - b * 1.62 + ceja
    cr.new_path()
    cr.move_to(x - a * 0.95, by + b * 0.3)
    cr.curve_to(x - a * 0.4, by - b * 0.34, x + a * 0.4, by - b * 0.3, x + a * 0.92, by + b * 0.14)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_width(b * 0.27)
    cr.set_source_rgb(0.2, 0.13, 0.08)
    cr.stroke()
    ojo(cr, x, oy, a, b, ap)


# ---------- piezas chicas ----------

def billete(cr, x, y, esc=1.0, ang=0.0, alfa=1.0):
    if esc <= 0.01 or alfa <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -48, -24, 96, 48, 7)
    M.rellenar(cr, (0.14, 0.50, 0.29), alfa)
    cr.new_path()
    M.rrect(cr, -40, -17, 80, 34, 5)
    cr.set_line_width(3)
    cr.set_source_rgba(0.62, 0.92, 0.68, alfa)
    cr.stroke()
    M.texto(cr, "$", 0, 0, 30, (0.80, 0.98, 0.84), alfa=alfa)
    cr.restore()


def pila(cr, x, y, esc=1.0, niveles=3):
    """Pila de billetes: en los contadores, una pila = un millón."""
    if esc <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    for i in range(niveles):
        yy = -i * 13
        cr.new_path()
        M.rrect(cr, -33, yy - 14, 66, 30, 5)
        M.rellenar(cr, (0.08, 0.30, 0.17))
        cr.new_path()
        M.rrect(cr, -33, yy - 18, 66, 30, 5)
        M.rellenar(cr, (0.17, 0.58, 0.33))
        cr.new_path()
        M.rrect(cr, -27, yy - 13, 54, 20, 3)
        cr.set_line_width(2.5)
        cr.set_source_rgb(0.62, 0.92, 0.68)
        cr.stroke()
    M.texto(cr, "$", 0, -(niveles - 1) * 13 - 3, 19, (0.82, 0.98, 0.86))
    cr.restore()


def engranaje(cr, x, y, r, rot, color, hueco=None):
    cr.save()
    cr.translate(x, y)
    cr.rotate(rot)
    for i in range(8):
        cr.save()
        cr.rotate(i * math.pi / 4)
        cr.new_path()
        M.rrect(cr, -r * 0.2, -r, r * 0.4, r * 0.5, r * 0.06)
        M.rellenar(cr, color)
        cr.restore()
    circ(cr, 0, 0, r * 0.76, color)
    cr.restore()
    if hueco is not None:
        circ(cr, x, y, r * 0.32, hueco)


def pin(cr, x, y, r, color, hueco):
    cr.new_path()
    cr.move_to(x - r * 0.92, y - r * 0.2)
    cr.line_to(x, y + r * 1.5)
    cr.line_to(x + r * 0.92, y - r * 0.2)
    cr.close_path()
    M.rellenar(cr, color)
    circ(cr, x, y - r * 0.5, r, color)
    circ(cr, x, y - r * 0.5, r * 0.4, hueco)


def pastilla(cr, x, y, s, tam, esc, color=None, icono=None, t=0.0):
    """Renglón de dato: píldora oscura con ícono y texto."""
    if esc <= 0.01:
        return
    wt = M.ancho_texto(cr, s, tam)
    ic = tam * 1.25 if icono else 0
    w, h = wt + ic + tam * 1.2, tam * 1.7
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, h / 2)
    M.rellenar(cr, NEGRO, 0.9)
    cr.new_path()
    M.rrect(cr, -w / 2, -h / 2, w, h, h / 2)
    cr.set_line_width(4)
    cr.set_source_rgba(*M.DORADO, 0.55)
    cr.stroke()
    xi = -w / 2 + tam * 0.5 + ic * 0.36
    if icono == "engranaje":
        engranaje(cr, xi, 0, tam * 0.52, t * 1.2, M.DORADO, hueco=NEGRO)
    elif icono == "pin":
        pin(cr, xi, -tam * 0.12, tam * 0.3, M.ROJO, NEGRO)
    M.texto(cr, s, -w / 2 + tam * 0.6 + ic + wt / 2, 2, tam, color or M.BLANCO)
    cr.restore()


def busto(cr, estilo, cx, cy, r, t, pose="sonreir", mira=1, fondo=None, aro=None, detras=None):
    """Retrato circular de un personaje (cabeza y hombros)."""
    if r <= 3:
        return
    circ(cr, cx, cy, r, fondo or (0.2, 0.08, 0.22))
    cr.save()
    cr.new_path()
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.clip()
    if detras:
        detras(cr)
        cr.new_path()
    s = r / 118.0
    PJ.personaje(cr, estilo, cx - 8 * s * mira, cy - r * 0.08 + 468 * s, s, mira, pose, t)
    cr.restore()
    cr.new_path()
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.set_line_width(max(5, r * 0.07))
    cr.set_source_rgb(*(aro or M.BLANCO))
    cr.stroke()


def anio_rodante(cr, y, tam, valor):
    """Año con el último dígito que rueda como un cuentakilómetros (valor = 1963.0 … 1969.0)."""
    cr.select_font_face(M.FUENTE, cairo.FONT_SLANT_NORMAL, M.PESO)
    cr.set_font_size(tam)
    paso = max(cr.text_extents(d).x_advance for d in "0123456789")
    x0 = M.W / 2 - paso * 1.5
    base = int(math.floor(valor))
    frac = M.ease_in_out(valor - base)
    fijos = str(base)[:3]
    for i, d in enumerate(fijos):
        texto_s(cr, d, x0 + i * paso, y, tam, M.BLANCO, 9)
    x = x0 + 3 * paso
    alto = tam * 0.92
    cr.save()
    cr.new_path()
    cr.rectangle(x - paso * 0.6, y - tam * 0.41, paso * 1.3, tam * 0.86)
    cr.clip()
    texto_s(cr, str(base % 10), x, y - frac * alto, tam, M.DORADO, 9)
    if frac > 0.001:
        texto_s(cr, str((base + 1) % 10), x, y + (1 - frac) * alto, tam, M.DORADO, 9)
    cr.restore()


def botella(cr, x, y, ang, esc, con_corcho=True):
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    vd = (0.10, 0.34, 0.22)
    cr.new_path()
    M.rrect(cr, -34, -150, 68, 175, 14)
    M.rellenar(cr, vd)
    cr.new_path()
    cr.move_to(-34, -138)
    cr.curve_to(-34, -190, -14, -190, -14, -232)
    cr.line_to(14, -232)
    cr.curve_to(14, -190, 34, -190, 34, -138)
    cr.close_path()
    M.rellenar(cr, vd)
    cr.new_path()
    cr.rectangle(-14, -262, 28, 40)
    M.rellenar(cr, vd)
    cr.new_path()
    M.rrect(cr, -18, -268, 36, 56, 6)
    M.rellenar(cr, (0.96, 0.80, 0.58))
    cr.new_path()
    M.rrect(cr, -28, -108, 56, 72, 6)
    M.rellenar(cr, (0.96, 0.93, 0.85))
    cr.new_path()
    cr.rectangle(-20, -86, 40, 9)
    M.rellenar(cr, (0.78, 0.14, 0.2))
    cr.new_path()
    M.rrect(cr, -27, -140, 9, 150, 4)
    M.rellenar(cr, (1, 1, 1), 0.2)
    if con_corcho:
        corcho(cr, 0, -276, 0, 1.0)
    cr.restore()


def corcho(cr, x, y, ang, esc=1.0):
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -14, -4, 28, 28, 5)
    M.rellenar(cr, (0.74, 0.56, 0.36))
    cr.new_path()
    M.rrect(cr, -20, -24, 40, 26, 11)
    M.rellenar(cr, (0.90, 0.74, 0.52))
    cr.restore()


def copa(cr, x, y):
    """Copa de champán apoyada en (x, y)."""
    cr.new_path()
    cr.rectangle(x - 16, y - 5, 32, 5)
    M.rellenar(cr, (0.92, 0.93, 0.96))
    cr.new_path()
    cr.rectangle(x - 2, y - 42, 4, 40)
    M.rellenar(cr, (0.92, 0.93, 0.96))
    cr.new_path()
    cr.move_to(x - 15, y - 100)
    cr.line_to(x + 15, y - 100)
    cr.line_to(x + 9, y - 44)
    cr.line_to(x - 9, y - 44)
    cr.close_path()
    M.rellenar(cr, (0.92, 0.93, 0.96), 0.55)
    cr.new_path()
    cr.move_to(x - 13, y - 82)
    cr.line_to(x + 13, y - 82)
    cr.line_to(x + 9, y - 46)
    cr.line_to(x - 9, y - 46)
    cr.close_path()
    M.rellenar(cr, (1.0, 0.86, 0.6), 0.9)


def roseta(cr, x, y, r, s, esc):
    """Sello de cinta roja con un texto corto (año de la patente)."""
    if esc <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.scale(esc, esc)
    for sx in (-1, 1):
        cr.new_path()
        cr.move_to(0, 0)
        cr.line_to(sx * r * 0.55, 0)
        cr.line_to(sx * r * 0.8, r * 1.8)
        cr.line_to(sx * r * 0.45, r * 1.5)
        cr.line_to(sx * r * 0.1, r * 1.8)
        cr.close_path()
        M.rellenar(cr, (0.66, 0.07, 0.13))
    estrella(cr, 0, 0, r, 18, (0.86, 0.10, 0.16), interior=0.86)
    cr.new_path()
    cr.arc(0, 0, r * 0.72, 0, 2 * math.pi)
    cr.set_line_width(3)
    cr.set_source_rgba(1, 1, 1, 0.7)
    cr.stroke()
    M.texto(cr, s, 0, 1, r * 0.52, M.BLANCO)
    cr.restore()


def documento_patente(cr, x, y, esc, t, anio_sello="1967"):
    if esc <= 0.01:
        return
    cr.save()
    cr.translate(x, y)
    cr.rotate(-0.04)
    cr.scale(esc, esc)
    cr.new_path()
    M.rrect(cr, -172, -238, 360, 500, 12)
    M.rellenar(cr, (0, 0, 0), 0.35)
    cr.new_path()
    M.rrect(cr, -180, -250, 360, 500, 12)
    M.rellenar(cr, (0.97, 0.95, 0.89))
    cr.new_path()
    M.rrect(cr, -180, -250, 360, 92, 12)
    M.rellenar(cr, M.OSCURO)
    M.texto(cr, "PATENTE", 0, -203, 54, (0.97, 0.95, 0.89))
    cr.save()   # esquema del invento
    cr.translate(0, 10)
    cr.scale(0.6, 0.6)
    parabrisas(cr, t, (0.5, 1.1), n=0)
    cr.restore()
    for i, w in enumerate((300, 300, 190)):
        cr.new_path()
        cr.rectangle(-150, 52 + i * 34, w, 12)
        M.rellenar(cr, (0.72, 0.71, 0.70))
    cr.new_path()
    cr.rectangle(-150, 200, 130, 6)
    M.rellenar(cr, (0.45, 0.45, 0.48))
    k = M.clamp((t - 0.3) / 0.16)
    if k > 0:
        roseta(cr, 92, 176, 62, anio_sello, 2.0 - M.ease_out_cubic(k))
    cr.restore()


# ---------- decorados ----------

def dec_oficina_ford(cr, t, W, H, dibujar_icono):
    """Despacho de un directivo: pared lisa, ventanal con una fábrica al atardecer y placa «FORD»."""
    P = PJ.PISO
    cr.new_path()
    cr.rectangle(0, 0, W, P)
    M.rellenar(cr, (0.37, 0.31, 0.41))
    cr.new_path()
    cr.rectangle(0, P - 150, W, 150)
    M.rellenar(cr, (0.28, 0.22, 0.31))
    cr.new_path()
    cr.rectangle(0, P - 158, W, 10)
    M.rellenar(cr, (0.50, 0.42, 0.52))
    x0, y0, w, h = 385, 520, 310, 330
    g = cairo.LinearGradient(0, y0, 0, y0 + h)
    g.add_color_stop_rgb(0, 0.58, 0.26, 0.36)
    g.add_color_stop_rgb(1, 1.0, 0.72, 0.52)
    cr.new_path()
    cr.rectangle(x0, y0, w, h)
    cr.set_source(g)
    cr.fill()
    cr.save()
    cr.new_path()
    cr.rectangle(x0, y0, w, h)
    cr.clip()
    fab = (0.22, 0.12, 0.22)
    for i, cx in enumerate((x0 + 60, x0 + 130)):   # chimeneas con humo
        cr.new_path()
        cr.rectangle(cx - 14, y0 + 110, 28, 160)
        M.rellenar(cr, fab)
        for j in range(4):
            u = ((t * 0.35 + j / 4 + i * 0.13) % 1.0)
            circ(cr, cx + u * 60, y0 + 100 - u * 110, 14 + u * 22, (0.98, 0.9, 0.86), 0.5 * (1 - u))
    cr.new_path()
    cr.rectangle(x0, y0 + 230, w, 100)
    M.rellenar(cr, fab)
    for i in range(4):   # techo en diente de sierra
        xx = x0 + 150 + i * 44
        cr.new_path()
        cr.move_to(xx, y0 + 230)
        cr.line_to(xx, y0 + 192)
        cr.line_to(xx + 44, y0 + 230)
        cr.close_path()
        M.rellenar(cr, fab)
    cr.restore()
    cr.new_path()
    cr.rectangle(x0, y0, w, h)
    cr.set_line_width(16)
    cr.set_source_rgb(0.93, 0.91, 0.88)
    cr.stroke()
    cr.new_path()
    cr.rectangle(x0 + w / 2 - 5, y0, 10, h)
    M.rellenar(cr, (0.93, 0.91, 0.88))
    placa(cr, "FORD", 850, 610, 62)


def dec_tribunal(cr, t, W, H, dibujar_icono):
    """Sala de audiencias con paneles de madera y el emblema de la balanza."""
    P = PJ.PISO
    cr.new_path()
    cr.rectangle(0, 0, W, P)
    M.rellenar(cr, (0.32, 0.19, 0.16))
    for x in range(0, W, 180):
        cr.new_path()
        M.rrect(cr, x + 16, 470, 148, P - 500, 10)
        M.rellenar(cr, (0.38, 0.23, 0.18))
    cr.new_path()
    cr.rectangle(0, 430, W, 22)
    M.rellenar(cr, (0.24, 0.13, 0.11))
    cx, cy = 560, 545
    circ(cr, cx, cy, 70, (0.22, 0.12, 0.10))
    cr.new_path()
    cr.arc(cx, cy, 70, 0, 2 * math.pi)
    cr.set_line_width(7)
    cr.set_source_rgb(*M.DORADO)
    cr.stroke()
    linea(cr, cx, cy - 40, cx, cy + 36, 7, M.DORADO)
    linea(cr, cx - 40, cy - 28, cx + 40, cy - 28, 7, M.DORADO)
    linea(cr, cx - 22, cy + 38, cx + 22, cy + 38, 7, M.DORADO)
    for sx in (-1, 1):
        cr.new_path()
        cr.arc(cx + sx * 40, cy - 6, 17, 0, math.pi)
        cr.close_path()
        M.rellenar(cr, M.DORADO)


def estrado(cr):
    """Frente del estrado del juez (se dibuja encima del juez, que queda detrás)."""
    P = PJ.PISO
    cr.new_path()
    cr.rectangle(395, 905, 330, P - 905)
    M.rellenar(cr, (0.47, 0.29, 0.17))
    cr.new_path()
    M.rrect(cr, 425, 940, 270, P - 975, 10)
    M.rellenar(cr, (0.40, 0.24, 0.14))
    cr.new_path()
    M.rrect(cr, 372, 878, 376, 32, 8)
    M.rellenar(cr, (0.27, 0.15, 0.09))
    cr.new_path()
    cr.rectangle(372, 906, 376, 6)
    M.rellenar(cr, M.DORADO)
    cr.new_path()   # mazo apoyado
    M.rrect(cr, 640, 852, 62, 26, 7)
    M.rellenar(cr, (0.62, 0.42, 0.24))
    cr.new_path()
    cr.rectangle(662, 824, 12, 30)
    M.rellenar(cr, (0.62, 0.42, 0.24))


def escritorio(cr, x0, x1, alto=215):
    P = PJ.PISO
    cr.new_path()
    cr.rectangle(x0 + 16, P - alto + 20, x1 - x0 - 32, alto - 20)
    M.rellenar(cr, (0.36, 0.22, 0.14))
    cr.new_path()
    M.rrect(cr, x0, P - alto, x1 - x0, 28, 8)
    M.rellenar(cr, (0.50, 0.32, 0.19))
    cr.new_path()
    M.rrect(cr, x0 + 40, P - alto + 56, x1 - x0 - 80, alto - 90, 8)
    M.rellenar(cr, (0.30, 0.18, 0.11))


# ---------- escenas ----------

def esc_gancho(cr, t, p):
    """Gancho y cierre del bucle: marcas + cifra + el auto con el limpiaparabrisas funcionando.
    En t <= 0 no hay nada entrando: el primer cuadro ya está completo. `desfase` (negativo) hace que
    la última escena termine exactamente en el cuadro 0 de la primera."""
    t += p.get("desfase", 0.0)
    W = M.W
    k = M.ease_in_out((t - 3.86) / 0.5)   # segundo tiempo: acercamiento a «esto»
    spec = (0.35, 1.5)
    piso(cr)
    lluvia(cr, t, 30, 770, W - 30, PJ.PISO - 4, 26, 0.17)
    tam = 66
    wf, wc, sep = ancho_placa(cr, "FORD", tam), ancho_placa(cr, "CHRYSLER", tam), 92
    x0 = (W - (wf + wc + sep)) / 2
    xf, xc = x0 + wf / 2, x0 + wf + sep + wc / 2
    for i in range(8):   # billetes que caen por los costados, de las placas hacia abajo
        u = (t * 0.55 + i / 8) % 1.0
        lado = -1 if i % 2 == 0 else 1
        bx = W / 2 + lado * (418 + 46 * math.sin(i * 2.1)) + math.sin(u * 7 + i) * 22
        billete(cr, bx, lerp(360, 800, u), 0.95, math.sin(u * 6 + i * 1.3) * 0.6, golpe(u) * 0.9 * (1 - k))
    bal = math.sin(t * 1.6) * 0.012
    placa(cr, "FORD", xf, 266, tam, ang=-0.03 + bal)
    M.texto(cr, "Y", x0 + wf + sep / 2, 266, 58, M.BLANCO)
    placa(cr, "CHRYSLER", xc, 266, tam, ang=0.025 - bal)
    s = 1 - 0.42 * k
    pulso = 1 + 0.015 * math.sin(t * 3.2) + 0.13 * golpe((t - 2.42) / 0.4)
    cr.save()
    cr.translate(W / 2, 566 - 40 * k)
    cr.scale(s, s)
    cartel(cr, p.get("cartel", "LE PAGARON UNOS"), -176, 9, tam=50, x=0)
    cr.save()
    cr.scale(pulso, pulso)
    texto_s(cr, p.get("cifra", "$30"), 0, 14, 300, M.VERDE, 11)
    cr.restore()
    texto_s(cr, "MILLONES", 0, 194, 104, M.BLANCO, 7)
    cr.restore()
    esc_auto = 0.92 + 0.38 * k
    e = M.ease_out_back((t - 4.0) / 0.35)
    auto_frente(cr, t, W / 2, PJ.PISO - 2, esc_auto, ROJO_AUTO, spec,
                marcar=M.clamp(e) * (0.75 + 0.25 * math.sin(t * 9)))
    if e > 0.01:
        y_et = 1158
        cr.new_path()
        cr.move_to(W / 2 - 34 * e, y_et - 40)
        cr.line_to(W / 2, y_et - 40 - 46 * e)
        cr.line_to(W / 2 + 34 * e, y_et - 40)
        cr.close_path()
        M.rellenar(cr, M.TITULAR_FONDO or M.DORADO)
        cartel(cr, p.get("etiqueta", "AL INVENTOR DE ESTO"), y_et, t - 4.0, tam=56, max_w=860)


def esc_ficha(cr, t, p):
    """Ficha de presentación: retrato + dos renglones de datos."""
    W = M.W
    M.titular(cr, p.get("titulo", "ROBERT KEARNS"), t)
    a = M.ease_out_back(t / 0.4)
    cx, cy, r = W / 2, 672, 228 * a

    def pizarra(c):
        c.push_group()
        engranaje(c, cx - 128, cy - 78, 64, t * 0.8, (1, 1, 1), hueco=(0.13, 0.30, 0.23))
        engranaje(c, cx - 48, cy - 150, 34, -t * 1.5 + 0.3, (1, 1, 1), hueco=(0.13, 0.30, 0.23))
        M.texto(c, "F = m · a", cx + 108, cy - 128, 34, (1, 1, 1))
        linea(c, cx + 50, cy - 86, cx + 170, cy - 86, 5, (1, 1, 1))
        c.pop_group_to_source()
        c.paint_with_alpha(0.42)

    busto(cr, p.get("estilo", "kearns"), cx, cy, r, t, "sonreir", fondo=(0.13, 0.30, 0.23), detras=pizarra)
    pastilla(cr, W / 2, 972, p.get("dato1", "PROFESOR DE INGENIERÍA"), 48,
             M.ease_out_back((t - 0.78) / 0.35), icono="engranaje", t=t)
    pastilla(cr, W / 2, 1116, p.get("dato2", "DETROIT"), 92,
             M.ease_out_back((t - 1.72) / 0.35), color=M.DORADO, icono="pin")


def esc_corcho(cr, t, p):
    """Noche de bodas: el corcho sale de la botella y le pega en el ojo."""
    W, P = M.W, PJ.PISO
    T0, T1 = p.get("sale", 2.26), p.get("pega", 3.22)
    kx, esc_k = 290, 0.95
    ex, ey = kx + 50 * esc_k, P - 476 * esc_k      # el ojo de Kearns
    mx = 810
    cr.save()
    camara(cr, t)
    PJ.decorado(cr, "hotel", t, W, M.H, M.dibujar_icono)
    cr.new_path()   # mesa
    cr.rectangle(mx - 16, P - 230, 32, 230)
    M.rellenar(cr, (0.26, 0.15, 0.09))
    cr.new_path()
    M.rrect(cr, mx - 90, P - 18, 180, 18, 6)
    M.rellenar(cr, (0.26, 0.15, 0.09))
    cr.new_path()
    M.rrect(cr, mx - 170, P - 252, 340, 26, 8)
    M.rellenar(cr, (0.95, 0.93, 0.9))
    copa(cr, mx - 128, P - 252)
    copa(cr, mx + 132, P - 252)
    bx, by, bang, besc = mx + 6, P - 322, -0.62, 0.86
    botella(cr, bx, by, bang, besc, con_corcho=t < T0)
    cr.new_path()   # hielera, delante de la botella
    cr.move_to(mx - 74, P - 392)
    cr.line_to(mx + 86, P - 392)
    cr.line_to(mx + 64, P - 252)
    cr.line_to(mx - 52, P - 252)
    cr.close_path()
    M.rellenar(cr, (0.74, 0.76, 0.82))
    cr.new_path()
    M.rrect(cr, mx - 82, P - 404, 176, 22, 10)
    M.rellenar(cr, (0.88, 0.89, 0.93))
    cr.new_path()
    M.rrect(cr, mx - 40, P - 370, 14, 100, 6)
    M.rellenar(cr, (1, 1, 1), 0.3)
    # boca de la botella en pantalla
    qx = bx + 276 * besc * math.sin(-bang) * -1
    qy = by - 276 * besc * math.cos(bang)
    if t < T0:
        pose = "sonreir"
    elif t < T1:
        pose = "sorpresa"
    else:
        pose = "tapar_ojo"
    PJ.personaje(cr, "kearns", kx, P, esc_k, 1, pose, t)
    if T0 <= t < T0 + 0.7:   # espuma y «¡POP!»
        u = (t - T0) / 0.7
        rnd = random.Random(4)
        for _ in range(14):
            an = math.pi + bang + rnd.uniform(-0.6, 0.6) + math.pi / 2
            d = rnd.uniform(40, 190) * M.ease_out_cubic(u)
            circ(cr, qx - d * math.sin(-bang) * 0.0 + d * math.cos(an), qy + d * math.sin(an) + 120 * u * u,
                 rnd.uniform(5, 13), (1, 1, 1), 0.9 * (1 - u))
        a = M.ease_out_back(u / 0.3)
        if a > 0.01:
            cr.save()
            cr.translate(qx + 96, qy - 122)
            cr.rotate(0.12)
            cr.scale(a, a)
            estrella(cr, 0, 0, 104, 11, M.BLANCO, rot=0.2, interior=0.72, alfa=1 - M.clamp((u - 0.8) / 0.2))
            M.texto(cr, "¡POP!", 0, 2, 50, M.TITULAR_FONDO or M.ROJO, alfa=1 - M.clamp((u - 0.8) / 0.2))
            cr.restore()
    if T0 <= t < T1:   # vuelo del corcho
        u = (t - T0) / (T1 - T0)
        for j in range(1, 7):
            uj = u - j * 0.045
            if uj > 0:
                circ(cr, lerp(qx, ex, uj), lerp(qy, ey, uj) - 150 * 4 * uj * (1 - uj), 9 - j, (1, 1, 1), 0.5 - j * 0.07)
        cx, cy = lerp(qx, ex, u), lerp(qy, ey, u) - 150 * 4 * u * (1 - u)
        circ(cr, cx, cy, 44, M.DORADO, 0.3)
        corcho(cr, cx, cy, -1.2 - u * 9, 1.7)
    elif t >= T1:
        u = t - T1
        if u < 0.9:   # rebota y cae
            corcho(cr, ex + 150 * u, ey - 260 * u + 720 * u * u, u * 12, 1.7)
        if u < 0.45:
            a = M.ease_out_back(u / 0.15)
            estrella(cr, ex, ey, 96 * a, 9, M.BLANCO, rot=u * 2, interior=0.45, alfa=1 - M.clamp((u - 0.25) / 0.2))
            estrella(cr, ex, ey, 58 * a, 9, M.TITULAR_FONDO or M.ROJO, rot=u * 2 + 0.2, interior=0.45,
                     alfa=1 - M.clamp((u - 0.25) / 0.2))
    cr.restore()
    if T1 <= t < T1 + 0.12:
        cr.new_path()
        cr.rectangle(0, 0, W, M.H)
        M.rellenar(cr, (1, 1, 1), 0.35 * (1 - (t - T1) / 0.12))
    M.titular(cr, p.get("titulo", "NOCHE DE BODAS, 1953"), t)
    pastilla(cr, W / 2, 432, p.get("fuente", "SEGÚN CONTABA ÉL"), 36, M.ease_out_back((t - 0.25) / 0.3))
    if t >= T1 + 0.1:
        M.globo(cr, p.get("globo", "¡AY!"), kx + 40, P - 640 * esc_k, t - T1 - 0.1)


def esc_ojo(cr, t, p):
    """Primer plano de un ojo que parpadea, con un anillo que marca la pausa entre parpadeos."""
    W = M.W
    T = p.get("parpadeos", [0.62, 1.96, 3.12])
    titulos(cr, t, [(0.0, p.get("titulo", "AÑOS DESPUÉS, NOTÓ ALGO")), (1.5, p.get("titulo2", "TU OJO PARPADEA"))])
    a = M.ease_out_back(t / 0.4)
    if a > 0.01:
        cr.save()
        cr.translate(W / 2, 735)
        cr.scale(a, a)
        cr.translate(-W / 2, -735)
        cara_ojo(cr, W / 2, 735, 860, 540, 320, 158, apertura(t, T), -18 * golpe((t - 0.85) / 0.6))
        cr.restore()
    e = M.ease_out_back((t - 0.9) / 0.3) * (1 - M.clamp((t - 1.5) / 0.2))
    if e > 0.01:
        circ(cr, 930, 500, 62 * e, M.TITULAR_FONDO or M.ROJO)
        cr.save()
        cr.translate(930, 500)
        cr.scale(e, e)
        M.texto(cr, "!", 0, 0, 84, M.BLANCO)
        cr.restore()
    e2 = M.ease_out_back((t - p.get("pie_en", 2.4)) / 0.35)
    if e2 > 0.01:
        frac, fl = ritmo(t, T + [T[-1] + 1.2])
        cr.save()
        cr.translate(W / 2, 1124)
        cr.scale(e2, e2)
        cr.new_path()
        M.rrect(cr, -410, -64, 820, 128, 64)
        M.rellenar(cr, NEGRO, 0.9)
        anillo(cr, -338, 0, 36, frac, fl)
        M.texto(cr, p.get("pie", "CADA POCOS SEGUNDOS"), 62, 2, 46, M.BLANCO)
        cr.restore()


def esc_paralelo(cr, t, p):
    """La idea: el ojo (arriba) y el limpiaparabrisas (abajo) se mueven con el mismo ciclo."""
    W = M.W
    T = p.get("ciclos", [0.5, 1.42, 2.34])
    M.titular(cr, p.get("titulo", "UN LIMPIAPARABRISAS\nQUE PARPADEA"), t)
    a = M.ease_out_back(t / 0.4)
    if a > 0.01:
        cr.save()
        cr.translate(W / 2, 610)
        cr.scale(a, a)
        cr.translate(-W / 2, -610)
        cara_ojo(cr, W / 2, 610, 760, 320, 236, 104, apertura(t, T))
        cr.restore()
    b = M.ease_out_back((t - 0.12) / 0.4)
    if b > 0.01:
        cr.save()
        cr.translate(W / 2, 1010)
        cr.scale(b, b)
        cr.translate(-W / 2, -1010)
        cr.new_path()
        M.rrect(cr, 96, 1140, 888, 84, 30)
        M.rellenar(cr, ROJO_AUTO)
        cr.new_path()
        M.rrect(cr, 96, 1186, 888, 38, 20)
        M.rellenar(cr, mezcla(ROJO_AUTO, (0, 0, 0), 0.32))
        cr.new_path()
        M.rrect(cr, 130, 1128, 820, 30, 12)
        M.rellenar(cr, (0.10, 0.10, 0.14))
        cr.translate(W / 2, 1140)
        parabrisas(cr, t, T, bw=385, tw=300, h=285, largo=250, piv=(-185, 105), n=96, semilla=5)
        cr.restore()
    c = M.ease_out_back((t - 0.25) / 0.35)
    if c > 0.01:
        frac, fl = ritmo(t, T + [T[-1] + (T[1] - T[0])])
        cr.save()
        cr.translate(W / 2, 806)
        cr.scale(c, c)
        anillo(cr, 0, 0, 50, frac, fl, "=")
        cr.restore()


def esc_reunion(cr, t, p):
    """1963: Kearns le muestra el invento a Ford; cae el sello «SIN ACUERDO»."""
    W, P = M.W, PJ.PISO
    TS = p.get("sello_en", 1.28)
    cr.save()
    camara(cr, t)
    PJ.decorado(cr, "oficina_ford", t, W, M.H, M.dibujar_icono)
    PJ.personaje(cr, "ejecutivo_ford", 850, P, 0.95, -1, "rechazo" if t > TS - 0.15 else "escuchar", t)
    escritorio(cr, 660, 1040)
    if t < TS + 0.25:
        PJ.personaje(cr, "kearns", 262, P, 0.95, 1, "dar", t, "invento")
    else:
        PJ.personaje(cr, "kearns", 262, P, 0.95, 1, "triste", t, "invento")
    cr.restore()
    anio(cr, p.get("anio", "1963"), t)
    cartel(cr, p.get("cartel", "SE LO MOSTRÓ A FORD"), 438, t - 0.1)
    sello(cr, p.get("sello", "SIN ACUERDO"), W / 2, 1052, t - TS, M.TITULAR_FONDO or M.ROJO, 92, -0.07)


def ruta(cr, yh):
    """Suelo y ruta en perspectiva, del horizonte (yh) al piso."""
    W, P = M.W, PJ.PISO
    cr.new_path()
    cr.rectangle(0, yh, W, P - yh)
    M.rellenar(cr, (0.12, 0.06, 0.14))
    cr.new_path()
    cr.move_to(W / 2 - 46, yh)
    cr.line_to(W / 2 + 46, yh)
    cr.line_to(W / 2 + 520, P)
    cr.line_to(W / 2 - 520, P)
    cr.close_path()
    M.rellenar(cr, (0.19, 0.17, 0.23))
    for i in range(7):
        u0, u1 = (i / 7) ** 2.2, ((i + 0.55) / 7) ** 2.2
        a0, a1 = 4 + 30 * u0, 4 + 30 * u1
        y0, y1 = lerp(yh, P, u0), lerp(yh, P, u1)
        cr.new_path()
        cr.move_to(W / 2 - a0 / 2, y0)
        cr.line_to(W / 2 + a0 / 2, y0)
        cr.line_to(W / 2 + a1 / 2, y1)
        cr.line_to(W / 2 - a1 / 2, y1)
        cr.close_path()
        M.rellenar(cr, (0.80, 0.80, 0.84), 0.55)
    cr.new_path()
    cr.rectangle(0, yh - 3, W, 6)
    M.rellenar(cr, (0.30, 0.16, 0.32))


def esc_lanzamiento(cr, t, p):
    """El año rueda de 1963 a 1969 mientras el auto de Ford se acerca; después llega el de Chrysler."""
    W, P = M.W, PJ.PISO
    T1, T2 = p.get("ford_en", 1.3), p.get("chrysler_en", 2.96)
    yh = 700
    ruta(cr, yh)
    piso(cr)
    lluvia(cr, t, 0, 470, W, P - 4, 44, 0.2)
    k2 = M.ease_in_out((t - T2) / 0.5)
    if t < T2:
        anio_rodante(cr, 282, 190, 1963 + 6 * M.clamp((t - 0.1) / 1.0))
    else:
        anio(cr, p.get("luego", "DESPUÉS"), t - T2, y=286, tam=150)
    if t < T1:
        cartel(cr, p.get("cartel0", "6 AÑOS DESPUÉS"), 438, t)
    elif t < T2:
        cartel(cr, p.get("cartel1", "FORD LANZÓ EL SUYO"), 438, t - T1)
    else:
        cartel(cr, p.get("cartel2", "CHRYSLER TAMBIÉN"), 438, t - T2)
    llega = T1 + 0.25
    q = M.clamp((t - 0.1) / (llega - 0.1)) ** 2.4      # se acerca: despacio lejos, rápido cerca
    freno = 1 + 0.05 * golpe((t - llega) / 0.3)
    sf = lerp(0.98, 0.72, k2) * lerp(0.05, 1.0, q)
    xf = lerp(W / 2, 280, k2)
    auto_frente(cr, t, xf, lerp(yh + 12, P - 2, q), sf * freno, ROJO_AUTO, (llega + 0.45, 1.15))
    placa(cr, "FORD", xf, P - 2 - 436 * lerp(0.98, 0.72, k2) - 66, lerp(66, 54, k2),
          esc=M.ease_out_back((t - llega - 0.05) / 0.3))
    if t > T2:
        llega2 = T2 + 0.7
        q2 = M.clamp((t - T2) / (llega2 - T2)) ** 2.2
        sc = 0.72 * lerp(0.05, 1.0, q2) * (1 + 0.05 * golpe((t - llega2) / 0.3))
        auto_frente(cr, t, lerp(W / 2, 772, q2), lerp(yh + 12, P - 2, q2), sc, CREMA_AUTO, (llega2 + 0.3, 1.15))
        placa(cr, "CHRYSLER", 772, P - 2 - 436 * 0.72 - 66, 54, esc=M.ease_out_back((t - llega2 - 0.05) / 0.3))


def esc_patente(cr, t, p):
    """El documento de la patente y, enseguida, las dos demandas."""
    TD = p.get("demanda_en", 1.0)
    titulos(cr, t, [(0.0, p.get("titulo", "TENÍA LA PATENTE")), (TD, p.get("titulo2", "DEMANDÓ A LAS DOS"))])
    documento_patente(cr, 252, 842, 1.06 * M.ease_out_back(t / 0.4), t, p.get("anio_patente", "1967"))
    filas = p.get("demandas", [["FORD", "1978"], ["CHRYSLER", "1982"]])
    for i, (nombre, an) in enumerate(filas):
        y = 632 + i * 300
        w = ancho_placa(cr, nombre, 64)
        placa(cr, nombre, 742, y, 64, esc=M.ease_out_back((t - 0.25 - i * 0.12) / 0.35))
        td = TD + 0.05 + i * 0.28
        flecha(cr, 456, 742 + i * 190, 742 - w / 2 - 14, y + 6 + i * 26, M.ease_out_cubic((t - td) / 0.2), M.DORADO, 18)
        sello(cr, "DEMANDA " + an, 742, y + 116, t - td - 0.12, M.TITULAR_FONDO or M.ROJO, 46, -0.06)


def esc_doce(cr, t, p):
    """Línea de tiempo de los doce años de juicio, con Kearns que encanece mientras avanza."""
    W = M.W
    M.titular(cr, p.get("titulo", "EN TRIBUNALES"), t)
    a0, a1 = p.get("desde_anio", 1978), p.get("hasta_anio", 1990)
    n = a1 - a0
    prog = M.ease_in_out((t - 0.1) / 1.25)
    tn, ta = 270, 118
    wn, wa = M.ancho_texto(cr, str(n), tn), M.ancho_texto(cr, "AÑOS", ta)
    x0 = W / 2 - (wn + 34 + wa) / 2
    pul = 1 + 0.08 * golpe((t - 1.3) / 0.35)
    cr.save()
    cr.translate(W / 2, 610)
    cr.scale(pul, pul)
    cr.translate(-W / 2, -610)
    texto_s(cr, str(int(n * prog + 0.5)), x0 + wn, 606, tn, M.DORADO, 10, alinear="derecha")
    texto_s(cr, "AÑOS", x0 + wn + 34, 648, ta, M.BLANCO, 7, alinear="izq")
    cr.restore()
    xa, xb, y = 130, 925, 1046
    linea(cr, xa, y, xb, y, 14, M.GRIS, 0.5)
    if prog > 0.005:
        linea(cr, xa, y, lerp(xa, xb, prog), y, 14, M.DORADO)
    for i in range(n + 1):
        hecho = prog >= i / n - 0.01
        circ(cr, lerp(xa, xb, i / n), y, 15 if i in (0, n) else 9, M.DORADO if hecho else M.GRIS)
    M.texto(cr, str(a0), 92, y + 78, 66, M.BLANCO, alinear="izq")
    M.texto(cr, str(a1), 940, y + 78, 66, M.BLANCO if prog > 0.97 else M.GRIS, alinear="derecha")
    est = PJ.ESTILOS["kearns_tmp"]
    est["pelo"] = mezcla(PJ.ESTILOS["kearns"]["pelo"], PJ.ESTILOS["kearns_mayor"]["pelo"], prog)
    xm = lerp(xa, xb, prog)
    bote = abs(math.sin(t * 10)) * 7 if 0.02 < prog < 0.98 else 0
    cr.new_path()
    cr.move_to(xm - 16, y - 44)
    cr.line_to(xm, y - 20)
    cr.line_to(xm + 16, y - 44)
    cr.close_path()
    M.rellenar(cr, M.DORADO)
    busto(cr, "kearns_tmp", xm, y - 138 - bote, 92, t, "sonreir", fondo=(0.24, 0.10, 0.26), aro=M.DORADO)


def esc_pago(cr, t, p):
    """Contador de dinero: cifra que cuenta y pilas de billetes (una pila = un millón)."""
    W = M.W
    monto = p["monto"]
    if p.get("anio"):
        anio(cr, p["anio"], t)
    else:
        placa(cr, p.get("placa", ""), 452, 262, 80, esc=M.ease_out_back(t / 0.35))
        M.dibujar_icono(cr, "mazo", max(0.0, t - 0.12), 912, 258, 0.36)
    cartel(cr, p.get("cartel", ""), 438 if p.get("anio") else 425, t - 0.1)
    T0, dur = p.get("inicio", 0.3), p.get("cuenta", 1.0)
    k = M.ease_out_cubic((t - T0) / dur) if t > T0 else 0.0
    v = monto * k
    tam = 250
    fin = "$" + f"{monto:.1f}".replace(".", ",")
    x0 = W / 2 - M.ancho_texto(cr, fin, tam) / 2
    pul = 1 + 0.07 * golpe((t - T0 - dur + 0.15) / 0.35)
    cr.save()
    cr.translate(W / 2, 660)
    cr.scale(pul, pul)
    cr.translate(-W / 2, -660)
    texto_s(cr, "$" + f"{v:.1f}".replace(".", ","), x0, 660, tam, M.VERDE, 10, alinear="izq")
    cr.restore()
    texto_s(cr, "MILLONES", W / 2, 858, 96, M.BLANCO, 6)
    total = int(math.ceil(monto - 1e-9))
    cols, paso, esc_p = (11, 74, 1.06) if total == 11 else (10, 80, 1.15)
    filas = (total + cols - 1) // cols
    y0 = 1040 if filas == 1 else 1004
    for i in range(total):
        f = M.clamp((v - i) * 1.4)
        if f <= 0:
            continue
        resto = monto - i
        niveles = 3 if resto >= 1 else max(1, int(round(resto * 3)))
        pila(cr, W / 2 + (i % cols - (cols - 1) / 2) * paso, y0 + (i // cols) * 96, esc_p * M.ease_out_back(f), niveles)
    M.texto(cr, p.get("leyenda", "CADA PILA = 1 MILLÓN"), W / 2, y0 + (filas - 1) * 96 + 82, 36, M.GRIS,
            alfa=M.clamp((t - T0) / 0.3))


def esc_tribunal(cr, t, p):
    """Kearns, ya canoso, habla de pie ante el juez; al final cae el sello «GANÓ»."""
    W, P = M.W, PJ.PISO
    TG = p.get("sello_en", 3.12)
    gano = t > TG
    cr.save()
    camara(cr, t)
    PJ.decorado(cr, "tribunal", t, W, M.H, M.dibujar_icono)
    PJ.personaje(cr, "juez", 560, P - 150, 0.85, -1, "escuchar", t)
    estrado(cr)
    PJ.personaje(cr, "abogado_chrysler", 880, P, 0.93, -1, "triste" if t > TG + 0.12 else "escuchar", t, "maletin")
    placa(cr, "CHRYSLER", 862, 672, 42)
    PJ.personaje(cr, "kearns_mayor", 212, P, 0.97, 1, "festejo" if gano else "hablar", t,
                 None if gano else "papel")
    cr.restore()
    titulos(cr, t, [(0.0, p.get("titulo", "CONTRA CHRYSLER")), (1.5, p.get("titulo2", "SU PROPIO ABOGADO"))])
    sello(cr, p.get("sello", "GANÓ"), 556, 1062, t - TG, M.VERDE, 138, -0.09, relleno=(0.04, 0.10, 0.07))


def esc_suma(cr, t, p):
    """Cierre: los dos pagos, la raya y el total."""
    W = M.W
    M.titular(cr, p.get("titulo", "EN TOTAL"), t)
    filas = p.get("filas", [["FORD", "$10,2 M"], ["CHRYSLER", "$18,7 M"]])
    for i, (nombre, monto) in enumerate(filas):
        y = 545 + i * 185
        a = M.ease_out_back((t - i * 0.16) / 0.3)
        if a <= 0.01:
            continue
        w = ancho_placa(cr, nombre, 58)
        placa(cr, nombre, 76 + w / 2, y, 58, esc=a)
        texto_s(cr, monto, 1008, y, 120, M.VERDE, 8, alinear="derecha", alfa=M.clamp(a))
    e = M.ease_out_back((t - 0.3) / 0.3)
    if e > 0.01:
        cr.save()
        cr.translate(498, 640)
        cr.scale(e, e)
        M.texto(cr, "+", 0, 0, 120, M.DORADO)
        cr.restore()
    kl = M.ease_out_cubic((t - 0.5) / 0.25)
    if kl > 0.01:
        linea(cr, 76, 842, lerp(76, 1008, kl), 842, 12, M.BLANCO)
    et = M.clamp((t - 0.72) / 0.16)
    if et > 0:
        yt = 1000
        for i in range(9):
            a = M.ease_out_back((t - 0.86 - i * 0.03) / 0.3)
            billete(cr, 150 + i * 94, 1168 + 12 * math.sin(i * 1.7) + 30 * (1 - M.clamp(a)), 1.05 * a,
                    math.sin(i * 2.3) * 0.3 + 0.04 * math.sin(t * 5 + i), M.clamp(a))
        esc = (2.0 - M.ease_out_cubic(et)) * (1 + 0.05 * golpe((t - 0.9) / 0.4))
        cr.save()
        cr.translate(W / 2, yt)
        cr.scale(esc, esc)
        texto_s(cr, p.get("total", "$28,9 M"), 0, 0, 190, M.VERDE, 11, alfa=et)
        cr.restore()


# ---------- registro ----------

def registrar(m, pj):
    global M, PJ
    M, PJ = m, pj
    # Kearns: saco crema, corbata roja y anteojos; solo cambia el pelo con los años
    kearns = {"ropa": (0.93, 0.89, 0.80), "pantalon": (0.33, 0.26, 0.22), "pelo": (0.17, 0.11, 0.07),
              "peinado": "corto", "anteojos": True, "corbata": (0.80, 0.14, 0.18)}
    pj.ESTILOS["kearns"] = dict(kearns)
    pj.ESTILOS["kearns_mayor"] = dict(kearns, pelo=(0.82, 0.82, 0.85))
    pj.ESTILOS["kearns_tmp"] = dict(kearns)   # lo usa la línea de tiempo para encanecerlo de a poco
    pj.ESTILOS["ejecutivo_ford"] = dict(pj.ESTILOS["ejecutivo"])
    pj.ESTILOS["abogado_chrysler"] = dict(pj.ESTILOS["ejecutivo"], ropa=(0.27, 0.26, 0.30), pantalon=(0.19, 0.18, 0.22),
                                          pelo=(0.25, 0.16, 0.10), corbata=(0.56, 0.57, 0.63), bigote=True)

    pj.POSES_EXTRA["tapar_ojo"] = lambda t: {"brazoD": (150, 118), "cabeza": 12, "torso": 5, "boca": "triste",
                                             "cejas": -1, "temblor": math.sin(t * 22) * 2}
    pj.POSES_EXTRA["rechazo"] = lambda t: {"brazoD": (58, 100), "boca": "neutra", "cejas": -0.5,
                                           "cabeza": 6 * math.sin(t * 12)}

    def obj_invento(cr, x, y):
        """Prototipo en la mano: un vidrio chico con su escobilla y la caja del motor."""
        cr.new_path()
        m.rrect(cr, x - 6, y - 96, 118, 82, 8)
        m.rellenar(cr, (0.86, 0.85, 0.91))
        cr.new_path()
        m.rrect(cr, x - 6, y - 96, 118, 82, 8)
        cr.set_line_width(7)
        cr.set_source_rgb(0.12, 0.12, 0.16)
        cr.stroke()
        linea(cr, x + 20, y - 24, x + 84, y - 78, 8, (0.05, 0.05, 0.07))
        cr.new_path()
        m.rrect(cr, x + 4, y - 20, 50, 30, 6)
        m.rellenar(cr, (0.30, 0.31, 0.37))
        circ(cr, x + 20, y - 24, 7, m.DORADO)
    pj.OBJETOS_EXTRA["invento"] = obj_invento

    # festejo con los brazos en V (el «celebrar» del motor cruza el brazo por delante de la cara)
    pj.POSES_EXTRA["festejo"] = lambda t: {"brazoD": (138 + 8 * math.sin(t * 8), 18),
                                           "brazoT": (-138 - 8 * math.sin(t * 8), -18),
                                           "salto": abs(math.sin(t * 6)) * 22, "boca": "sonrisa", "cejas": 0.5}

    pj.DECORADOS_EXTRA["oficina_ford"] = dec_oficina_ford
    pj.DECORADOS_EXTRA["tribunal"] = dec_tribunal

    # íconos reutilizables (centrados en 0,0; ~400 px)
    def ic_auto_frente(cr, t, color=None, **kw):
        auto_frente(cr, t, 0, 215, 0.95, tuple(color) if color else ROJO_AUTO, (0.4, 1.4))

    def ic_ojo(cr, t, **kw):
        cara_ojo(cr, 0, 0, 520, 330, 190, 96, apertura(t, (0.6, 1.4)))

    def ic_patente(cr, t, **kw):
        documento_patente(cr, 0, 0, 0.9, t, kw.get("anio", "1967"))

    m.ICONOS.update({"auto_frente": ic_auto_frente, "ojo": ic_ojo, "patente": ic_patente})
    m.ESCENAS.update({"gancho": esc_gancho, "ficha": esc_ficha, "corcho": esc_corcho, "ojo": esc_ojo,
                      "paralelo": esc_paralelo, "reunion": esc_reunion, "lanzamiento": esc_lanzamiento,
                      "patente": esc_patente, "doce": esc_doce, "pago": esc_pago, "tribunal": esc_tribunal,
                      "suma": esc_suma})
