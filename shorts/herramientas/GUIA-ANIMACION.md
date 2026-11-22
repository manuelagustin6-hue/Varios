# Guía del motor de Shorts animados

Referencia para armar un Short «historia animada» (1080×1920, 30 cuadros por segundo) con `motion.py`.
Todo se describe en un archivo JSON; el arte propio de un video va en un archivo de extensión, sin tocar los archivos compartidos.

## Comandos

```bash
cd shorts
# Vista previa rápida (segundos): hoja con cuadros sueltos y el subtítulo aproximado de cada momento
python3 herramientas/previsualizar.py <carpeta> <archivo.json> <salida.png> [t1 t2 ...]
# Video completo (unos 2 minutos por cada 40 s de video)
python3 herramientas/motion.py <carpeta> <archivo.json>
```

Sin tiempos, la vista previa toma tres cuadros por escena (comienzo, mitad y final) e informa el segundo en que empieza cada escena.

## Estructura del JSON

```json
{
  "audio": "../../audios/011/voz-final.mp3",
  "palabras": "palabras.json",
  "extension": "ext.py",
  "v2": true,
  "paleta": "roja",
  "bucle": true,
  "salida": "video-historia.mp4",
  "reemplazos": {"diez millones": "10 millones"},
  "sonidos": [["golpe", "frase donde suena", 0.0]],
  "escenas": [ ... ]
}
```

- Las rutas son relativas a la carpeta que se pasa por línea de comandos.
- `palabras`: transcripción con tiempos por palabra (formato de ElevenLabs). Por defecto, `palabras.json`.
- `v2`: tipografía Montserrat, cámara, viñeta, barrido entre escenas y efectos de sonido. Usar siempre.
- `paleta: "roja"`: fondo vino, cartel rojo con letras blancas y resaltado durazno. Usar siempre. **Regla del canal: nunca combinar azul con amarillo.**
- `bucle`: corta el video justo después de la última palabra, para que empalme con el comienzo.
- `reemplazos`: une palabras de la voz en un solo texto de subtítulo («diez millones» → «10 millones»). La clave debe coincidir con palabras consecutivas de la transcripción.
- `sonidos`: efectos puntuales `[nombre, frase, desfase]`. Nombres: `whoosh`, `pop`, `golpe`, `caja`. Además, el motor pone solo un `whoosh` en cada cambio de escena, `golpe` en los sellos, `caja` en las cifras y `pop` en los globos.
- `y_sub`: altura del subtítulo (por defecto 1350).

### Escenas

La primera escena empieza en 0. Cada una de las demás lleva `"desde": "frase"`: empieza cuando la voz dice esa frase (palabras consecutivas de la transcripción, sin importar mayúsculas, tildes ni puntuación; se busca a partir de la escena anterior). Dentro de una escena, los tiempos (`poses`, `entra`, `globo`, movimientos) son segundos **desde el comienzo de la escena**.

| Tipo | Campos |
|---|---|
| `historia` | `titulo` (admite `\n`), `decorado`, `personajes`, `elementos`, `rejas` |
| `cifra` | `titulo`, `de`, `a`, `prefijo`, `sufijo`, `unidad`, `icono`, `color`, `cuenta` (segundos que tarda en contar), `args` |
| `icono` | `titulo`, `icono`, `pie`, `color_pie`, `args` |
| `iconos` | `titulo`, `icono`, `cantidad`, `columnas`, `escala` |
| `sello` | `texto` (sello rojo inclinado que cae de golpe), `base` (otra escena completa que queda debajo), `desfase` |
| `barras` | `titulo`, `prefijo`, `sufijo`, `barras`: `[[etiqueta corta, valor, color]]` |
| `grafico` | `titulo`, `valores`, `dibujo` (segundos), `color`, `pie` |
| `linea_tiempo` | `titulo`, `anios`: `[[año, etiqueta, color]]` |
| `versus` | `titulo`, `izq` y `der`: `{icono, texto, color, args}` |
| `transformar` | `titulo`, `de`, `a` (texto que se transforma letra por letra), `espera`, `pie` |

### Tiempos atados a la voz

En cualquier campo de tiempo se puede escribir, en lugar de un número, `{"en": "frase", "mas": 0.2}`: vale los segundos desde el comienzo de la escena hasta que la voz dice esa frase (más un desfase opcional). Ejemplos: `"poses": [[{"en": "y ganó"}, "celebrar"]]`, `"entra": {"en": "un corcho"}`. La frase se busca a partir del comienzo de la escena; si no está, el motor avisa y se detiene (en la escena final del bucle hay que usar números).

### Más campos de `historia`

- `titulos`: `[[segundo, texto], ...]` cambia el cartel dentro de la escena.
- `placas`: `[{texto, x, y, tam, entra, sale}]` carteles claros con texto oscuro, detrás de los personajes. Para nombres de marcas y lugares (nunca logotipos).
- `textos`: `[{t, x, y, tam, color, entra, sale}]` textos sueltos sobre la escena.
- `sellos`: `[{texto, entra, sale, x, y, tam, color}]` sellos inclinados que caen de golpe (con sonido).
- En `elementos`: `entra` y `sale` (aparece con rebote) y `sin_tarjeta` (sin la tarjeta de fondo).

Personaje (dentro de `historia`):

```json
{"estilo": "profesor", "x": 330, "pose": "hablar", "mira": 1, "escala": 0.95,
 "poses": [[2.0, "sorpresa"]], "entra": 0.5, "sale": 6.0,
 "objeto": "papel", "globo": ["¡Esa idea es mía!", 0.3, 4.5]}
```

- `x`: número fijo o `[desde, hasta, t_inicio, t_fin]` para que se desplace (con `pose: "caminar"`).
- `mira`: 1 mira a la derecha, −1 a la izquierda. Los pies se apoyan en el piso (y = 1240).
- Elemento: `{"icono": "auto", "x": 790, "y": 700, "escala": 0.5, "args": {}}` (con `v2` lleva una tarjeta de fondo).

### Catálogo

- **Decorados:** aula, calle, calle_noche, calle_paris, cancha, carcel, cuarto, discoteca, garaje, hotel, juzgado, oficina, oficina_noche, tienda_muebles.
- **Estilos de personaje:** canillita, comerciante, comerciante2, compradora, coronel, ejecutivo, ejecutivo2, estudiante, joven1, joven2, juez, jugador, knight, lustig, mujer, poisson, policia, productor, profesor, programador, wayne.
- **Poses:** parado, caminar, correr, hablar, señalar, dar, celebrar, sorpresa, triste, tapar_cara, pensar, nervioso, escuchar, sonreir.
- **Objetos en la mano:** maletin, billetes, lata, tarjeta, pelota, papel.
- **Íconos:** anillo, auto, avion, caja (registradora), candado, caramelos, carcel, carrito, casa, cereal, cine, claqueta, contrato, corazon, diario, dinero, duda, dvd, estafador, laberinto, lata, lista, luna, maletin, mazo, navegador, pantalla, parabrisas, pelota, personas, pincel, pregunta, regla, reloj, risa, sirena, sobre, tacho, tarjeta, tienda, torre, torta, zapatilla.

## Zonas de la pantalla

- **0–200:** marca de agua del canal. No poner nada importante.
- **200–420:** cartel del título (lo dibuja `titular`, centrado en y = 300).
- **420–1240:** escena. El piso de los personajes está en y = 1240.
- **1240–1500:** franja oscura del subtítulo (centrado en y = 1350). No poner elementos.
- **1500–1920:** zona tapada por la interfaz de TikTok y YouTube. Vacía.
- Margen lateral: nada importante a menos de 60 px de los bordes; a la derecha, la columna de botones tapa desde x ≈ 940 por debajo de y ≈ 900.

## Extensión: arte propio de un video

`"extension": "ext.py"` carga un archivo con una función `registrar(m, pj)`: `m` es el módulo `motion` y `pj` es `personajes`.

```python
import math

def registrar(m, pj):
    # Estilo de personaje (ver ESTILOS en personajes.py para las claves: ropa, pantalon, pelo, peinado,
    # piel, bigote, barba, anteojos, corbata, sombrero, falda, cuello, cordones…)
    pj.ESTILOS["kearns"] = dict(pj.ESTILOS["profesor"], ropa=(0.45, 0.33, 0.25))

    # Ícono: se dibuja centrado en (0, 0), con un tamaño base de unos 400 px
    def ic_patente(cr, t, **kw):
        cr.new_path()
        m.rrect(cr, -150, -190, 300, 380, 16)
        m.rellenar(cr, (0.96, 0.94, 0.88))
        m.texto(cr, "PATENTE", 0, -120, 44, m.OSCURO)
    m.ICONOS["patente"] = ic_patente

    # Decorado: dibuja el fondo entre y = 0 y y = 1240; el piso y la franja del subtítulo los agrega el motor
    def dec_lluvia(cr, t, W, H, dibujar_icono):
        cr.rectangle(0, 0, W, pj.PISO)
        m.rellenar(cr, (0.20, 0.22, 0.30))
    pj.DECORADOS_EXTRA["ruta_lluvia"] = dec_lluvia

    # Objeto en la mano (x, y = posición de la mano) y pose nueva (campos que cambian respecto de «parado»)
    pj.OBJETOS_EXTRA["plano"] = lambda cr, x, y: (cr.rectangle(x - 30, y - 60, 60, 80), m.rellenar(cr, (1, 1, 1)))
    pj.POSES_EXTRA["brazos_cruzados"] = lambda t: {"brazoD": (40, 120), "brazoT": (-40, -120)}

    # Tipo de escena nuevo: f(cr, t, p), con t en segundos desde el comienzo de la escena y p = dict del JSON
    def esc_mia(cr, t, p):
        m.titular(cr, p.get("titulo", ""), t)
    m.ESCENAS["mia"] = esc_mia
```

Ayudas de `motion`: `texto(cr, s, x, y, tam, color, alinear="centro", alfa=1)`, `ancho_texto`, `rellenar(cr, color, alfa=1)`, `rrect(cr, x, y, w, h, r)`, `titular(cr, s, t)`, `dibujar_icono(cr, nombre, t, x, y, escala)`, `globo`, `clamp`, `ease_out_back`, `ease_out_cubic`, `ease_in_out`, constantes `W`, `H` y colores `BLANCO`, `GRIS`, `VERDE`, `ROJO`, `DORADO` (resaltado), `OSCURO`, `FONDO1`.

Cuidados al dibujar con cairo:

- Leer los colores en el momento de dibujar (`m.DORADO`, no una copia hecha al importar): la paleta se aplica antes de cargar la extensión, pero puede cambiar.
- Llamar a `cr.new_path()` antes de cada figura nueva; si no, quedan líneas sueltas entre figuras.
- No escalar a cero (`cr.scale(0, 0)` rompe el dibujo): omitir la figura mientras la escala sea ≤ 0,001.
- La tipografía (Montserrat) no tiene flechas ni símbolos como →, ≈, ↑: escribirlos con palabras.
- Todo debe animarse en función de `t`: nada de azar sin semilla fija (`random.Random(7)`).
